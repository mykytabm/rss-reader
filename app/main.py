from typing import final
from fastapi import FastAPI

import models
from database import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# dependancy
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
