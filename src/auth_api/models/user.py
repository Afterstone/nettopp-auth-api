import datetime as dt

from pydantic import BaseModel, EmailStr, validator


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

    # Validate username.
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        return v


class User(BaseUser):
    id: int | None = None
    password_hash: str | None = None

    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None
