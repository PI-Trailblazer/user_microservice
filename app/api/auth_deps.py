from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi.responses import JSONResponse, Response

from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, ValidationError
from jose import JWTError, jwt
from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Literal, Optional, Set, Union
from loguru import logger

from app.models.user import User
from app.models.device_login import DeviceLogin
from app.schemas.user import ScopeEnum
from app.core.config import settings


ACCESS_TOKEN_TYPE: str = "access"
REFRESH_TOKEN_TYPE: str = "refresh"

with open(settings.JWT_SECRET_KEY_PATH) as f:
    private_key = f.read()

with open(settings.JWT_PUBLIC_KEY_PATH) as f:
    public_key = f.read()

auth_response: Dict[Union[int, str], Dict[str, Any]] = {
    401: {"description": "Not Authenticated"},
    403: {"description": "Not Authorized"},
}

oauth2_scheme = OAuth2PasswordBearer(
    auto_error=False,
    tokenUrl=f"{settings.API_V1_STR}/login/",
    scopes={
        ScopeEnum.ADMIN: "Admin users",
        ScopeEnum.PROVIDER: "Provider users",
        ScopeEnum.USER: "Regular users",
    },
)


class Token(BaseModel):
    access_token: str
    token_type: str


def create_token(payload: dict[str, Any]) -> str:
    encoded_jwt = jwt.encode(payload, private_key, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        public_key,
        algorithms=[settings.JWT_ALGORITHM],
        options={
            "require_exp": True,
            "require_iat": True,
            "require_sub": True,
        },
    )


class AuthData(BaseModel):
    sub: str
    name: str
    scopes: List[str]
    tags: List[str]


async def get_auth_data(
    token: str = Depends(oauth2_scheme),
) -> Optional[AuthData]:
    if token is None:
        return None

    try:
        payload = decode_token(token)
        token_type = payload["type"]
    except JWTError:
        return None

    if token_type != ACCESS_TOKEN_TYPE:
        return None

    try:
        auth_data = AuthData(**payload)
    except ValidationError as e:
        logger.debug(e)
        return None

    return auth_data


GetAuthData = Annotated[Optional[AuthData], Depends(get_auth_data)]


async def verify_token(
    security_scopes: SecurityScopes, auth_data: GetAuthData
) -> AuthData:
    """Dependency for user authentication"""
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    if auth_data is None:
        raise credentials_exception

    # Bypass scopes for admin
    if ScopeEnum.ADMIN in auth_data.scopes:
        return auth_data

    # Verify that the token has all the necessary scopes
    for scope in security_scopes.scopes:
        if scope not in auth_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    return auth_data


def generate_response(
    db: Session,
    user: User,
    device_login: DeviceLogin | None = None,
) -> Response:

    iat = datetime.now(timezone.utc)

    if device_login is None:
        device_login = DeviceLogin(
            user_id=user.id,
            session_id=int(iat.timestamp()),
            refreshed_at=iat,
            expires_at=iat + settings.ACCESS_TOKEN_EXPIRE,
        )
        db.add(device_login)
    else:
        device_login.refreshed_at = iat
        device_login.expires_at = iat + settings.ACCESS_TOKEN_EXPIRE

    db.commit()

    access_token = create_token(
        {
            "sub": user.id,
            "name": f"{user.f_name} {user.l_name}",
            "scopes": user.roles,
            "tags": user.tags,
            "type": ACCESS_TOKEN_TYPE,
            "iat": iat,
            "exp": iat + settings.ACCESS_TOKEN_EXPIRE,
        }
    )

    refresh_token = create_token(
        {
            "iat": iat,
            "exp": device_login.expires_at,
            "sub": user.id,
            "type": REFRESH_TOKEN_TYPE,
            "sid": device_login.session_id,
        }
    )

    token_data = Token(access_token=access_token, token_type="bearer")
    response = JSONResponse(content=token_data.model_dump())
    response.set_cookie(
        key="refresh",
        value=refresh_token,
        expires=device_login.expires_at.astimezone(timezone.utc),
        httponly=True,
        secure=settings.PRODUCTION,
        samesite="strict",
    )
    return response


class OperationSuccess(BaseModel):
    status: Literal["success"] = "success"
    message: str
