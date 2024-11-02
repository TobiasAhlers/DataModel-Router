from conftest import *


def test_save_valid(client: TestClient):
    """
    Test that valid data is saved correctly.
    """
    response = client.post("/save", params={"name": "Bob", "age": 40})
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "Bob", "age": 40}


def test_save_invalid(client: TestClient):
    """
    Test that an HTTPException is raised when invalid data is provided.
    """
    response = client.post("/save", params={"invalid_field": "value"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid query parameter: invalid_field"}


def test_save_update(client: TestClient):
    """
    Test that an existing entry is updated when the primary key is provided.
    """
    response = client.post("/save", params={"id": 1, "name": "Alice", "age": 35})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "age": 35}
    response = client.get("/get_one", params={"id": 1})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "age": 35}
