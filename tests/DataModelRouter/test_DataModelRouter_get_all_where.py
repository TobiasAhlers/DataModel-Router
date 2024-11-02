from conftest import *


def test_get_all_where_valid(client: TestClient):
    """
    Test that valid query parameters return the expected data.
    """
    response = client.get("/", params={"id": 1})
    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "Alice", "age": 30}]


def test_get_all_where_invalid(client: TestClient):
    """
    Test that an HTTPException is raised when invalid query parameters are provided.
    """
    response = client.get("/", params={"invalid_param": "value"})
    assert response.status_code == 400
    assert response.json() == {"detail": "Invalid query parameter: invalid_param"}


def test_no_entry(client: TestClient):
    """
    Test that an empty list is returned when no entries match the query parameters.
    """
    response = client.get("/", params={"id": 2})
    assert response.status_code == 200
    assert response.json() == []
