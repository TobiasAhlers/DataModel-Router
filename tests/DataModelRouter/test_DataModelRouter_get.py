from conftest import *


def test_valid(client: TestClient):
    """
    Test that valid query parameters return the expected data.
    """
    TestDataModel(name="Alice", age=30).save()
    response = client.get("testdatamodel/1/")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "name": "Alice", "age": 30}


def test_nonexistent_entry(client: TestClient):
    """
    Test that an HTTPException is raised when no entry matches the primary key.
    """
    response = client.get("testdatamodel/2/")
    assert response.status_code == 404
    assert response.json() == {"detail": "No TestDataModel entry with id 2"}
