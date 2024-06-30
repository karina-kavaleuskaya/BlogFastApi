from pydantic import BaseModel, validator
from typing import Optional
import datetime


class UserBase(BaseModel):
    email: str
    first_name: str
    second_name: str
    nickname: str
    sex_id: int
    country_id: int


    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password:str

    @validator('email')
    def email_must_be_valid(cls, v):
        if not isinstance(v, str) or '@' not in v:
            raise ValueError('email must be a valid email address')
        return v



class User(UserBase):
    id: int


class UsersForAdmin(UserBase):
    banned_is: bool
