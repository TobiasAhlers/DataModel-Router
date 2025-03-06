from data_model_orm import DataModel
from fastapi import APIRouter, Request
from typing import List

from ..utils import extract_and_validate_query_params, generate_function


class SearchRouter(APIRouter):
    """
    A router for a DataModel that provides search operations for the DataModel.

    This router provides a single GET endpoint that allows for searching for entries in the DataModel.
    """

    def __init__(self, data_model: type[DataModel]) -> None:
        super().__init__()

        def search(request: Request, *args, **kwargs) -> List[DataModel]:
            """
            Search for entries in the DataModel based on the query parameters provided.

            If no query parameters are provided, all entries in the DataModel will be returned.

            Args:
                request (Request): The request object.

            Returns:
                List[DataModel]: A list of DataModel objects that match the query parameters.
            """
            return data_model.get_all(
                **extract_and_validate_query_params(request, data_model)
            )

        self.add_api_route(
            "/",
            generate_function(
                function_name="search",
                parameters={
                    field_name: {
                        "type_": field.annotation,
                        "default": None,
                    }
                    for field_name, field in data_model.model_fields.items()
                },
                action=search,
            ),
            methods=["GET"],
            tags=[data_model.__name__],
            response_model=List[data_model],
            name=f"Search {data_model.__name__}",
            description=f"Return all {data_model.__name__} entries where the query parameters match the fields of the model. If no query parameters are provided, all {data_model.__name__} entries will be returned.",
            operation_id=f"search_{data_model.__name__.lower()}",
        )
