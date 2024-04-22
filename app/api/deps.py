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
