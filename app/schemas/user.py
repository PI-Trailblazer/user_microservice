from enum import Enum
from re import L
from typing import Optional, List

from pydantic import BaseModel

from app.core.config import settings

from app.utils import ValidateFromJson


class ScopeEnum(str, Enum):
    """Permissions scopes"""

    USER = "user"
    PROVIDER = "provider"
    ADMIN = "admin"


class User(BaseModel):
    email: str
    f_name: str
    l_name: str
    phone_number: Optional[str]
    roles: List[str]
    verified: bool
    tags: List[str]


class UserCreate(User):
    uid: str
    roles: List[str] = []
    image: str


class UserUpdate(User, ValidateFromJson):
    f_name: Optional[str]
    l_name: Optional[str]
    phone_number: Optional[str]
    roles: Optional[List[str]]
    verified: Optional[bool]
    tags: Optional[List[str]]


class UserInDB(User):
    uid: str
    image: str
