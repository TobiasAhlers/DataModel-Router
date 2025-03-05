from conftest import *


def test_delete_existing(client: TestClient):
    """
    Test that an existing entry is deleted correctly.
    """
    response = client.delete("testdatamodel/1/")
    assert response.status_code == 204
    assert TestDataModel.get_all(id=1) == []


def test_no_entry(client: TestClient):
    """
    Test that an HTTPException is raised when no entry matches the primary key.
    """
    assert TestDataModel.get_all(id=2) == []
    response = client.delete("testdatamodel/2/")
    assert response.status_code == 404
    assert TestDataModel.get_all(id=2) == []


def test_delete_multiple_models(client: TestClient):
    """
    Test that multiple models can be deleted.
    """
    response = client.delete("testdatamodel/1/")
    assert response.status_code == 204
    assert TestDataModel.get_all(id=1) == []

    response = client.delete("testdatamodel2/1/")
    assert response.status_code == 204
    response = client.get("testdatamodel2/get_one", params={"id": 1})
    assert TestDataModel2.get_all(id=1) == []
