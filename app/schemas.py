from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from .decorators import as_form
from pydantic.types import conint
from app.models import Payment


class EventBase(BaseModel):
    title: str
    content: str
    image_url: Optional[str] = None 
    status: bool = True
    space_allowed: int = 50
    space_available: int = 50 #space_allowed - len(BookingBase.space)
    # start_date: date = 2022/6/5
    # end_date: date = 2022/6/15
    cost: float = 00.00 

@as_form
class EventCreate(BaseModel):
    title: str
    content: str
    image_url: Optional[str]
    status: bool = True
    space_allowed: int = 50
    space_available: int = 50
    cost: float = 00.00 

@as_form
class EventUpdate(BaseModel):
    title: str
    content: str
    image_url: Optional[str]

class UserOut(BaseModel):
    id: int
    email: EmailStr
    image_url: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: int
    admin: Optional[bool] = False
    is_host: Optional[bool] = False
    created_at: datetime
    

    class Config:
        orm_mode = True

class EventResponse(EventBase):
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
    created_at: datetime
    event: EventResponse
    user: UserOut

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: EmailStr
    password: str
    image_url: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: int
    admin: Optional[bool] = False
    is_host: Optional[bool] = False

@as_form
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    image_url: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: int
    admin: Optional[bool] = False
    is_host: Optional[bool] = False

class UserTest(UserBase):
   pass

@as_form
class UserUpdate(BaseModel):
    password: Optional[str]
    image_url: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    phone_number: Optional[int]

    # for name, value in UserUpdate:
    #     return name

class UserResponse(UserBase):
    id: int
    created_at: datetime
    
       
    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class RequestReset(BaseModel):
    email: EmailStr

class EmailSchema(BaseModel):
    email: List[EmailStr]

class ResetPassword(BaseModel):
    password: str
    confirm_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
    admin: Optional[bool] = None

class TokenReset(Token):
    message: str

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

