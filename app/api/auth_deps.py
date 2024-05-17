from urllib import request
from fastapi import Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response

from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError
from jose import JWTError, jwt
from datetime import datetime, timezone
from typing import Annotated, Any, Dict, List, Literal, Optional, Set, Union
from loguru import logger
from jwt.algorithms import RSAAlgorithm
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, SecurityScopes
import requests
from app.models.user import User
from app.models.device_login import DeviceLogin
from app.schemas.user import ScopeEnum
from app.core.config import settings
from app import crud

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


class FirebaseToken(HTTPBearer):
    def __init__(self, *, auto_error: bool = True):
        super().__init__(auto_error=auto_error)


class ProprietaryToken(HTTPBearer):
    def __init__(self, *, auto_error: bool = True):
        super().__init__(auto_error=auto_error)


secure = ProprietaryToken(auto_error=False)


class Token(BaseModel):
    access_token: str
    token_type: str


def create_token(payload: dict[str, Any]) -> str:
    encoded_jwt = jwt.encode(payload, private_key, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def verify_firebasetoken(token: str) -> dict[str, Any]:
    try:
        response = requests.get(
            "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
        )
        keys = response.json()
        unverified_header = jwt.get_unverified_header(token)
        key_id = unverified_header["kid"]

        if key_id not in keys:
            raise HTTPException(status_code=401, detail="Invalid token")

        decoded_token = jwt.get_unverified_claims(token)
        exp = decoded_token["exp"]
        iat = decoded_token["iat"]
        aud = decoded_token["aud"]
        iss = decoded_token["iss"]
        sub = decoded_token["sub"]
        auth_time = decoded_token["auth_time"]

        localtime = datetime.now(timezone.utc)

        if exp < localtime.timestamp():
            raise HTTPException(status_code=401, detail="Token has expired")
        if iat > localtime.timestamp():
            raise HTTPException(status_code=401, detail="Token issued in the future")
        if aud != settings.FIREBASE_PROJECT_ID:
            raise HTTPException(status_code=401, detail="Invalid audience")
        if iss != f"https://securetoken.google.com/{settings.FIREBASE_PROJECT_ID}":
            raise HTTPException(status_code=401, detail="Invalid issuer")
        if not sub:
            raise HTTPException(status_code=401, detail="Anonymous user")
        if auth_time > localtime.timestamp():
            raise HTTPException(status_code=401, detail="Invalid authentication time")

        return decoded_token
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Signature has expired")
    except jwt.JWTClaimsError:
        raise HTTPException(status_code=401, detail="Invalid token")


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
    cred: str = Depends(secure),
) -> Optional[AuthData]:
    if cred is None:
        return None
    token = cred.credentials
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
            user_id=user.uid,
            session_id=int(iat.timestamp()),
            refreshed_at=iat,
            expires_at=iat + settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        )
        db.add(device_login)
    else:
        device_login.refreshed_at = iat
        device_login.expires_at = iat + settings.ACCESS_TOKEN_EXPIRE_MINUTES

    db.commit()

    access_token = create_token(
        {
            "sub": user.uid,
            "name": f"{user.f_name} {user.l_name}",
            "scopes": user.roles,
            "tags": user.tags,
            "type": ACCESS_TOKEN_TYPE,
            "iat": iat,
            "exp": iat + settings.ACCESS_TOKEN_EXPIRE_MINUTES,
            "image": user.image,
        }
    )

    refresh_token = create_token(
        {
            "iat": iat,
            "exp": device_login.expires_at,
            "sub": user.uid,
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


def _validate_refresh_token(db, token):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Refresh"},
    )

    if token is None:
        raise credentials_exception

    try:
        payload = decode_token(token)
        print(payload)
        # Extract all needed fields inside a `try` in case a token
        # has a bad payload.
        user_id = payload["sub"]
        session_id = int(payload["sid"])
        issued_at = payload["iat"]
        token_type = payload["type"]
    except (JWTError, ValueError, KeyError):
        raise credentials_exception
    # Check that the token is a refresh token
    if token_type != REFRESH_TOKEN_TYPE:
        raise credentials_exception

    # Get the token's session from the database
    device_login = db.get(DeviceLogin, (user_id, session_id))
    if device_login is None:
        raise credentials_exception

    # Safety check that the session hasn't expired, the token should already
    # encode this.
    if device_login.expires_at < datetime.now():
        logger.warning(f"Token that should be expired was accepted")
        # Remove the device login from the database since it's no longer used
        db.delete(device_login)
        db.commit()

        raise credentials_exception

    # Check that this token issue date isn't before the last token refresh, if
    # this happens it might mean someone got the token and is trying to replay it
    if int(device_login.refreshed_at.timestamp()) > issued_at:
        logger.warning(f"A refresh token was resubmitted")
        # Preemptively remove the device login in order to prevent the token
        # from being used by a malicious third party.
        db.delete(device_login)
        db.commit()

        raise credentials_exception

    user = crud.user.get(db, user_id)
    if user is None:
        # The user no longer exists so the device login is no longer useful.
        db.delete(device_login)
        db.commit()

        raise credentials_exception

    return user, device_login


class OperationSuccess(BaseModel):
    status: Literal["success"] = "success"
    message: str
