from conftest import *


def test_set_field_value_valid(client: TestClient):
    """
    Test that valid data is saved correctly.
    """
    response = client.put("/1/name", params={"name": "Bob"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Bob", "age": 30}


def test_set_field_value_invalid(client: TestClient):
    """
    Test that an HTTPException is raised when an invalid field is provided.
    """
    response = client.put("/1/invalid_field", params={"invalid_field": "value"})
    assert response.status_code == 404


def test_no_entry(client: TestClient):
    """
    Test that an HTTPException is raised when no entry matches the primary key.
    """
    response = client.put("/2/name", params={"name": "Bob"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No TestDataModel entry with id 2"}


def test_multiple_entries(client: TestClient):
    """
    Test that multiple entries are returned when multiple entries match the query parameters.
    """
    response = client.put("/1/age", params={"age": 35})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "age": 35}

    TestDataModel(name="Bob", age=35).save()
    response = client.put("/1/age", params={"age": 30})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "age": 30}
    response = client.put("/2/age", params={"age": 40})
    assert response.status_code == 200
    assert response.json() == {"id": 2, "name": "Bob", "age": 40}
