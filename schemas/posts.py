from pydantic import BaseModel, validator
from fastapi import HTTPException, status
from typing import Optional
from datetime import datetime


class PostBase(BaseModel):
    title: str
    topic_id: int
    content: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

    @validator('topic_id')
    def topic_id_must_be_valid(cls, v):
        if v is not None and not isinstance(v, int):
            raise ValueError('topic_id must be an integer or None')
        return v

    @validator('content')
    def content_must_not_exceed_10000_chars(cls, v):
        if len(v) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Content must not exceed 10,000 characters'
            )
        return v

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

    @validator('content')
    def content_must_not_exceed_10000_chars(cls, v):
        if len(v) > 10000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Content must not exceed 10,000 characters'
            )
        return v

    @validator('title')
    def content_must_not_exceed_10000_chars(cls, v):
        if len(v) > 300:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Content must not exceed 300 characters'
            )
        return v


class PaginationInfo(BaseModel):
    last_viewed_at: datetime
    next_page: Optional[str]
    prev_page: Optional[str]


class TopicBase(BaseModel):
    title: str


class TopicCreate(TopicBase):
    pass


class Topic(TopicBase):
    id: int

    class Config:
        from_attributes = True
