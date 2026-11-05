import pytest

from src.custom_stack_class import *

def test_push_one_elementinstack():
    element_value = 5.0
    value = 0.0

    cut = CustomStack(5)
    cut.push(element_value)
    assert cut.is_empty() == False
    assert element_value == cut.top()
    assert 1 == cut.size()


def test_push_on_full_stack_raises_exception():
    stack = CustomStack(5)
    for value in range(5):
        stack.push(value)
    with pytest.raises(StackFullException):
        stack.push(99)
    assert stack.size() == 5
