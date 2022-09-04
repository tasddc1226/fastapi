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