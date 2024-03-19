from typing import Optional
from typing import List

from sqlalchemy import String, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class User(Base):
    uid: Mapped[str] = mapped_column("id", String, primary_key=True)
    email: Mapped[str] = mapped_column("email", String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(264))
    phone_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    roles: Mapped[List[str]] = mapped_column(String(264))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[List[str]] = mapped_column(String(264))
