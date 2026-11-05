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
