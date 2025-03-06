from data_model_orm import DataModel
from fastapi import APIRouter, HTTPException

from ..utils import generate_function


class GetByIdRouter(APIRouter):
    """
    A router for a DataModel that provides get by id operations for the DataModel.

    This router provides a single GET endpoint that allows for getting a single entry in the DataModel by its primary key.
    """

    def __init__(self, data_model: type[DataModel]) -> None:
        super().__init__()

        primary_key = data_model.get_primary_key()

        def get_entry_by_id(**kwargs) -> DataModel | None:
            """
            Get a single entry in the DataModel by its primary key.

            Args:
                **kwargs: The primary key value for the entry.
            """
            data = data_model.get_one(**{primary_key: kwargs[primary_key]})
            if data is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"No {data_model.__name__} entry with {primary_key} {kwargs[primary_key]}",
                )
            return data

        self.add_api_route(
            f"/{{{primary_key}}}/",
            generate_function(
                function_name="get",
                parameters={
                    primary_key: {
                        "type_": str,
                    }
                },
                action=get_entry_by_id,
            ),
            methods=["GET"],
            tags=[data_model.__name__],
            response_model=data_model,
            name=f"Get {data_model.__name__} by ID",
            description=f"Return the {data_model.__name__} entry with the provided {primary_key}.",
            operation_id=f"get_{data_model.__name__.lower()}_by_{primary_key.lower()}",
        )
