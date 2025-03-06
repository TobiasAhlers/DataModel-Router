from fastapi import APIRouter
from data_model_orm import DataModel

from .router import *


class DataModelRouter(APIRouter):
    """
    A router for a DataModel that provides CRUD operations for the DataModel.
    """

    def __init__(
        self, data_model: type[DataModel], prefix: str | None = None, *args, **kwargs
    ) -> None:
        super().__init__(
            prefix=prefix if prefix is not None else f"/{data_model.__name__.lower()}",
            *args,
            **kwargs,
        )

        self.include_router(CreateRouter(data_model))
        self.include_router(DeleteRouter(data_model))
        self.include_router(GetByIdRouter(data_model))
        self.include_router(SaveRouter(data_model))
        self.include_router(SearchRouter(data_model))
