from pydantic import BaseModel, Field
from typing import Optional, List

class DeliveryAddress(BaseModel):
    street: str 
    city: str 
    province: str 
    postalCode: str 
    country: str    


class UserModel(BaseModel):
    firstName: Optional[str]
    lastName: Optional[str]
    phoneNumber: Optional[str]
    emails: List[str]
    deliveryAddress: DeliveryAddress