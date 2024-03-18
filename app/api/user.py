from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from firebase_admin import auth
from typing import List, Optional

""" from app.api.deps import get_db """

router = APIRouter()


class RegisterData(BaseModel):
    roles: List[str]
    phone_number: Optional[str] = None


class AuthHeader(BaseModel):
    Authorization: str


@router.post("/api/register")
async def register_endpoint(*, user_in: RegisterData, headers: AuthHeader = Depends()):
    # Now you can access the data sent by the `register` function
    # data.roles, data.phone_number, headers.Authorization
    # Write your logic here
    print(user_in)
    print(headers)
    pass
