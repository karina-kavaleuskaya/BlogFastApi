from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    topic_id: int
    content: str
    user_id: int

    class Config:
        from_attributes = True