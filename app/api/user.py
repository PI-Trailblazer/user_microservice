from requests import Session
from app.api import deps
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import jwt

router = APIRouter()


class RegisterData(BaseModel):
    roles: List[str]
    phone_number: Optional[str] = None


class AuthHeader(BaseModel):
    Authorization: str


@router.post("/api/register")
async def register_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    user_in: RegisterData,
    headers: AuthHeader = Depends()
):
    # Now you can access the data sent by the `register` function
    # data.roles, data.phone_number, headers.Authorization
    # Write your logic here
    print(user_in)

    # Remove 'Bearer ' from the Authorization header
    id_token = headers.Authorization[7:]

    # Decode the JWT token
    try:
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    # Token is valid; now you can use the decoded_token
    uid = decoded_token["user_id"]
    email = decoded_token["email"]
    print(uid, email)
    pass
