from fastapi import FastAPI
from app.api import router as api_router 

app = FastAPI(
    title="User Microservice",
    description="This is a very fancy project, with auto docs for the API and everything",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api")
