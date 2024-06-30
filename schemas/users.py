from pydantic import BaseModel
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



class User(UserBase):
    id: int


class UsersForAdmin(UserBase):
    banned_is: bool
