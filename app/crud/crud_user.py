import os
from io import BytesIO
from hashlib import md5
from datetime import datetime
from typing import Optional, Union, Any, Dict

import magic
from loguru import logger
from PIL import Image, ImageOps
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi import UploadFile
from fastapi.encoders import jsonable_encoder
from starlette.datastructures import UploadFile as StarletteUploadFile

from app.exception import FileFormatException
from app.crud.base import CRUDBase
from app.models.user import User, UserEmail
from app.schemas.user import UserCreate, UserUpdate
from app.core.config import settings
from app.api.api_v1.auth._deps import hash_password

mime = magic.Magic(mime=True)


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]): ...
