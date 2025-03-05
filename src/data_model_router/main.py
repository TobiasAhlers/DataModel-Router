from typing import Any, List

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import Response
from pydantic import ValidationError

from data_model_orm import DataModel

from .utils import extract_and_validate_query_params, generate_function


class DataModelRouter(APIRouter):
    def __init__(
        self, data_model: type[DataModel], prefix: str | None = None, *args, **kwargs
    ) -> None:
        super().__init__(
            prefix=prefix if prefix is not None else f"/{data_model.__name__.lower()}",
            *args,
            **kwargs,
        )
        self.data_model = data_model
        self.primary_key = data_model.get_primary_key()

        def search(request: Request, *args, **kwargs) -> List[DataModel]:
            return self.data_model.get_all(
                **extract_and_validate_query_params(request, self.data_model)
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
                    for field_name, field in self.data_model.model_fields.items()
                },
                action=search,
            ),
            methods=["GET"],
            tags=[data_model.__name__],
            response_model=List[self.data_model],
            name=f"Search {data_model.__name__}",
            description=f"Return all {data_model.__name__} entries where the query parameters match the fields of the model. If no query parameters are provided, all {data_model.__name__} entries will be returned.",
            operation_id=f"search_{data_model.__name__.lower()}",
        )

        @self.post(
            "/",
            response_model=self.data_model,
            tags=[data_model.__name__],
            description=f"Create a new {data_model.__name__} entry.",
            operation_id=f"create_{data_model.__name__.lower()}",
            name=f"Create new {data_model.__name__}",
            status_code=201,
        )
        def create(data: self.data_model) -> DataModel:
            try:
                data = self.data_model.model_validate(data)
            except ValidationError as e:
                raise HTTPException(status_code=422, detail=e.errors())
            if (
                self.data_model.get_one(
                    **{self.primary_key: getattr(data, self.primary_key)}
                )
                is not None
            ):
                raise HTTPException(
                    status_code=409,
                    detail=f"Data already exists with {self.primary_key} {getattr(data, self.primary_key)}",
                )
            data.save()
            return data

        def save(request: Request, *args, **kwargs) -> DataModel:
            query_params = extract_and_validate_query_params(request, self.data_model)
            if self.data_model.get_primary_key() in query_params:
                data = self.data_model.get_one(
                    **{
                        self.data_model.get_primary_key(): query_params[
                            self.data_model.get_primary_key()
                        ]
                    }
                )
                if data is None:
                    data = self.data_model(**query_params)
                for key, value in query_params.items():
                    setattr(data, key, value)
            else:
                data = self.data_model(**query_params)
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
                    for field_name, field in self.data_model.model_fields.items()
                },
                action=save,
            ),
            methods=["POST"],
            tags=[data_model.__name__],
            response_model=self.data_model,
            description=f"Saves a {data_model.__name__} entry with the provided query parameters. If no query parameters are provided, a new {data_model.__name__} entry will be saved with the default values of the model fields.",
        )

        primary_key = data_model.get_primary_key()

        def delete(request: Request, **kwargs) -> Response:

            data = self.data_model.get_one(**{primary_key: kwargs[primary_key]})
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
                parameters={
                    primary_key: {
                        "type_": data_model.model_fields[primary_key].annotation,
                        "default": None,
                    }
                },
                action=delete,
            ),
            methods=["DELETE"],
            tags=[data_model.__name__],
            description=f"Deletes the {data_model.__name__} entry with the provided {primary_key}.",
        )

        self.add_api_route(
            f"/{{{primary_key}}}/",
            generate_function(
                function_name="get",
                parameters={
                    primary_key: {
                        "type_": data_model.model_fields[primary_key].annotation,
                        "default": None,
                    }
                },
                action=self.data_model.get_one,
            ),
            methods=["GET"],
            tags=[data_model.__name__],
            response_model=self.data_model | None,
            description=f"Return the {data_model.__name__} entry with the provided {primary_key}.",
        )

        for field_name, field in data_model.model_fields.items():
            if field_name == primary_key:
                continue

            def create_get_field_value_fn(field_name):
                def get_field_value(request: Request, *args, **kwargs) -> Any:
                    data = self.data_model.get_one(**{primary_key: kwargs[primary_key]})
                    if data is None:
                        raise HTTPException(
                            status_code=404,
                            detail=f"No {data_model.__name__} entry with {primary_key} {kwargs[primary_key]}",
                        )
                    return {field_name: getattr(data, field_name)}

                return get_field_value

            self.add_api_route(
                f"/{{{primary_key}}}/{field_name}",
                generate_function(
                    function_name=f"get_{field_name}",
                    parameters={
                        primary_key: {
                            "type_": data_model.model_fields[primary_key].annotation,
                            "default": None,
                        }
                    },
                    action=create_get_field_value_fn(field_name),
                ),
                methods=["GET"],
                tags=[data_model.__name__],
                response_model=dict[str, field.annotation],
                description=f"Return the {field_name} of the {data_model.__name__} entry with the provided {primary_key}.",
            )

            def create_set_field_value_fn(field_name: str):
                def set_field_value(request: Request, **kwargs):

                    data = self.data_model.get_one(**{primary_key: kwargs[primary_key]})
                    if data is None:
                        raise HTTPException(
                            status_code=404,
                            detail=f"No {data_model.__name__} entry with {primary_key} {kwargs[primary_key]}",
                        )
                    setattr(data, field_name, kwargs[field_name])
                    data.save()
                    return data

                return set_field_value

            self.add_api_route(
                f"/{{{primary_key}}}/{field_name}",
                generate_function(
                    function_name=f"set_{field_name}",
                    parameters={
                        primary_key: {
                            "type_": data_model.model_fields[primary_key].annotation,
                            "default": None,
                        },
                        field_name: {"type_": field.annotation, "default": None},
                    },
                    action=create_set_field_value_fn(field_name),
                ),
                methods=["PUT"],
                tags=[data_model.__name__],
                response_model=self.data_model,
                description=f"Set the {field_name} of the {data_model.__name__} entry with the provided {primary_key}.",
            )
