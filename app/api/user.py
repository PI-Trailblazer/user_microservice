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
    first_name: str
    last_name: str
    email: str
    roles: List[str]
    phone: Optional[str] = None
    tags: List[str]




@router.post("/register")
async def register_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    user_in: RegisterData,
    headers: deps.AuthHeader = Depends(deps.get_auth_header)
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

    userin = UserCreate(
        uid=uid,
        email=user_in.email,
        roles=user_in.roles,
        phone_number=user_in.phone,
        tags=user_in.tags,
        f_name=user_in.first_name,
        l_name=user_in.last_name,
        verified=False if "PROVIDER" in user_in.roles else True,
        image="",
    )

    # Create the user in the database
    return crud.user.create(db, obj_in=userin)


@router.post("/login")
async def get_user_by_token(
    db: Session = Depends(deps.get_db), headers: deps.AuthHeader = Depends(deps.get_auth_header)
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

@router.get("/{user_id}")
async def get_user_by_id(
    user_id: str,
    db: Session = Depends(deps.get_db)
    ):
    user = crud.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user