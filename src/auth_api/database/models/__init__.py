import datetime as dt

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from ._base import Base


class AuthUser(Base):
    __tablename__ = 'auth_user'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password_hash = Column(String(128), nullable=False)

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    created_at = Column(DateTime, nullable=False, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, nullable=True, onupdate=dt.datetime.utcnow)

    def __repr__(self):
        return f"<User('{self.username}', '{self.email}')>"


__all__ = [
    'AuthUser',
    'Base'
]
