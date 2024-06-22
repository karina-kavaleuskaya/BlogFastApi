from pydantic import BaseModel


class UserBase(BaseModel):
    email: str

    class Config:
        from_attributes = True


class UserCreate(UserBase):
    password:str
    first_name: str
    second_name: str
    nickname: str


class User(UserBase):
    id: int