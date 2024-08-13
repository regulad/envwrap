import os
from typing import Any, Dict, Tuple, Union

import pytest
from envwrap import envwrap


# Helper function to set environment variables
def set_env_vars(vars_dict: Dict[str, Union[str, int, float, bool]]) -> None:
    for key, value in vars_dict.items():
        os.environ[key] = str(value)


# Helper function to clear environment variables
def clear_env_vars(vars_dict: Dict[str, Any]) -> None:
    for key in vars_dict:
        if key in os.environ:
            del os.environ[key]


# Test cases


def test_standalone_function() -> None:
    @envwrap("TEST_")
    def test_func(a: int = 1, b: str = "default", c: float = 3.14) -> Tuple[int, str, float]:
        return a, b, c

    # Test default values
    assert test_func() == (1, "default", 3.14)

    # Test env var override
    set_env_vars({"TEST_A": "42", "TEST_B": "override", "TEST_C": "2.718"})
    assert test_func() == (42, "override", 2.718)
    clear_env_vars({"TEST_A": "", "TEST_B": "", "TEST_C": ""})

    # Test call override
    assert test_func(a=10, c=1.23) == (10, "default", 1.23)


def test_instance_method() -> None:
    class TestClass:
        @envwrap("TEST_")
        def test_method(self, x: int = 1, y: str = "default") -> Tuple[int, str]:
            return x, y

    obj = TestClass()

    # Test default values
    assert obj.test_method() == (1, "default")

    # Test env var override
    set_env_vars({"TEST_X": "99", "TEST_Y": "override"})
    assert obj.test_method() == (99, "override")
    clear_env_vars({"TEST_X": "", "TEST_Y": ""})

    # Test call override
    assert obj.test_method(y="call_override") == (1, "call_override")


def test_class_method() -> None:
    class TestClass:
        @classmethod
        @envwrap("TEST_")
        def test_class_method(cls, p: int = 1, q: str = "default") -> Tuple[int, str]:
            return p, q

    # Test default values
    assert TestClass.test_class_method() == (1, "default")

    # Test env var override
    set_env_vars({"TEST_P": "88", "TEST_Q": "class_override"})
    assert TestClass.test_class_method() == (88, "class_override")
    clear_env_vars({"TEST_P": "", "TEST_Q": ""})


def test_static_method() -> None:
    class TestClass:
        @staticmethod
        @envwrap("TEST_")
        def test_static_method(m: int = 1, n: str = "default") -> Tuple[int, str]:
            return m, n

    # Test default values
    assert TestClass.test_static_method() == (1, "default")

    # Test env var override
    set_env_vars({"TEST_M": "77", "TEST_N": "static_override"})
    assert TestClass.test_static_method() == (77, "static_override")
    clear_env_vars({"TEST_M": "", "TEST_N": ""})


def test_type_conversion() -> None:
    @envwrap("TEST_")
    def test_func(a: int = 1, b: float = 2.0, c: bool = False) -> Tuple[int, float, bool]:
        return a, b, c

    set_env_vars({"TEST_A": "42", "TEST_B": "3.14", "TEST_C": "True"})
    result = test_func()
    assert result == (42, 3.14, True)
    assert isinstance(result[0], int)
    assert isinstance(result[1], float)
    assert isinstance(result[2], bool)
    clear_env_vars({"TEST_A": "", "TEST_B": "", "TEST_C": ""})


# Run the tests
if __name__ == "__main__":
    pytest.main([__file__])
