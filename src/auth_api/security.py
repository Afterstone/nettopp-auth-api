from __future__ import annotations

import hashlib
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from .config import JWT_ALGORITHM, JWT_SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return str(pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    result: bool = pwd_context.verify(plain_password, hashed_password)
    return result


def create_jwt_token(
    data: dict[str, Any],
    expires_delta: timedelta,
    token_type: str
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode["exp"] = expire
    to_encode["token_type"] = token_type
    token: str = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict[str, Any]:
    data: dict[str, Any] = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    return data


def get_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


async def verify_decode_access_token(token: str) -> dict[str, Any]:
    data = decode_jwt_token(token)
    return data