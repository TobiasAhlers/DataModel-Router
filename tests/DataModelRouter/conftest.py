import pytest

from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlmodel import create_engine
from data_model_orm import DataModel, Field
from data_model_router.main import DataModelRouter
from typing import Optional


class TestDataModel(DataModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str
    age: int


@pytest.fixture
def test_data_model():
    TestDataModel.__engine__ = create_engine("sqlite:///database.db")
    TestDataModel.metadata.create_all(TestDataModel.__engine__)
    TestDataModel(id=1, name="Alice", age=30).save()
    yield TestDataModel
    TestDataModel.metadata.drop_all(TestDataModel.__engine__)


@pytest.fixture
def client(test_data_model: TestDataModel):
    app = FastAPI()
    app.include_router(DataModelRouter(TestDataModel))
    client = TestClient(app)
    return client
