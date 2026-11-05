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
