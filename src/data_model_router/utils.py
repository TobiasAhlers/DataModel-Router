from typing import Any, Callable
from inspect import Signature, Parameter, _empty

from fastapi import HTTPException, Request

from data_model_orm import DataModel


def generate_function(
    function_name: str,
    parameters: dict,
    action: Callable,
    description: str = None,
) -> Callable:
    """
    Dynamically generates a function with the given name, parameters, and action.

    Args:
        function_name (str): The name of the generated function.
        parameters (dict): A dictionary where keys are parameter names and values are dictionaries
                           with 'type_' and 'default' keys.
        action (Callable): The action to be performed by the generated function.
        description (str, optional): The docstring for the generated function. Defaults to None.

    Returns:
        Callable: The dynamically generated function.
    """
    def generated_function(request: Request, *args, **kwargs):
        return action(request=request, *args, **kwargs)

    generated_function.__doc__ = description
    generated_function.__name__ = function_name
    generated_function.__signature__ = Signature(
        parameters=[
            Parameter(
                name="request", kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=Request
            )
        ]
        + [
            Parameter(
                name=name,
                kind=Parameter.POSITIONAL_OR_KEYWORD,
                annotation=annotation["type_"],
                default=annotation["default"] if "default" in annotation else _empty,
            )
            for name, annotation in parameters.items()
        ]
    )
    return generated_function


def extract_and_validate_query_params(
    request: Request, data_model: type[DataModel]
) -> dict[str, Any]:
    """
    Extracts and validates query parameters from the request against the data model.

    Args:
        request (Request): The FastAPI request object containing query parameters.
        data_model (type[DataModel]): The data model class to validate query parameters against.

    Raises:
        HTTPException: If a query parameter is not valid according to the data model.

    Returns:
        dict[str, Any]: A dictionary of validated query parameters.
    """
    where = {}
    for query_param in request.query_params:
        if query_param not in data_model.model_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid query parameter: {query_param}",
            )
        where[query_param] = request.query_params[query_param]
    return where