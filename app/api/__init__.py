from fastapi import APIRouter

from . import (
    user,
    item
)

router = APIRouter()

router.include_router(user.router, prefix="/user", tags=["user"])
router.include_router(item.router, prefix="/item", tags=["item"])
