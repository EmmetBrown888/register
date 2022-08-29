from datetime import date
from pydantic import BaseModel


class User(BaseModel):
    email: str
    phone: str
    birthday: date
    password: str


class UserCreate(User):
    pass


class UserCode(BaseModel):
    code: str
    phone: str


class UserResend(BaseModel):
    phone: str
