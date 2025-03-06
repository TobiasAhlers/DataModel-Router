from conftest import *


def test_create_valid(client: TestClient):
    """
    Test that valid data is created.
    """
    response = client.post("testdatamodel/", json={"name": "Bob", "age": 40})
    assert response.status_code == 201
    assert response.json() == {"id": 2, "name": "Bob", "age": 40}


def test_create_invalid_schema(client: TestClient):
    """
    Test that an HTTPException is raised when invalid data is provided.
    """
    response = client.post("testdatamodel/", json={"invalid_field": "value"})
    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "input": None,
                "loc": [
                    "name",
                ],
                "msg": "field required",
                "type": "value_error.missing",
                "msg": "Input should be a valid string",
                "type": "string_type",
                "url": "https://errors.pydantic.dev/2.10/v/string_type",
            },
            {
                "input": None,
                "loc": [
                    "age",
                ],
                "msg": "field required",
                "type": "value_error.missing",
                "msg": "Input should be a valid integer",
                "type": "int_type",
                "url": "https://errors.pydantic.dev/2.10/v/int_type",
            },
        ]
    }


def test_create_existing_with_id(client: TestClient):
    """
    Test that an HTTPException is raised when the primary key is provided.
    """
    response = client.post("testdatamodel/", json={"id": 1, "name": "Alice", "age": 35})
    assert response.status_code == 409
    assert response.json() == {"detail": "Data already exists with id 1"}


def test_create_existing_without_id(client: TestClient):
    """
    Test that an HTTPException is raised when the data already exists.
    """
    response = client.post("testdatamodel/", json={"name": "Alice", "age": 35})
    assert response.status_code == 409
    assert response.json() == {"detail": "Data already exists with id 1"}