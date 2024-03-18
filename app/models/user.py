from datetime import datetime
from typing import Optional
from typing import List

from sqlalchemy import ForeignKey, SmallInteger, String, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.ext.hybrid import hybrid_property

from app.core.config import settings
from app.db.base_class import Base
from app.models.user import User


class User(Base):
    id: Mapped[str] = mapped_column("id", String, primary_key=True)
    email: Mapped[str] = mapped_column("email", String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(264))
    phone: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    role: Mapped[List[str]] = mapped_column(String(264))
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    tags: Mapped[List[str]] = mapped_column(String(264))