from conftest import *


def test_delete_existing(client: TestClient):
    """
    Test that an existing entry is deleted correctly.
    """
    response = client.delete("/1/")
    assert response.status_code == 204
    response = client.get("/get_one", params={"id": 1})
    assert response.status_code == 404
    assert response.json() == {
        "detail": "No TestDataModel entry found with the provided query parameters."
    }


def test_no_entry(client: TestClient):
    """
    Test that an HTTPException is raised when no entry matches the primary key.
    """
    response = client.delete("/2/")
    assert response.status_code == 404
    assert response.json() == {"detail": "No TestDataModel entry with id 2"}
