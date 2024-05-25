import os
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from fastapi import UploadFile
from io import BytesIO
from app.exception import FileFormatException
from starlette.datastructures import UploadFile as StarletteUploadFile
from hashlib import md5
from PIL import Image, ImageOps
from loguru import logger


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):

    def update(
        self,
        db: Session,
        *,
        db_obj: User,
        obj_in: UserUpdate,
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        return super(CRUDUser, self).update(db, db_obj=db_obj, obj_in=update_data)

    async def update_image(
        self,
        db: Session,
        *,
        db_obj: User,
        image: UploadFile | bytes | None,
    ) -> User:
        img_path = None
        delete_old = image is None

        if image is not None:
            try:
                if isinstance(image, StarletteUploadFile):
                    image = await image.read()
                img_bytes = BytesIO(image)
                md5sum = md5(img_bytes.getbuffer())
                img = Image.open(img_bytes)
            except:
                raise FileFormatException()
            ext = img.format
            if ext not in ("JPEG", "PNG", "BMP"):
                raise FileFormatException(detail="Image format must be JPEG or PNG.")

            img = ImageOps.exif_transpose(img)
            img = img.convert("RGB")
            os.makedirs(f"static/user/users/{db_obj.uid}", exist_ok=True)
            img_path = f"/user/users/{db_obj.uid}/{md5sum.hexdigest()}.jpg"
            img.save(
                f"static{img_path}",
                format="JPEG",
                quality="web_high",
                optimize=True,
                progressive=True,
            )

            delete_old = img_path != db_obj.image

            if delete_old:
                try:
                    os.remove(f"static{db_obj.image}")
                except Exception as e:
                    logger.error(
                        f"Failed to delete profile picture for user {db_obj.uid}: {e}"
                    )

            setattr(db_obj, "image", f"/static{img_path}")
            db.add(db_obj)
            db.commit()
            return db_obj


user = CRUDUser(User)
