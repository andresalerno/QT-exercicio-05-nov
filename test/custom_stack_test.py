import pytest

from src.custom_stack_class import (
    CustomStack,
    StackEmptyException,
    StackFullException,
)

LIMIT = 5


class TestCustomStack:

    @pytest.fixture
    def stack(self):
        return CustomStack(LIMIT)

    def test_new_stack_is_empty(self, stack):
        assert stack.is_empty() is True
        assert stack.size() == 0
        assert stack.limit == LIMIT

    def test_push_one_element_in_stack(self, stack):
        stack.push(5.0)
        assert stack.is_empty() is False
        assert stack.top() == 5.0
        assert stack.size() == 1

    def test_push_many_elements_top_is_last_pushed(self, stack):
        for value in [1, 2, 3]:
            stack.push(value)
        assert stack.top() == 3
        assert stack.size() == 3

    def test_pop_returns_elements_in_lifo_order(self, stack):
        for value in [1, 2, 3]:
            stack.push(value)
        assert stack.pop() == 3
        assert stack.pop() == 2
        assert stack.pop() == 1
        assert stack.is_empty() is True

    def test_top_does_not_remove_element(self, stack):
        stack.push("a")
        assert stack.top() == "a"
        assert stack.top() == "a"
        assert stack.size() == 1

    def test_pop_on_empty_stack_raises_exception(self, stack):
        with pytest.raises(StackEmptyException):
            stack.pop()

    def test_top_on_empty_stack_raises_exception(self, stack):
        with pytest.raises(StackEmptyException):
            stack.top()

    def test_push_on_full_stack_raises_exception(self, stack):
        for value in range(LIMIT):
            stack.push(value)
        with pytest.raises(StackFullException):
            stack.push(99)
        assert stack.size() == LIMIT

    def test_push_after_pop_on_full_stack_is_allowed(self, stack):
        for value in range(LIMIT):
            stack.push(value)
        stack.pop()
        stack.push(99)
        assert stack.top() == 99
        assert stack.size() == LIMIT
