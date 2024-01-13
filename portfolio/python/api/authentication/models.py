from datetime import datetime
from uuid import uuid4

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, DateTime
from passlib import hash

from authentication.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        index=True,
    )
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    def verify_password(self, password: str):
        return hash.bcrypt.verify(password, self.password)
