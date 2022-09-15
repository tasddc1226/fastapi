from pydantic import BaseModel, EmailStr
from pydantic.types import conint

from typing import Optional
from datetime import datetime


class User(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None


class Login(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    body: str


class Post(PostBase):
    id: int
    user_id: int
    created_at: datetime
    user: UserResponse

    class Config:
        orm_mode = True


class CreatePost(PostBase):
    pass


class PostLike(BaseModel):
    Post: Post
    likes: int

    class Config:
        orm_mode = True


class Like(BaseModel):
    post_id: int
    dir: conint(le=1)
