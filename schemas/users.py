from pydantic import BaseModel, validator
from fastapi import HTTPException, status


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

    #@validator('email')
    #def email_must_be_valid(cls, v):
        #import re
        #if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v):
            #raise HTTPException(
                #status_code=status.HTTP_403_FORBIDDEN,
                #detail="Invalid email address"
            #)
        #return v



class User(UserBase):
    id: int


class UsersForAdmin(UserBase):
    banned_is: bool

