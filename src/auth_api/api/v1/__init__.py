from __future__ import annotations

import datetime as dt

import starlette.status as status
from fastapi import APIRouter, Depends, Form, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer
from jose.exceptions import ExpiredSignatureError
from pydantic import EmailStr
from pydantic.error_wrappers import ValidationError

from auth_api.database import Session, get_db
from auth_api.database.logic import (UserAlreadyExistsError,
                                     UserDoesNotExistError, create_user,
                                     get_user_by_email)
from auth_api.models import User
from auth_api.models.token import (ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE,
                                   AccessToken, RefreshToken, TokenPair)
from auth_api.security import (create_jwt_token, hash_password,
                               verify_decode_access_token, verify_password)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")


@router.get('/health')
async def health() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/register')
async def register(
    db: Session = Depends(get_db),
    email: str | None = Form(None),
    username: str | None = Form(None),
    password: str | None = Form(None),
) -> Response:
    if not (username and password and email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username, password or email.")

    try:
        user = User(
            username=username,
            email=EmailStr(email),
            password_hash=hash_password(password),
        )
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid value provided.")

    try:
        await create_user(db, user)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists.")

    return Response(status_code=status.HTTP_201_CREATED)


@router.post('/login')
async def login(
    db: Session = Depends(get_db),
    email: str | None = Form(None),
    password: str | None = Form(None),
) -> TokenPair:
    if not (email and password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing email or password.")

    try:
        user = await get_user_by_email(db, email)
    except UserDoesNotExistError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not isinstance(user.password_hash, str):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error.")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")

    access_token = AccessToken(
        token=create_jwt_token(
            data={
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
            },
            expires_delta=dt.timedelta(minutes=5),
            token_type=ACCESS_TOKEN_TYPE
        )
    )

    refresh_token = RefreshToken(
        token=create_jwt_token(
            data={
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
            },
            expires_delta=dt.timedelta(days=7),
            token_type=REFRESH_TOKEN_TYPE
        )
    )

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post('/refresh')
async def refresh(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> AccessToken:
    try:
        token_data = verify_decode_access_token(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    if token_data.get('token_type', None) != REFRESH_TOKEN_TYPE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    email = token_data.get('email', None)
    if email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email missing")

    try:
        user = await get_user_by_email(db, email)
    except UserDoesNotExistError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User is not active")

    access_token = AccessToken(
        token=create_jwt_token(
            data={
                "username": user.username,
                "email": user.email,
                "is_active": user.is_active,
                "is_superuser": user.is_superuser,
            },
            expires_delta=dt.timedelta(minutes=5),
            token_type=ACCESS_TOKEN_TYPE,
        )
    )

    return access_token
