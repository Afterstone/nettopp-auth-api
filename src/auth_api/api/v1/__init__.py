import datetime as dt

import starlette.status as status
from fastapi import APIRouter, Depends, Form, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose.exceptions import ExpiredSignatureError

from auth_api.database import Session, get_db
from auth_api.database.logic import (UserAlreadyExistsError,
                                     UserDoesNotExistError, create_user,
                                     get_user_by_username)
from auth_api.models import User
from auth_api.models.token import (ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE,
                                   AccessToken, RefreshToken, TokenPair)
from auth_api.security import (create_jwt_token, hash_password,
                               verify_decode_access_token, verify_password)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


# async def get_current_user(
#     token: str = Depends(oauth2_scheme)
# ) -> User:
#     try:
#         token_data = await verify_decode_access_token(token)
#     except ExpiredSignatureError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
#     username = token_data.get('username', None)
#     if not username:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username missing")
#     try:
#         user = await get_user_by_username(db, username)
#     except UserDoesNotExistError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
#     return user


@router.get('/health')
async def health() -> Response:
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post('/register')
async def register(
    db: Session = Depends(get_db),
    email: str | None = Form(None),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Response:
    username = form_data.username
    password = form_data.password
    if not (username and password and email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing username, password or email.")

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
    )

    try:
        await create_user(db, user)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists.")

    return Response(status_code=status.HTTP_201_CREATED)


@router.post('/login')
async def login(
    db: Session = Depends(get_db),
    email: str | None = Form(None),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> TokenPair:
    password = form_data.password

    if not (email and password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing email or password.")

    try:
        user = await get_user_by_username(db, email)
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
        token_data = await verify_decode_access_token(token)
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    if token_data.get('token_type', None) != REFRESH_TOKEN_TYPE:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    try:
        user = await get_user_by_username(db, token_data.get('username', None))
    except UserDoesNotExistError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

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