# DataModel-Router

DataModel-Router is a simple router for data models built with FastAPI and SQLModel. It provides a set of utilities and routes to manage data models efficiently.

## Features

- Dynamic route generation for CRUD operations
- Query parameter validation
- Easy integration with FastAPI

## Installation

To install the dependencies, run:

```sh
pip install -r 
```

## Usage

### Define Your Data Model
Create a data model using DataModel-ORM:
```python
from datamodel_orm import DataMode, Field
from typing import Optional

class TestDataModel(DataModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int
```

### Create and Include the Router
Create a router for your data model and include it in your FastAPI app:

```python
from fastapi import FastAPI
from data_model_router import DataModelRouter

app = FastAPI()
app.include_router(DataModelRouter(TestDataModel))
```

### Run the Application
Run your FastAPI application:

```sh
uvicorn main:app --reload
```