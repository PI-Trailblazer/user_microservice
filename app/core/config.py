import os
import pathlib

from datetime import timedelta
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Union


# Project Directories
ROOT = pathlib.Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

    PRODUCTION: bool = os.getenv("ENV") == "production"

    API_V1_STR: str = "/api"
    STATIC_STR: str = "/static"

    HOST: str = "www.google.pt" if PRODUCTION else "http://localhost"
    STATIC_URL: str = HOST + STATIC_STR
    # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    BACKEND_CORS_ORIGINS: List[str] = [HOST] + (
        [] if PRODUCTION else ["http://localhost:3000"]
    )

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # PostgreSQL DB
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "user_db_user"
    POSTGRES_PASSWORD: str = "user_db_password"
    POSTGRES_DB: str = "user_db"
    POSTGRES_URI: str = ""
    TEST_POSTGRES_URI: str = ""

    SCHEMA_NAME: str = "usr_microservice"

    @model_validator(mode="after")
    def populate_database_uris(self) -> "Settings":
        if self.POSTGRES_URI == "":
            self.POSTGRES_URI = (
                f"postgresql://{self.POSTGRES_USER}"
                f":{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}"
                f":5432/{self.POSTGRES_DB}"
            )

        if self.TEST_POSTGRES_URI == "":
            self.TEST_POSTGRES_URI = (
                f"postgresql://{self.POSTGRES_USER}"
                f":{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}"
                f":5432/{self.POSTGRES_DB}_test"
            )

        return self

    # Auth
    JWT_SECRET_KEY_PATH: str = "./dev-keys/jwt-key"
    JWT_PUBLIC_KEY_PATH: str = "./dev-keys/jwt-key.pub"
    ACCESS_TOKEN_EXPIRE_MINUTES: timedelta = timedelta(hours=1)
    REFRESH_TOKEN_EXPIRE_MINUTES: timedelta = timedelta(days=7)
    JWT_ALGORITHM: str = "RS256"

    # Firebase
    FIREBASE_PROJECT_ID: str = "trailblazerauth"


settings = Settings()
