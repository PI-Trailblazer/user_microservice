from typing import Optional
from typing import List

from sqlalchemy import String, Integer, Boolean, Text, ARRAY
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY

from app.db.base_class import Base


class User(Base):
    uid: Mapped[str] = mapped_column("id", String(128), primary_key=True)
    email: Mapped[str] = mapped_column(
        "email", String(64), unique=True, index=True, nullable=False
    )
    f_name: Mapped[str] = mapped_column(String(32), nullable=False)
    l_name: Mapped[str] = mapped_column(String(32), nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String(14))
    roles: Mapped[List[str]] = mapped_column(
        MutableList.as_mutable(ARRAY(Text)), default=[], nullable=False
    )
    verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tags: Mapped[List[str]] = mapped_column(ARRAY(Text), default=[], nullable=False)

    image: Mapped[str] = mapped_column(String(2048), nullable=False)
