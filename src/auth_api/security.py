from __future__ import annotations

import datetime as dt
import hashlib
import uuid
from typing import Any

from jose import jwt
from passlib.context import CryptContext

from .config import JWT_ALGORITHM, JWT_SECRET_KEY

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
    token: str = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def decode_jwt_token(token: str) -> dict[str, Any]:
    data: dict[str, Any] = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])

    # Check the exp.
    exp_raw = data.get("exp", None)
    # We have to decode the exp.
    if exp_raw is None:
        raise ValueError("There is no exp in the token.")
    exp: dt.datetime = dt.datetime.fromtimestamp(exp_raw, tz=dt.timezone.utc)
    if exp < dt.datetime.now(dt.timezone.utc):
        raise ValueError("The token is expired.")

    return data


def get_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode('utf-8')).hexdigest()


async def verify_decode_access_token(token: str) -> dict[str, Any]:
    data = decode_jwt_token(token)
    return data
