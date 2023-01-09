from __future__ import annotations

import datetime as dt
import hashlib
import uuid
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from .config import JWT_ALGORITHM, JWT_PRIVATE_KEY, JWT_PUBLIC_KEY

PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return str(PWD_CONTEXT.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    result: bool = PWD_CONTEXT.verify(plain_password, hashed_password)
    return result


def create_jwt_token(
    data: dict[str, Any],
    expires_delta: dt.timedelta,
    token_type: str
) -> str:
    to_encode = data.copy()
    expire = dt.datetime.now(dt.timezone.utc) + expires_delta
    to_encode["exp"] = expire
    to_encode["jti"] = str(uuid.uuid4())
    to_encode["token_type"] = token_type
    token: str = jwt.encode(to_encode, JWT_PRIVATE_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict[str, Any]:
    data: dict[str, Any] = jwt.decode(token, JWT_PUBLIC_KEY, algorithms=[JWT_ALGORITHM])
    return data


def get_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


def verify_decode_access_token(token: str) -> dict[str, Any]:
    data = decode_jwt_token(token)

    # TODO: Should check JTI here to make sure it's not been used before.

    return data
