from datetime import datetime

from app.database.schema.schema import Base
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    email: Mapped[str] = Column(Text, unique=True, nullable=False)
    name: Mapped[str] = Column(Text, nullable=False)
    password_hash: Mapped[str] = Column(Text, nullable=True)
    timezone: Mapped[str] = Column(Text, nullable=False)
    created_at: Mapped[datetime] = Column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    last_login: Mapped[datetime] = Column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    last_active: Mapped[datetime] = Column(
        Date, nullable=False, default=datetime.utcnow
    )
    has_access: Mapped[bool] = Column(Boolean, nullable=False, default=False)
