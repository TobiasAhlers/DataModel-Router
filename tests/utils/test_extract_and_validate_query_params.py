import pytest
from fastapi import HTTPException
from data_model_router.utils import extract_and_validate_query_params


class MockRequest:
    def __init__(self, query_params):
        self.query_params = query_params


class MockDataModel:
    model_fields = ["valid_param1", "valid_param2"]


def test_extract_and_validate_query_params_valid():
    """
    Test that valid query parameters are correctly extracted and validated.
    """
    request = MockRequest(
        query_params={"valid_param1": "value1", "valid_param2": "value2"}
    )
    data_model = MockDataModel
    result = extract_and_validate_query_params(request, data_model)
    assert result == {"valid_param1": "value1", "valid_param2": "value2"}


def test_extract_and_validate_query_params_invalid():
    """
    Test that an HTTPException is raised when invalid query parameters are provided.
    """
    request = MockRequest(query_params={"invalid_param": "value"})
    data_model = MockDataModel
    with pytest.raises(HTTPException) as exc_info:
        extract_and_validate_query_params(request, data_model)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid query parameter: invalid_param"


def test_extract_and_validate_query_params_empty():
    """
    Test that an empty dictionary is returned when no query parameters are provided.
    """
    request = MockRequest(query_params={})
    data_model = MockDataModel
    result = extract_and_validate_query_params(request, data_model)
    assert result == {}
