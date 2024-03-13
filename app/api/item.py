from fastapi import APIRouter, HTTPException

router = APIRouter()

# This is an example delete whatever you deem necessary
@router.get("/example")
async def read_item():
    return {"message": "Hello World"}

