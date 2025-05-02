# models/__init__.py
from pydantic import BaseModel
from typing import List


class Product(BaseModel):
    title: str
    category: str
    price: float
    rating: float
    id: str
    stock: str


class ScrapeResponse(BaseModel):
    products: List[Product]
