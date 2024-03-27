from requests import Session
from app.api import deps
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import jwt
from app import crud
from app.schemas import UserCreate

router = APIRouter()


class RegisterData(BaseModel):
    roles: List[str]
    f_name: str
    l_name: str
    phone_number: Optional[int] = None


class AuthHeader(BaseModel):
    Authorization: str


@router.post("/register")
async def register_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    user_in: RegisterData,
    headers: AuthHeader = Depends()
):
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

    userin = UserCreate(
        uid=uid,
        email=email,
        f_name=user_in.f_name,
        L_name=user_in.l_name,
        roles=user_in.roles,
        phone_number=user_in.phone_number,
        tags=[],
        image="",
        verified=False if "PROVIDER" in user_in.roles else True,
    )

    # Create the user in the database
    return crud.user.create(db, obj_in=userin)


@router.post("/login")
async def get_user_by_token(
    db: Session = Depends(deps.get_db), headers: AuthHeader = Depends()
):
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

    # Get the user from the database
    user = crud.user.get(db, id=uid)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
