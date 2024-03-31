from contextlib import asynccontextmanager

from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from app.db.init_db import init_db
from fastapi import FastAPI
from app.api import router as api_router 
from app.core.config import settings

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="User Microservice",
    lifespan=lifespan,
    description="This is a very fancy project, with auto docs for the API and everything",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router, prefix="/api")
