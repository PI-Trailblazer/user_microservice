from enum import Enum
from datetime import datetime, date
from typing import Optional, List, Annotated

from pydantic import BaseModel

from app.core.config import settings



class User(BaseModel):
    email: str
    name: str
    phone: Optional[int]
    role: List[str]
    verified: bool
    tags: List[str]

class UserCreate(User):
    ...

class UserUpdate(User):
    name: Optional[str]
    phone: Optional[int]
    role: Optional[List[str]]
    verified: Optional[bool]
    tags: Optional[List[str]]

class UserInDB(User):
    id: str