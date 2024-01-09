from uuid import UUID
from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str
    password: str

    class Config:
        from_attributes=True


class User(UserCreate):
    id: UUID
    created_at: datetime
    updated_at: datetime

