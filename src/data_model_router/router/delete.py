from data_model_orm import DataModel
from fastapi import APIRouter, Request, HTTPException, Response

from ..utils import generate_function


class DeleteRouter(APIRouter):
    """
    A router for a DataModel that provides delete operations for the DataModel.

    This router provides a single DELETE endpoint that allows for deleting entries in the DataModel.
    """

    def __init__(self, data_model: type[DataModel]) -> None:
        super().__init__()
        primary_key = data_model.get_primary_key()

        def delete(request: Request, *args, **kwargs) -> None:
            """
            Delete a DataModel entry with the provided query parameters.

            Args:
                request (Request): The request object.
            """
            data = data_model.get_one(**{primary_key: kwargs[primary_key]})
            if data is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"No {data_model.__name__} entry with {primary_key} {kwargs[primary_key]}",
                )
            data.delete()
            return Response(status_code=204)

        self.add_api_route(
            f"/{{{primary_key}}}/",
            generate_function(
                function_name="delete",
                parameters={primary_key: {"type_": str}},
                action=delete,
            ),
            methods=["DELETE"],
            tags=[data_model.__name__],
            description=f"Delete a {data_model.__name__} entry with the provided {primary_key}.",
            operation_id=f"delete_{data_model.__name__.lower()}",
        )
