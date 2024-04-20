from sqlalchemy.exc import SQLAlchemyError
from app.db.session import SessionLocal
from fastapi import HTTPException, Request
from pydantic import BaseModel, Field

# Dependency that sets up a database transaction for each request


def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()


class AuthHeader(BaseModel):
    Authorization: str = Field(..., alias="Authorization")


def get_auth_header(request: Request):
    authorization: str = request.headers.get("Authorization", None)
    if not authorization:
        raise HTTPException(status_code=400, detail="Authorization header is missing")
    return AuthHeader(Authorization=authorization)
