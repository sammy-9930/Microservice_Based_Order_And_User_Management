from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Item(BaseModel):
    itemId: str
    quantity: int = Field(..., ge=1)
    price: float = Field(..., ge=0)

class DeliveryAddress(BaseModel):
    street: str
    city: str
    province: str
    postalCode: str
    country: str

class OrderModel(BaseModel):
    userId: Optional[str] = None 
    items: List[Item]
    emails: Optional[List[str]]
    deliveryAddress: DeliveryAddress
    orderStatus: str


