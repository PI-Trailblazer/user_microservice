from typing import Optional, List

from pydantic import BaseModel

from app.core.config import settings


class User(BaseModel):
    email: str
    name: str
    phone_number: Optional[int]
    roles: List[str]
    verified: bool
    tags: List[str]


class UserCreate(User):
    uid: str

class UserUpdate(User):
    name: Optional[str]
    phone_number: Optional[int]
    roles: Optional[List[str]]
    verified: Optional[bool]
    tags: Optional[List[str]]


class UserInDB(User):
    uid: str
