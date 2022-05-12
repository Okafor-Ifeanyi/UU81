from dataclasses import fields
from typing import Optional
from unittest.mock import Base
from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from pydantic.types import conint

from app.models import Payment

class EventBase(BaseModel):
    title: str
    content: str
    status: bool = True
    space_allowed: int = 50
    space_available: int = 50 #space_allowed - len(BookingBase.space)
    # start_date: date = 2022/6/5
    # end_date: date = 2022/6/15
    cost: float = 00.00

class EventCreate(EventBase):
    pass

class UserOut(BaseModel):
    id: int
    email: EmailStr
    phone_number: int
    created_at: datetime

    class Config:
        orm_mode = True

class EventResponse(BaseModel):
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut
       
    class Config:
        orm_mode = True

class EventOut(BaseModel):
    Event: EventResponse
    Booking: int

    class Config:
        orm_mode = True

class BookingResponse(BaseModel):
    id: int
    event: EventOut
    user: UserOut

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr
    password: str
    phone_number: int
    admin: bool = False
    is_host: bool = False

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    admin: bool
    is_host: bool 

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
       
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
    admin: Optional[bool] = None


class Booking(BaseModel):
    event_id: int = None
    dir: conint(le=1) 
    space: int = 1

class BookingGetUsers(BaseModel):
    user_id: int 

class BookingGetEvents(BaseModel):
    event_id: int 

class PaymentBase(BaseModel):
    class Meta:
        model = Payment
        fields = ("amount", "email")


# class BookingCreate(BookingBase):
#     pass

