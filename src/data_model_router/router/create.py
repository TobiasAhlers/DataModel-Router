from data_model_orm import DataModel
from fastapi import APIRouter, HTTPException
from pydantic import ValidationError


class CreateRouter(APIRouter):
    """
    A router for a DataModel that provides create operations for the DataModel.

    This router provides a single POST endpoint that allows for creating new entries in the DataModel.
    """

    def __init__(self, data_model: type[DataModel]) -> None:
        super().__init__()
        primary_key = data_model.get_primary_key()

        @self.post(
            "/",
            response_model=data_model,
            tags=[data_model.__name__],
            description=f"Create a new {data_model.__name__} entry.",
            operation_id=f"create_{data_model.__name__.lower()}",
            name=f"Create new {data_model.__name__}",
            status_code=201,
        )
        def create(data: data_model) -> DataModel: # type: ignore
            try:
                data = data_model.model_validate(data)
            except ValidationError as e:
                raise HTTPException(status_code=422, detail=e.errors())
            if (
                data_model.get_one(**{primary_key: getattr(data, primary_key)})
                is not None
            ):
                raise HTTPException(
                    status_code=409,
                    detail=f"Data already exists with {primary_key} {getattr(data, primary_key)}",
                )
            data.save()
            return data
