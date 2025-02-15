from datetime import datetime

from app.database.schema.schema import Base
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped


class RefreshToken(Base):
    __tablename__ = "user_refresh_tokens"
    id: Mapped[int] = Column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    token: Mapped[str] = Column(String, unique=True, index=True, nullable=False)
    device_info: Mapped[str] = Column(String)
    issued_at: Mapped[datetime] = Column(
        DateTime(timezone=True), default=datetime.utcnow
    )
    expires_at: Mapped[datetime] = Column(DateTime(timezone=True), nullable=False)
