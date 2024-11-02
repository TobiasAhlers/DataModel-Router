from conftest import *


def test_get_field_value_valid(client: TestClient):
    """
    Test that valid query parameters return the expected data.
    """
    response = client.get("testdatamodel/1/name")
    assert response.status_code == 200
    assert response.json() == {"name": "Alice"}


def test_get_field_value_invalid(client: TestClient):
    """
    Test that an HTTPException is raised when an invalid field is provided.
    """
    response = client.get("testdatamodel/1/invalid_field")
    assert response.status_code == 404


def test_no_entry(client: TestClient):
    """
    Test that an HTTPException is raised when no entry matches the primary key.
    """
    response = client.get("testdatamodel/2/name")
    assert response.status_code == 404
    assert response.json() == {"detail": "No TestDataModel entry with id 2"}


def test_multiple_entries(client: TestClient):
    """
    Test that multiple entries are returned when multiple entries match the query parameters.
    """
    response = client.get("testdatamodel/1/age")
    assert response.status_code == 200
    assert response.json() == {"age": 30}

    TestDataModel(name="Bob", age=35).save()
    response = client.get("testdatamodel/1/age")
    assert response.status_code == 200
    assert response.json() == {"age": 30}
    response = client.get("testdatamodel/2/age")
    assert response.status_code == 200
    assert response.json() == {"age": 35}


def test_multiple_models(client: TestClient):
    """
    Test that multiple models are returned when multiple models match the query parameters.
    """
    response = client.get("testdatamodel/1/name")
    assert response.status_code == 200
    assert response.json() == {"name": "Alice"}

    response = client.get("testdatamodel2/1/city")
    assert response.status_code == 200
    assert response.json() == {"city": "New York"}