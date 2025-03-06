from data_model_orm import DataModel
from fastapi import APIRouter, Request

from ..utils import extract_and_validate_query_params, generate_function


class SaveRouter(APIRouter):
    """
    A router for a DataModel that provides save operations for the DataModel.

    This router provides a single POST endpoint that allows for saving entries in the DataModel.
    """

    def __init__(self, data_model: type[DataModel]) -> None:
        super().__init__()
        primary_key = data_model.get_primary_key()

        def save(request: Request, *args, **kwargs) -> DataModel:
            """
            Save a DataModel entry with the provided query parameters.

            If no query parameters are provided, a new DataModel entry will be saved with the default values of the model fields.

            Args:
                request (Request): The request object.

            Returns:
                DataModel: The saved DataModel entry.
            """
            query_params = extract_and_validate_query_params(request, data_model)
            if primary_key in query_params:
                data = data_model.get_one(**{primary_key: query_params[primary_key]})
                if data is None:
                    data = data_model(**query_params)
                for key, value in query_params.items():
                    setattr(data, key, value)
            else:
                data = data_model(**query_params)
            data.save()
            data = data.model_validate(data)
            return data

        self.add_api_route(
            "/save",
            generate_function(
                function_name="save",
                parameters={
                    field_name: {
                        "type_": field.annotation,
                        "default": None,
                    }
                    for field_name, field in data_model.model_fields.items()
                },
                action=save,
            ),
            methods=["POST"],
            tags=[data_model.__name__],
            response_model=data_model,
            description=f"Saves a {data_model.__name__} entry with the provided query parameters. If no query parameters are provided, a new {data_model.__name__} entry will be saved with the default values of the model fields.",
            operation_id=f"save_{data_model.__name__.lower()}",
        )
