from pydantic import BaseModel, field_validator
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    title: str
    topic_id: int | None
    content: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PostCreate(PostBase):
    pass


class Post(PostBase):
    id:int


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    topic_id: int | None
    file_path: str | None
    created_at: datetime

    @field_validator('title')
    @classmethod
    def title_must_not_exceed_10000_chars(cls, v):
        if len(v) > 300:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Content must not exceed 300 characters'
            )
        return v


    @field_validator('content')
    @classmethod
    def content_must_not_exceed_10000_chars(cls, v):
        if len(v) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Content must not exceed 10,000 characters'
            )
        return v

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    last_viewed_at: datetime
    next_page: Optional[str]
    prev_page: Optional[str]


