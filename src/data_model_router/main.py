from pydantic import BaseModel, ValidationError
from typing import Any, Callable, List
from inspect import Signature, Parameter
from sqlite3 import OperationalError

from fastapi import APIRouter, HTTPException, Request
from starlette.responses import Response

from data_model_orm import DataModel


class Annotation(BaseModel):
    type_: type
    default: Any = None


def generate_function(
    function_name: str,
    parameters: dict[str, Annotation],
    action: Callable,
    description: str = None,
) -> Callable:
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
                annotation=annotation.type_,
                default=annotation.default,
            )
            for name, annotation in parameters.items()
        ]
    )
    return generated_function


def extract_and_validate_query_params(
    request: Request, data_model: type[DataModel]
) -> dict[str, Any]:
    where = {}
    for query_param in request.query_params:
        if query_param not in data_model.model_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid query parameter: {query_param}",
            )
        where[query_param] = request.query_params[query_param]
    return where


class DataModelRouter(APIRouter):
    def __init__(self, data_model: DataModel, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.data_model = data_model

        def get_all_where(request: Request, *args, **kwargs) -> List[DataModel]:
            try:
                return self.data_model.get_all(
                    **extract_and_validate_query_params(request, self.data_model)
                )
            except OperationalError as e:
                print(e)
                # TODO: Change Error handling for security reasons
                raise HTTPException(status_code=400, detail=str(e))

        self.add_api_route(
            "/",
            generate_function(
                function_name="get_all_where",
                parameters={
                    field_name: Annotation(type_=field.annotation, default=None)
                    for field_name, field in self.data_model.model_fields.items()
                },
                action=get_all_where,
            ),
            methods=["GET"],
            tags=[data_model.__name__],
            response_model=List[self.data_model],
            description=f"Return all {data_model.__name__} entries where the query parameters match the fields of the model. If no query parameters are provided, all {data_model.__name__} entries will be returned.",
        )

        def get_one_where(request: Request, *args, **kwargs) -> DataModel | None:
            try:
                return self.data_model.get_one(
                    **extract_and_validate_query_params(request, self.data_model)
                )
            except OperationalError as e:
                print(e)
                # TODO: Change Error handling for security reasons
                raise HTTPException(status_code=400, detail=str(e))

        self.add_api_route(
            "/get_one",
            generate_function(
                function_name="get_one_where",
                parameters={
                    field_name: Annotation(type_=field.annotation, default=None)
                    for field_name, field in self.data_model.model_fields.items()
                },
                action=get_one_where,
            ),
            methods=["GET"],
            tags=[data_model.__name__],
            response_model=self.data_model | None,
            description=f"Return the first {data_model.__name__} entry where the query parameters match the fields of the model. If no query parameters are provided, the first {data_model.__name__} entry will be returned.",
        )

        def save(request: Request, *args, **kwargs) -> DataModel:
            try:
                data = data_model.model_validate(
                    extract_and_validate_query_params(request, self.data_model)
                )
                data.save()
                return data
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=str(e))

        self.add_api_route(
            "/save",
            generate_function(
                function_name="save",
                parameters={
                    field_name: Annotation(type_=field.annotation, default=None)
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
            try:
                data = self.data_model.get_one(**kwargs)
                if data is None:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No {data_model.__name__} entry with {primary_key} {kwargs[primary_key]}",
                    )
                data.delete()

                return Response(
                    status_code=200,
                    content=f"{data_model.__name__} entry deleted successfully.",
                )
            except OperationalError as e:
                print(e)

        self.add_api_route(
            f"/{{{primary_key}}}/",
            generate_function(
                function_name="delete",
                parameters={
                    primary_key: Annotation(
                        type_=data_model.model_fields[primary_key].annotation,
                        default=None,
                    )
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
                    primary_key: Annotation(
                        type_=data_model.model_fields[primary_key].annotation,
                        default=None,
                    )
                },
                action=get_one_where,
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
                    try:
                        data = self.data_model.get_one(
                            **extract_and_validate_query_params(
                                request, self.data_model
                            )
                        )
                        if data is None:
                            raise HTTPException(
                                status_code=404,
                                detail=f"No {data_model.__name__} entry with {primary_key} {kwargs[primary_key]}",
                            )
                        return getattr(data, field_name)
                    except OperationalError as e:
                        print(e)

                return get_field_value

            self.add_api_route(
                f"/{{{primary_key}}}/{field_name}",
                generate_function(
                    function_name=f"get_{field_name}",
                    parameters={
                        primary_key: Annotation(
                            type_=data_model.model_fields[primary_key].annotation,
                            default=None,
                        )
                    },
                    action=create_get_field_value_fn(field_name),
                ),
                methods=["GET"],
                tags=[data_model.__name__],
                response_model=field.annotation,
                description=f"Return the {field_name} of the {data_model.__name__} entry with the provided {primary_key}.",
            )

            def create_set_field_value_fn(field_name: str):
                def set_field_value(request: Request, **kwargs):
                    try:
                        data = self.data_model.get_one(
                            **{primary_key: kwargs[primary_key]}
                        )
                        if data is None:
                            raise HTTPException(
                                status_code=404,
                                detail=f"No {data_model.__name__} entry with {primary_key} {kwargs[primary_key]}",
                            )
                        setattr(data, field_name, kwargs[field_name])
                        data.save()
                        return data
                    except ValidationError as e:
                        raise HTTPException(status_code=400, detail=str(e))
                    except OperationalError as e:
                        print(e)

                return set_field_value

            self.add_api_route(
                f"/{{{primary_key}}}/{field_name}",
                generate_function(
                    function_name=f"set_{field_name}",
                    parameters={
                        primary_key: Annotation(
                            type_=data_model.model_fields[primary_key].annotation,
                            default=None,
                        ),
                        field_name: Annotation(type_=field.annotation, default=None),
                    },
                    action=create_set_field_value_fn(field_name),
                ),
                methods=["PUT"],
                tags=[data_model.__name__],
                response_model=self.data_model,
                description=f"Set the {field_name} of the {data_model.__name__} entry with the provided {primary_key}.",
            )
