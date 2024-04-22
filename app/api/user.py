from requests import Session
from app.api import deps, auth_deps
from fastapi import APIRouter, Depends, HTTPException, Security, Cookie, Response
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
from jose import JWTError, jwt
from app import crud
from app.schemas import UserCreate

from app.schemas.user import ScopeEnum, UserInDB

router = APIRouter()


class RegisterData(BaseModel):
    first_name: str
    last_name: str
    email: str
    roles: List[str]
    phone: Optional[str] = None
    tags: List[str]


bearer_scheme = auth_deps.FirebaseToken(auto_error=False)


@router.post(
    "/register",
    response_model=auth_deps.Token,
    responses={
        401: {"description": "Invalid token"},
        400: {"description": "User already exists"},
    },
)
async def register_endpoint(
    *,
    db: Session = Depends(deps.get_db),
    user_in: RegisterData,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    # Remove 'Bearer ' from the Authorization header
    id_token = credentials.credentials

    # Decode the JWT token
    decoded_token = auth_deps.verify_firebasetoken(id_token)

    # Token is valid; now you can use the decoded_token
    uid = decoded_token["user_id"]

    maybe_user = crud.user.get(db, id=uid)

    if maybe_user is not None:
        raise HTTPException(status_code=400, detail="User already exists")

    roles = ["admin"]
    print(roles)
    userin = UserCreate(
        uid=uid,
        email=user_in.email,
        roles=roles,
        phone_number=user_in.phone,
        tags=user_in.tags,
        f_name=user_in.first_name,
        l_name=user_in.last_name,
        verified=False if "provider" in user_in.roles else True,
        image="",
    )

    user = crud.user.create(db, obj_in=userin)

    # Create the user in the database
    return auth_deps.generate_response(db, user)


@router.post(
    "/login",
    response_model=auth_deps.Token,
    responses={
        401: {"description": "Invalid token"},
        400: {"description": "User already exists"},
    },
)
async def get_user_by_token(
    db: Session = Depends(deps.get_db),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    # Remove 'Bearer ' from the Authorization header
    id_token = credentials.credentials

    # Decode the JWT token
    decoded_token = auth_deps.verify_firebasetoken(id_token)

    # Token is valid; now you can use the decoded_token
    uid = decoded_token["user_id"]
    # Get the user from the database
    user = crud.user.get(db, id=uid)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return auth_deps.generate_response(db, user)


@router.get("/{user_id}")
async def get_user_by_id(user_id: str, db: Session = Depends(deps.get_db)):
    user = crud.user.get(db, id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", status_code=200, responses=auth_deps.auth_response)
async def get_users(
    *,
    db: Session = Depends(deps.get_db),
    auth_data: auth_deps.AuthData = Security(
        auth_deps.verify_token, scopes=[ScopeEnum.ADMIN]
    ),
) -> List[UserInDB]:
    users = crud.user.get_multi(db)
    print(auth_data)
    return users


@router.post(
    "/logout",
    responses={401: {"description": "Invalid refresh token"}},
    response_model=auth_deps.OperationSuccess,
)
async def logout(
    response: Response,
    db: Session = Depends(deps.get_db),
    refresh: str | None = Cookie(default=None),
):
    # remove the refresh token cookie from the client
    response.delete_cookie("refresh")

    _, device_login = auth_deps._validate_refresh_token(db, refresh)

    # invalidate the user's token and clear it from the server-side
    db.delete(device_login)
    db.commit()

    return auth_deps.OperationSuccess(
        status="success", message="You have been logged out."
    )


@router.post(
    "/refresh",
    responses={401: {"description": "Invalid refresh token"}},
    response_model=auth_deps.Token,
)
async def refresh(
    db: Session = Depends(deps.get_db), refresh: str | None = Cookie(default=None)
):
    user, device_login = auth_deps._validate_refresh_token(db, refresh)
    return auth_deps.generate_response(db, user, device_login)
