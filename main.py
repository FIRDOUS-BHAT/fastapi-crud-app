from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class ItemModel(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, default=None)
    price = Column(Float)
    tax = Column(Float, default=None)


Base.metadata.create_all(bind=engine)


class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None


@app.post("/items/", response_model=Item)
def create_item(item: Item):
    db = SessionLocal()
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item


@app.get("/items/", response_model=List[Item])
def read_items():
    db = SessionLocal()
    items = db.query(ItemModel).all()
    db.close()
    return items


@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int):
    db = SessionLocal()
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    db.close()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, item: Item):
    db = SessionLocal()
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    for key, value in item.dict().items():
        setattr(db_item, key, value)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item


@app.delete("/items/{item_id}", response_model=Item)
def delete_item(item_id: int):
    db = SessionLocal()
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    db.close()
    return db_item
