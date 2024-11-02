import pytest

from fastapi import Request
from src.data_model_router.utils import generate_function
from inspect import Signature, Parameter


def mock_action(request: Request, param1: int, param2: str):
    """
    Mock action function to be used with generate_function.

    Args:
        request (Request): The request object.
        param1 (int): The first parameter.
        param2 (str): The second parameter.

    Returns:
        dict: A dictionary containing param1 and param2.
    """
    return {"param1": param1, "param2": param2}


def test_generate_function_name():
    """
    Test that generate_function correctly sets the function name.
    """
    generated_func = generate_function(
        function_name="test_func",
        parameters={
            "param1": {"type_": int, "default": 0},
            "param2": {"type_": str, "default": ""},
        },
        action=mock_action,
        description="This is a test function",
    )
    assert generated_func.__name__ == "test_func"


def test_generate_function_docstring():
    """
    Test that generate_function correctly sets the function docstring.
    """
    generated_func = generate_function(
        function_name="test_func",
        parameters={
            "param1": {"type_": int, "default": 0},
            "param2": {"type_": str, "default": ""},
        },
        action=mock_action,
        description="This is a test function",
    )
    assert generated_func.__doc__ == "This is a test function"


def test_generate_function_signature():
    """
    Test that generate_function correctly sets the function signature.
    """
    generated_func = generate_function(
        function_name="test_func",
        parameters={
            "param1": {"type_": int, "default": 0},
            "param2": {"type_": str, "default": ""},
        },
        action=mock_action,
        description="This is a test function",
    )
    expected_signature = Signature(
        parameters=[
            Parameter(
                name="request", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=Request
            ),
            Parameter(
                name="param1",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=int,
                default=0,
            ),
            Parameter(
                name="param2",
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=str,
                default="",
            ),
        ]
    )
    assert generated_func.__signature__ == expected_signature


def test_generate_function_behavior():
    """
    Test that generate_function correctly implements the behavior of the action function.
    """
    generated_func = generate_function(
        function_name="test_func",
        parameters={
            "param1": {"type_": int, "default": 0},
            "param2": {"type_": str, "default": ""},
        },
        action=mock_action,
        description="This is a test function",
    )

    class MockRequest:
        query_params = {}

    request = MockRequest()
    result = generated_func(request, param1=10, param2="test")
    assert result == {"param1": 10, "param2": "test"}
