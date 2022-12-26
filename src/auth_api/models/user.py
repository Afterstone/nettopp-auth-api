import datetime as dt

from pydantic import BaseModel


class BaseUser(BaseModel):
    username: str
    email: str
    is_active: bool = True
    is_superuser: bool = False


class User(BaseUser):
    id: int | None = None
    password_hash: str | None = None

    created_at: dt.datetime | None = None
    updated_at: dt.datetime | None = None
