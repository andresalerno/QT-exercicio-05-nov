# CustomStack – Qualidade e Testes

Exercício de testes de unidade em Python (pytest / pytest-cov / pytest-mock).

- **Parte 1:** testes de unidade da classe `CustomStack` com cobertura de 100%.
- **Parte 2:** classe `NumberAscOrder`, que ordena de forma ascendente os números da Mega Sena armazenados numa `CustomStack`.

## Instalação

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução dos testes

```sh
# Comando original do projeto (cobertura de linhas, inclui os arquivos de teste)
python -m pytest ./test/* --cov

# Comando recomendado (só código de produção, com cobertura de branches e linhas faltantes)
python -m pytest test/ -v --cov=src --cov-branch --cov-report=term-missing
```

## Fluxo de trabalho (branches)

| # | Branch | Conteúdo |
|---|--------|----------|
| 1 | `fix/push-limite-pilha` | medição inicial, teste que expõe o bug e correção |
| 2 | `test/cobertura-custom-stack` | demais testes da Parte 1 até 100% de cobertura |
| 3 | `feat/number-asc-order` | Parte 2: classe `NumberAscOrder` e seus testes |
| 4 | `refactor/classes-de-teste` | agrupa os testes nas classes `TestCustomStack` e `TestNumberAscOrder` |

---

## Parte 1 – Testes da `CustomStack`

### Branch 1: `fix/push-limite-pilha`

#### Passo 1 – Medição inicial da cobertura

Comando original do projeto:

```sh
python -m pytest ./test/* --cov
```

```text
Name                        Stmts   Miss  Cover
-----------------------------------------------
src/__init__.py                 0      0   100%
src/custom_stack_class.py      24      5    79%
test/__init__.py                0      0   100%
test/custom_stack_test.py       9      0   100%
-----------------------------------------------
TOTAL                          33      5    85%

1 passed
```

Comando com cobertura de branches, medindo apenas `src/`:

```sh
python -m pytest test/ --cov=src --cov-branch --cov-report=term-missing
```

```text
Name                        Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------
src/__init__.py                 0      0      0      0   100%
src/custom_stack_class.py      24      5      6      2    70%   22, 27-29, 33
-----------------------------------------------------------------------
TOTAL                          24      5      6      2    70%

1 passed
```

> A diferença entre 79% e 70% vem de duas coisas: o comando original mede só linhas, e
> o `--cov-branch` também exige que cada `if` seja exercitado nos dois sentidos
> (verdadeiro e falso).

#### Passo 2 – Análise da efetividade do teste existente

O teste original (`test_push_one_elementinstack`) passava, mas era pouco efetivo:

| Problema | Consequência |
|----------|--------------|
| Testa apenas `push` de 1 elemento | `pop`, `top` com a pilha vazia e o limite da pilha nunca são exercitados |
| Variável `value = 0.0` declarada e não usada | ruído no teste |
| `from ... import *` e `== False` | estilo pouco explícito (o idiomático é `is False`) |
| **Passa mesmo com um bug na classe** | não detecta o defeito principal (ver abaixo) |

Analisando as linhas não cobertas, a linha 22 (`raise StackFullException`) era **inalcançável**.
Isso revelou um bug em `push`:

```python
if (self.size == self.limit):   # compara o MÉTODO size com um int -> sempre False
    raise StackFullException
```

Sem os parênteses, `self.size` é o objeto método, e não o tamanho da pilha. A comparação é
sempre `False`, então **a pilha nunca respeita o limite**. Por isso não era possível chegar
a 100% de cobertura apenas escrevendo testes: era preciso corrigir o código.

#### Passo 3 – Teste que expõe o bug (vermelho)

```python
def test_push_on_full_stack_raises_exception():
    stack = CustomStack(5)
    for value in range(5):
        stack.push(value)
    with pytest.raises(StackFullException):
        stack.push(99)
    assert stack.size() == 5
```

```sh
python -m pytest test/ -v
```

```text
test/custom_stack_test.py::test_push_one_elementinstack PASSED                [ 50%]
test/custom_stack_test.py::test_push_on_full_stack_raises_exception FAILED    [100%]

    def test_push_on_full_stack_raises_exception():
        stack = CustomStack(5)
        for value in range(5):
            stack.push(value)
>       with pytest.raises(StackFullException):
E       Failed: DID NOT RAISE <class 'src.custom_stack_class.StackFullException'>

FAILED test/custom_stack_test.py::test_push_on_full_stack_raises_exception
1 failed, 1 passed
```

O teste falha como esperado: o 6º `push` numa pilha de limite 5 foi aceito.

#### Passo 4 – Correção do bug (verde)

`src/custom_stack_class.py`. Nenhum método novo foi criado, apenas a condição foi corrigida:

```diff
     def push(self, element):
-        if (self.size == self.limit):
+        if self.size() == self.limit:
             raise StackFullException
```

```sh
python -m pytest test/ -v --cov=src --cov-branch --cov-report=term-missing
```

```text
test/custom_stack_test.py::test_push_one_elementinstack PASSED                [ 50%]
test/custom_stack_test.py::test_push_on_full_stack_raises_exception PASSED    [100%]

Name                        Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------
src/__init__.py                 0      0      0      0   100%
src/custom_stack_class.py      24      4      6      1    77%   27-29, 33
-----------------------------------------------------------------------
TOTAL                          24      4      6      1    77%

2 passed
```

A linha 22 passou a ser coberta, e a cobertura subiu de 70% para 77%. Ainda não estão
cobertas as linhas 27-29 (`pop`) e 33 (`top` com a pilha vazia), que serão tratadas na branch 2.

### Branch 2: `test/cobertura-custom-stack`

#### Passo 5 – Reescrita da suíte de testes

Melhorias no arquivo `test/custom_stack_test.py`:

- o teste original virou `test_push_one_element_in_stack`, sem a variável não usada, com `is False`
  e com a ordem `real == esperado` nos asserts;
- imports explícitos no lugar do `import *`;
- uma fixture `stack` cria uma `CustomStack(5)` nova para cada teste, que ficam isolados entre si;
- 7 testes novos cobrem o restante do comportamento da classe.

| Teste | O que verifica | Linhas / branches |
|-------|----------------|-------------------|
| `test_new_stack_is_empty` | pilha nova vazia, tamanho 0 e limite configurado | `__init__`, `size`, `is_empty` |
| `test_push_one_element_in_stack` | `push` de um elemento (teste original refatorado) | `push`, `top` |
| `test_push_many_elements_top_is_last_pushed` | `top` retorna o último empilhado | `push`, `top` |
| `test_pop_returns_elements_in_lifo_order` | `pop` segue a ordem LIFO até esvaziar | `pop` (27-29, ramo falso) |
| `test_top_does_not_remove_element` | `top` não remove o elemento | `top` |
| `test_pop_on_empty_stack_raises_exception` | `pop` em pilha vazia lança `StackEmptyException` | linha 28 (ramo verdadeiro) |
| `test_top_on_empty_stack_raises_exception` | `top` em pilha vazia lança `StackEmptyException` | linha 33 (ramo verdadeiro) |
| `test_push_on_full_stack_raises_exception` | `push` em pilha cheia lança `StackFullException` | linha 22 (ramo verdadeiro) |
| `test_push_after_pop_on_full_stack_is_allowed` | depois de um `pop`, a pilha cheia volta a aceitar `push` | `push` (ramo falso no limite) |

#### Passo 6 – Resultado: 100% de cobertura

```sh
python -m pytest test/ -v --cov=src --cov-branch --cov-report=term-missing
```

```text
test/custom_stack_test.py::test_new_stack_is_empty PASSED                     [ 11%]
test/custom_stack_test.py::test_push_one_element_in_stack PASSED              [ 22%]
test/custom_stack_test.py::test_push_many_elements_top_is_last_pushed PASSED  [ 33%]
test/custom_stack_test.py::test_pop_returns_elements_in_lifo_order PASSED     [ 44%]
test/custom_stack_test.py::test_top_does_not_remove_element PASSED            [ 55%]
test/custom_stack_test.py::test_pop_on_empty_stack_raises_exception PASSED    [ 66%]
test/custom_stack_test.py::test_top_on_empty_stack_raises_exception PASSED    [ 77%]
test/custom_stack_test.py::test_push_on_full_stack_raises_exception PASSED    [ 88%]
test/custom_stack_test.py::test_push_after_pop_on_full_stack_is_allowed PASSED [100%]

Name                        Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------
src/__init__.py                 0      0      0      0   100%
src/custom_stack_class.py      24      0      6      0   100%
-----------------------------------------------------------------------
TOTAL                          24      0      6      0   100%

9 passed
```

Comando original do projeto:

```sh
python -m pytest ./test/* --cov
```

```text
Name                        Stmts   Miss  Cover
-----------------------------------------------
src/__init__.py                 0      0   100%
src/custom_stack_class.py      24      0   100%
test/__init__.py                0      0   100%
test/custom_stack_test.py      51      0   100%
-----------------------------------------------
TOTAL                          75      0   100%

9 passed
```

Relatório HTML (gerado em `htmlcov/`, que não é versionado):

```sh
python -m pytest test/ --cov=src --cov-branch --cov-report=html
open htmlcov/index.html
```

#### Resumo da Parte 1

| Etapa | Testes | Cobertura de linhas | Cobertura linhas + branches |
|-------|:------:|:-------------------:|:---------------------------:|
| Inicial | 1 | 79% | 70% |
| Teste do bug (vermelho) | 2 (1 falha) | – | – |
| Bug corrigido (verde) | 2 | – | 77% |
| Suíte completa | 9 | **100%** | **100%** |

---

## Parte 2 – Classe `NumberAscOrder`

### Branch 3: `feat/number-asc-order`

**Objetivo:** coletar os números sorteados da Mega Sena, armazenados numa `CustomStack` na
ordem do sorteio, e devolvê-los numa `list` em ordem ascendente.

#### Decisões de projeto

| Decisão | Justificativa |
|---------|---------------|
| `sort()` usa só `is_empty`, `pop` e `push` | respeita o encapsulamento: não acessa `elements` e não cria métodos novos na `CustomStack` |
| A pilha é restaurada depois da leitura | `sort()` não tem efeito colateral: a pilha continua com os números na ordem do sorteio |
| Pilha vazia retorna `[]` | ordenar uma coleção vazia resulta numa lista vazia (mesma semântica de `sorted([])`) |
| Parâmetro que não é `CustomStack` → `TypeError` | evita erros pouco claros (ex.: `AttributeError`) com entradas inválidas |
| Valor não inteiro (inclusive `bool`) → `TypeError` | números da Mega Sena são inteiros; `bool` é subclasse de `int` em Python e precisa ser barrado explicitamente |
| Número fora de 1–60 → `ValueError` | intervalo válido da Mega Sena |
| Números repetidos → `ValueError` | um sorteio não repete dezenas |

#### Passo 7 – Testes primeiro (vermelho)

Arquivo `test/number_asc_order_test.py`:

| Cenário | Teste(s) |
|---------|----------|
| **Pilha de 6 posições com 6 números sorteados aleatoriamente** | `test_sort_six_random_numbers_returns_ascending_list` (usa `random.sample(range(1, 61), 6)` e compara com `sorted()`) |
| Pilha com 6 números conhecidos (resultado determinístico) | `test_sort_known_numbers_returns_ascending_list` |
| A pilha não é alterada por `sort()` | `test_sort_keeps_stack_in_original_draw_order` |
| **Pilha de 6 posições vazia** | `test_sort_empty_stack_returns_empty_list` |
| Parâmetro inválido (`None`, `list`, `str`, `int`) | `test_sort_invalid_parameter_raises_type_error` (parametrizado, 4 casos) |
| Número fora do intervalo (`0`, `61`, `-5`) | `test_sort_number_out_of_range_raises_value_error` (parametrizado, 3 casos) |
| Valor não inteiro (`7.5`, `"7"`, `True`) | `test_sort_non_integer_value_raises_type_error` (parametrizado, 3 casos) |
| Números repetidos | `test_sort_repeated_numbers_raises_value_error` |
| Uso apenas da interface pública da pilha (**pytest-mock**) | `test_sort_uses_stack_public_interface` (`mocker.Mock(spec=CustomStack)`) |

```sh
python -m pytest test/ -v
```

```text
__________________ ERROR collecting test/number_asc_order_test.py ___________________
ImportError while importing test module '.../custom-stack/test/number_asc_order_test.py'.
test/number_asc_order_test.py:6: in <module>
    from src.number_asc_order import NumberAscOrder
E   ModuleNotFoundError: No module named 'src.number_asc_order'
============================== short test summary info ==============================
ERROR test/number_asc_order_test.py
!!!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!!!!
1 error
```

O teste falha porque a classe ainda não existe.

#### Passo 8 – Implementação (verde)

Arquivo `src/number_asc_order.py`:

```python
from src.custom_stack_class import CustomStack


class NumberAscOrder:
    MIN_NUMBER = 1
    MAX_NUMBER = 60

    def sort(self, stack):
        if not isinstance(stack, CustomStack):
            raise TypeError("O parâmetro deve ser uma instância de CustomStack")

        numbers = []
        while not stack.is_empty():
            numbers.append(stack.pop())

        # Restaura a pilha na ordem original do sorteio (sort não tem efeito colateral)
        for number in reversed(numbers):
            stack.push(number)

        for number in numbers:
            if isinstance(number, bool) or not isinstance(number, int):
                raise TypeError(f"Valor inválido na pilha: {number!r}")
            if not self.MIN_NUMBER <= number <= self.MAX_NUMBER:
                raise ValueError(f"Número fora do intervalo 1-60: {number}")

        if len(set(numbers)) != len(numbers):
            raise ValueError("A pilha contém números repetidos")

        return sorted(numbers)
```

```sh
python -m pytest test/ -v --cov=src --cov-branch --cov-report=term-missing
```

```text
test/custom_stack_test.py::test_new_stack_is_empty PASSED                     [  4%]
test/custom_stack_test.py::test_push_one_element_in_stack PASSED              [  8%]
test/custom_stack_test.py::test_push_many_elements_top_is_last_pushed PASSED  [ 12%]
test/custom_stack_test.py::test_pop_returns_elements_in_lifo_order PASSED     [ 16%]
test/custom_stack_test.py::test_top_does_not_remove_element PASSED            [ 20%]
test/custom_stack_test.py::test_pop_on_empty_stack_raises_exception PASSED    [ 24%]
test/custom_stack_test.py::test_top_on_empty_stack_raises_exception PASSED    [ 28%]
test/custom_stack_test.py::test_push_on_full_stack_raises_exception PASSED    [ 32%]
test/custom_stack_test.py::test_push_after_pop_on_full_stack_is_allowed PASSED [ 36%]
test/number_asc_order_test.py::test_sort_six_random_numbers_returns_ascending_list PASSED [ 40%]
test/number_asc_order_test.py::test_sort_known_numbers_returns_ascending_list PASSED [ 44%]
test/number_asc_order_test.py::test_sort_keeps_stack_in_original_draw_order PASSED [ 48%]
test/number_asc_order_test.py::test_sort_empty_stack_returns_empty_list PASSED [ 52%]
test/number_asc_order_test.py::test_sort_invalid_parameter_raises_type_error[None] PASSED [ 56%]
test/number_asc_order_test.py::test_sort_invalid_parameter_raises_type_error[invalid1] PASSED [ 60%]
test/number_asc_order_test.py::test_sort_invalid_parameter_raises_type_error[123456] PASSED [ 64%]
test/number_asc_order_test.py::test_sort_invalid_parameter_raises_type_error[6] PASSED [ 68%]
test/number_asc_order_test.py::test_sort_number_out_of_range_raises_value_error[0] PASSED [ 72%]
test/number_asc_order_test.py::test_sort_number_out_of_range_raises_value_error[61] PASSED [ 76%]
test/number_asc_order_test.py::test_sort_number_out_of_range_raises_value_error[-5] PASSED [ 80%]
test/number_asc_order_test.py::test_sort_non_integer_value_raises_type_error[7.5] PASSED [ 84%]
test/number_asc_order_test.py::test_sort_non_integer_value_raises_type_error[7] PASSED [ 88%]
test/number_asc_order_test.py::test_sort_non_integer_value_raises_type_error[True] PASSED [ 92%]
test/number_asc_order_test.py::test_sort_repeated_numbers_raises_value_error PASSED [ 96%]
test/number_asc_order_test.py::test_sort_uses_stack_public_interface PASSED   [100%]

Name                        Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------
src/__init__.py                 0      0      0      0   100%
src/custom_stack_class.py      24      0      6      0   100%
src/number_asc_order.py        20      0     14      0   100%
-----------------------------------------------------------------------
TOTAL                          44      0     20      0   100%

25 passed
```

Comando original do projeto:

```sh
python -m pytest ./test/* --cov
```

```text
Name                            Stmts   Miss  Cover
---------------------------------------------------
src/__init__.py                     0      0   100%
src/custom_stack_class.py          24      0   100%
src/number_asc_order.py            20      0   100%
test/__init__.py                    0      0   100%
test/custom_stack_test.py          51      0   100%
test/number_asc_order_test.py      52      0   100%
---------------------------------------------------
TOTAL                             147      0   100%

25 passed
```

### Branch 4: `refactor/classes-de-teste`

#### Passo 9 – Organização dos testes em classes

O enunciado pede **"uma classe de teste com os casos de teste necessários"**. Os testes,
que eram funções soltas no módulo, foram agrupados em classes:

| Arquivo | Classe de teste |
|---------|-----------------|
| `test/custom_stack_test.py` | `TestCustomStack` |
| `test/number_asc_order_test.py` | `TestNumberAscOrder` |

A lógica dos testes não mudou. As alterações foram:

- cada função de teste virou um método da classe, com o parâmetro `self`;
- as fixtures (`stack` e `cut`) foram movidas para dentro das classes;
- o helper `build_stack` continua no nível do módulo, por montar dados e não ser um teste;
- o pytest coleta automaticamente classes com prefixo `Test` (sem `__init__`).

Trecho da estrutura:

```python
class TestNumberAscOrder:

    @pytest.fixture
    def cut(self):
        return NumberAscOrder()

    # Cenário 1: pilha de 6 posições com 6 números sorteados aleatoriamente
    def test_sort_six_random_numbers_returns_ascending_list(self, cut):
        drawn = random.sample(range(1, 61), 6)
        result = cut.sort(build_stack(drawn))
        assert isinstance(result, list)
        assert result == sorted(drawn)

    # Cenário 2: pilha de 6 posições vazia
    def test_sort_empty_stack_returns_empty_list(self, cut):
        stack = CustomStack(STACK_LIMIT)
        assert cut.sort(stack) == []
        assert stack.is_empty() is True
    ...
```

```sh
python -m pytest test/ -v --cov=src --cov-branch --cov-report=term-missing
```

```text
test/custom_stack_test.py::TestCustomStack::test_new_stack_is_empty PASSED [  4%]
test/custom_stack_test.py::TestCustomStack::test_push_one_element_in_stack PASSED [  8%]
test/custom_stack_test.py::TestCustomStack::test_push_many_elements_top_is_last_pushed PASSED [ 12%]
test/custom_stack_test.py::TestCustomStack::test_pop_returns_elements_in_lifo_order PASSED [ 16%]
test/custom_stack_test.py::TestCustomStack::test_top_does_not_remove_element PASSED [ 20%]
test/custom_stack_test.py::TestCustomStack::test_pop_on_empty_stack_raises_exception PASSED [ 24%]
test/custom_stack_test.py::TestCustomStack::test_top_on_empty_stack_raises_exception PASSED [ 28%]
test/custom_stack_test.py::TestCustomStack::test_push_on_full_stack_raises_exception PASSED [ 32%]
test/custom_stack_test.py::TestCustomStack::test_push_after_pop_on_full_stack_is_allowed PASSED [ 36%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_six_random_numbers_returns_ascending_list PASSED [ 40%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_known_numbers_returns_ascending_list PASSED [ 44%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_keeps_stack_in_original_draw_order PASSED [ 48%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_empty_stack_returns_empty_list PASSED [ 52%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_invalid_parameter_raises_type_error[None] PASSED [ 56%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_invalid_parameter_raises_type_error[invalid1] PASSED [ 60%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_invalid_parameter_raises_type_error[123456] PASSED [ 64%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_invalid_parameter_raises_type_error[6] PASSED [ 68%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_number_out_of_range_raises_value_error[0] PASSED [ 72%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_number_out_of_range_raises_value_error[61] PASSED [ 76%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_number_out_of_range_raises_value_error[-5] PASSED [ 80%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_non_integer_value_raises_type_error[7.5] PASSED [ 84%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_non_integer_value_raises_type_error[7] PASSED [ 88%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_non_integer_value_raises_type_error[True] PASSED [ 92%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_repeated_numbers_raises_value_error PASSED [ 96%]
test/number_asc_order_test.py::TestNumberAscOrder::test_sort_uses_stack_public_interface PASSED [100%]

Name                        Stmts   Miss Branch BrPart  Cover   Missing
-----------------------------------------------------------------------
src/__init__.py                 0      0      0      0   100%
src/custom_stack_class.py      24      0      6      0   100%
src/number_asc_order.py        20      0     14      0   100%
-----------------------------------------------------------------------
TOTAL                          44      0     20      0   100%

25 passed
```

Os mesmos 25 testes continuam passando com 100% de cobertura; agora os IDs dos testes incluem
o nome da classe (`arquivo::Classe::teste`).

---

## Resumo final

| Item | Resultado |
|------|-----------|
| Bug encontrado e corrigido | `push` comparava o método `self.size` com o limite, e a pilha nunca ficava cheia |
| Testes da `CustomStack` | 1 → 9 testes, na classe `TestCustomStack` |
| Testes da `NumberAscOrder` | 16 testes (9 métodos, 3 deles parametrizados), na classe `TestNumberAscOrder` |
| Cobertura da `CustomStack` | 79% (linhas) / 70% (branches) → **100% / 100%** |
| Cobertura da `NumberAscOrder` | **100% / 100%** |
| Métodos adicionados às classes existentes | nenhum |
| Ferramentas | pytest 8.1.1, pytest-cov 5.0.0, pytest-mock 3.14.0 |
