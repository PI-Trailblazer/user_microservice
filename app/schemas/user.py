from re import L
from typing import Optional, List

from pydantic import BaseModel

from app.core.config import settings


class User(BaseModel):
    email: str
    f_name: str
    L_name: str
    phone_number: Optional[int]
    roles: List[str]
    verified: bool
    tags: List[str]
    image: str


class UserCreate(User):
    uid: str


class UserUpdate(User):
    f_name: Optional[str]
    l_name: Optional[str]
    phone_number: Optional[int]
    roles: Optional[List[str]]
    verified: Optional[bool]
    tags: Optional[List[str]]
    image: Optional[str]


class UserInDB(User):
    uid: str
