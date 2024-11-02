import pytest

from fastapi.testclient import TestClient
from fastapi import FastAPI
from sqlmodel import create_engine
from sqlalchemy import Engine
from data_model_orm import DataModel, Field
from data_model_router.main import DataModelRouter
from typing import Optional


class TestDataModel(DataModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    name: str
    age: int


class TestDataModel2(DataModel, table=True):
    id: Optional[int] = Field(primary_key=True)
    country: str
    city: str


@pytest.fixture
def engine() -> Engine:
    return create_engine("sqlite:///database.db")


@pytest.fixture
def test_data_model(engine: Engine):
    TestDataModel.__engine__ = engine
    TestDataModel.metadata.create_all(bind=engine)
    TestDataModel(id=1, name="Alice", age=30).save()
    yield TestDataModel
    TestDataModel.metadata.drop_all(bind=engine)


@pytest.fixture
def test_data_model2(engine: Engine):
    TestDataModel2.__engine__ = engine
    TestDataModel2.metadata.create_all(bind=engine)
    TestDataModel2(id=1, country="USA", city="New York").save()
    yield TestDataModel2
    TestDataModel2.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_data_model: TestDataModel, test_data_model2: TestDataModel2):
    app = FastAPI()
    app.include_router(DataModelRouter(TestDataModel))
    app.include_router(DataModelRouter(TestDataModel2))
    client = TestClient(app)
    return client
