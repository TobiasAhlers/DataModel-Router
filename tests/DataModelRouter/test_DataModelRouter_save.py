from conftest import *


def test_save_valid(client: TestClient):
    """
    Test that valid data is saved correctly.
    """
    response = client.post("testdatamodel/save", params={"name": "Bob", "age": 40})
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "Bob", "age": 40}


def test_save_invalid(client: TestClient):
    """
    Test that an HTTPException is raised when invalid data is provided.
    """
    response = client.post("testdatamodel/save", params={"invalid_field": "value"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid query parameter: invalid_field"}


def test_save_update(client: TestClient):
    """
    Test that an existing entry is updated when the primary key is provided.
    """
    response = client.post(
        "testdatamodel/save", params={"id": 1, "name": "Alice", "age": 35}
    )
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "age": 35}
    response = client.get("testdatamodel/get_one", params={"id": 1})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "age": 35}


def test_multiple_models(client: TestClient):
    """
    Test that multiple models are returned when multiple models match the query parameters.
    """
    response = client.post("testdatamodel/save", params={"name": "Bob", "age": 40})
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "Bob", "age": 40}

    response = client.post(
        "testdatamodel2/save", params={"country": "USA", "city": "New York"}
    )
    assert response.status_code == 200
    assert response.json() == {"id": 2, "country": "USA", "city": "New York"}


def test_create_new_model(client: TestClient):
    """
    Test that a new model is created when the primary key is not provided.
    """
    response = client.post(
        "testdatamodel2/save", params={"country": "USA", "city": "New York"}
    )
    assert response.status_code == 200

    response = client.get("testdatamodel2/get_one", params={"id": 1})
    assert response.status_code == 200


def test_save_new_with_id(client: TestClient):
    """
    Test that a new model is created with the provided primary key.
    """
    response = client.post(
        "testdatamodel2/save", params={"id": 3, "country": "USA", "city": "New York"}
    )
    assert response.status_code == 200

    response = client.get("testdatamodel2/get_one", params={"id": 1})
    assert response.status_code == 200
