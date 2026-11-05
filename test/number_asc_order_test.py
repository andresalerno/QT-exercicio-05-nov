import random

import pytest

from src.custom_stack_class import CustomStack
from src.number_asc_order import NumberAscOrder

STACK_LIMIT = 6


def build_stack(numbers):
    stack = CustomStack(STACK_LIMIT)
    for number in numbers:
        stack.push(number)
    return stack


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

    def test_sort_known_numbers_returns_ascending_list(self, cut):
        assert cut.sort(build_stack([42, 7, 59, 13, 1, 60])) == [1, 7, 13, 42, 59, 60]

    def test_sort_keeps_stack_in_original_draw_order(self, cut):
        drawn = random.sample(range(1, 61), 6)
        stack = build_stack(drawn)
        cut.sort(stack)
        assert stack.size() == 6
        assert [stack.pop() for _ in range(6)] == list(reversed(drawn))

    # Cenário 2: pilha de 6 posições vazia
    def test_sort_empty_stack_returns_empty_list(self, cut):
        stack = CustomStack(STACK_LIMIT)
        assert cut.sort(stack) == []
        assert stack.is_empty() is True

    # Tratamentos / verificações
    @pytest.mark.parametrize("invalid", [None, [1, 2, 3], "123456", 6])
    def test_sort_invalid_parameter_raises_type_error(self, cut, invalid):
        with pytest.raises(TypeError):
            cut.sort(invalid)

    @pytest.mark.parametrize("value", [0, 61, -5])
    def test_sort_number_out_of_range_raises_value_error(self, cut, value):
        with pytest.raises(ValueError):
            cut.sort(build_stack([1, 2, 3, 4, 5, value]))

    @pytest.mark.parametrize("value", [7.5, "7", True])
    def test_sort_non_integer_value_raises_type_error(self, cut, value):
        with pytest.raises(TypeError):
            cut.sort(build_stack([1, 2, 3, 4, 5, value]))

    def test_sort_repeated_numbers_raises_value_error(self, cut):
        with pytest.raises(ValueError):
            cut.sort(build_stack([10, 20, 30, 40, 50, 10]))

    # pytest-mock: garante que sort usa só a interface pública da pilha
    def test_sort_uses_stack_public_interface(self, mocker, cut):
        stack = mocker.Mock(spec=CustomStack)
        stack.is_empty.side_effect = [False, False, True]
        stack.pop.side_effect = [30, 10]

        assert cut.sort(stack) == [10, 30]
        assert stack.pop.call_count == 2
        stack.push.assert_has_calls([mocker.call(10), mocker.call(30)])
