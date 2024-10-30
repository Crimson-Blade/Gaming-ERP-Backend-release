from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

class RegistrationBase(BaseModel):
    name: str
    phone_number: str

class RegistrationCreate(RegistrationBase):
    pass

class Registration(RegistrationBase):
    user_id: uuid.UUID
    date: datetime
    bill: Optional[float] = None
    membership: Optional[str] = None
    active: bool

    class Config:
        orm_mode = True

class SystemBase(BaseModel):
    name: str
    amount: float
    start_time: datetime
    end_time: Optional[datetime] = None

class SystemCreate(SystemBase):
    pass

class System(SystemBase):
    id: int
    user_id: uuid.UUID

    class Config:
        orm_mode = True

class MenuBase(BaseModel):
    item_name: str
    item_price: float
    item_photo: Optional[str] = None

class MenuCreate(MenuBase):
    pass

class Menu(MenuBase):
    item_id: int

    class Config:
        orm_mode = True

class OrderBase(BaseModel):
    item_name: str
    quantity: int
    price: float

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    user_id: uuid.UUID

    class Config:
        orm_mode = True

# Base schema for charts that have both labels and values
class ChartResponse(BaseModel):
    labels: List[str]
    values: List[float]

# Specific schema for Active/Inactive users since it only has values
class ActiveInactiveUsersResponse(BaseModel):
    values: List[int]

# Aliases for different use cases (reusing the same structure for consistency)
AverageSessionDurationResponse = ChartResponse
RegistrationStatsResponse = ChartResponse
IncomeStatsResponse = ChartResponse
    
