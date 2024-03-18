from contextlib import asynccontextmanager

from app.db.init_db import init_db
from fastapi import FastAPI
from app.api import router as api_router 

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

app.include_router(api_router, prefix="/api")
