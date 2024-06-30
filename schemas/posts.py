from pydantic import BaseModel
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
