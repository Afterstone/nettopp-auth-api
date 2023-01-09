from __future__ import annotations

import datetime as dt
import typing as t
from copy import deepcopy

import pytest
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from pydantic import EmailStr, ValidationError

import auth_api.api.v1 as api_v1
from auth_api.main import app
from auth_api.models.token import (ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE,
                                   AccessToken, TokenPair)
from auth_api.models.user import User
from auth_api.security import (create_jwt_token, hash_password,
                               verify_decode_access_token)


@pytest.fixture
def test_client() -> t.Generator[TestClient, None, None]:
    yield TestClient(app)


@pytest.mark.asyncio
async def test_can_get_health(test_client):
    response = test_client.get('/api/v1/health')
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.parametrize(
    'email, username, password, expected_status_code, expected_exception',
    [
        ('test@example.com', 'test', 'test', status.HTTP_201_CREATED, None),
        (None, 'test', 'test', status.HTTP_400_BAD_REQUEST, ValidationError),
        ('test', None, 'test', status.HTTP_400_BAD_REQUEST, ValidationError),
        ('test', 'test', None, status.HTTP_400_BAD_REQUEST, ValidationError),
        ('test', 'test', 'test', status.HTTP_400_BAD_REQUEST, HTTPException),  # Invalid email.
        ('test@example.com', 'exists', 'test', status.HTTP_409_CONFLICT, HTTPException),
        ('exists@example.com', 'exists', 'test', status.HTTP_409_CONFLICT, HTTPException),
    ]
)
@pytest.mark.asyncio
async def test_register(test_client, monkeypatch, email, username, password, expected_status_code, expected_exception):
    # Need to mock create_user.
    async def mock_create_user(db, user) -> None:
        if user.username == 'exists' or user.email == 'exists@example.com':
            raise api_v1.UserAlreadyExistsError
        return user
    monkeypatch.setattr(api_v1, 'create_user', mock_create_user)

    def mock_hash_password(password) -> str:
        return password
    monkeypatch.setattr(api_v1, 'hash_password', mock_hash_password)

    try:
        response = test_client.post("/api/v1/register", json={
            'email': email,
            'username': username,
            'password': password,
        })
        assert response.status_code == expected_status_code
    except Exception as e:
        if isinstance(e, AssertionError):
            raise e
        assert isinstance(e, expected_exception)


@pytest.mark.parametrize(
    'email, password, expected_status_code, expected_exception',
    [
        ('valid@example.com', 'test', status.HTTP_200_OK, None),
        (None, 'valid@example.com', status.HTTP_400_BAD_REQUEST, ValidationError),
        ('valid@example.com', None, status.HTTP_400_BAD_REQUEST, ValidationError),
        ('invalid', 'test', status.HTTP_401_UNAUTHORIZED, HTTPException),
        ('does_not_exist@example.com', 'test', status.HTTP_401_UNAUTHORIZED, HTTPException),
        ('valid@example.com', 'wrong_password', status.HTTP_401_UNAUTHORIZED, HTTPException),
        ('not_active@example.com', 'test', status.HTTP_401_UNAUTHORIZED, HTTPException),
    ]
)
@pytest.mark.asyncio
async def test_login(test_client, monkeypatch, email, password, expected_status_code, expected_exception):
    user = User(
        username='test',
        email=EmailStr("valid@example.com"),
        is_active=True,
        is_superuser=False,
        id=1,
        password_hash=hash_password('test'),
        created_at=None,
        updated_at=None,
    )
    non_active_user = deepcopy(user)
    non_active_user.is_active = False
    non_active_user.email = EmailStr('not_active@example.com')
    users = {
        "valid@example.com": user,
        "not_active@example.com": non_active_user,
    }

    async def mock_get_user_by_email(db, email) -> User:
        if email not in users:
            raise api_v1.UserDoesNotExistError
        return users[email]
    monkeypatch.setattr(api_v1, 'get_user_by_email', mock_get_user_by_email)

    try:
        response = test_client.post("/api/v1/login", json={
            'email': email,
            'password': password,
        })
        assert response.status_code == expected_status_code

        if str(expected_status_code)[0] == '2':
            token_pair = TokenPair(**response.json())

            assert isinstance(token_pair, TokenPair)
            assert token_pair.access_token
            at_decoded = verify_decode_access_token(token_pair.access_token.token)
            assert at_decoded['username'] == user.username
            assert at_decoded['email'] == user.email
            assert at_decoded['is_active'] == user.is_active
            assert at_decoded['is_superuser'] == user.is_superuser
            assert at_decoded['token_type'] == ACCESS_TOKEN_TYPE
            assert at_decoded['jti']

            assert token_pair.refresh_token
            rt_decoded = verify_decode_access_token(token_pair.refresh_token.token)
            assert rt_decoded['username'] == user.username
            assert rt_decoded['email'] == user.email
            assert rt_decoded['is_active'] == user.is_active
            assert rt_decoded['is_superuser'] == user.is_superuser
            assert rt_decoded['token_type'] == REFRESH_TOKEN_TYPE
            assert rt_decoded['jti']
    except Exception as e:
        if isinstance(e, AssertionError):
            raise e
        assert isinstance(e, expected_exception)


@pytest.mark.parametrize(
    'token_data, expires_delta, token_type, expected_status_code, expected_exception',
    [
        ({"email": "valid@example.com"}, dt.timedelta(minutes=5), REFRESH_TOKEN_TYPE, status.HTTP_200_OK, None),
        ({"email": "valid@example.com"}, dt.timedelta(minutes=-5), REFRESH_TOKEN_TYPE, status.HTTP_401_UNAUTHORIZED, None),  # noqa: E501
        ({"email": "valid@example.com"}, dt.timedelta(minutes=5), ACCESS_TOKEN_TYPE, status.HTTP_401_UNAUTHORIZED, None),  # noqa: E501
        ({"test": "test"}, dt.timedelta(minutes=5), REFRESH_TOKEN_TYPE, status.HTTP_400_BAD_REQUEST, None),
        ({"email": "does_not_exists@example.com"}, dt.timedelta(minutes=5), REFRESH_TOKEN_TYPE, status.HTTP_401_UNAUTHORIZED, None),  # noqa: E501
        ({"email": "not_active@example.com"}, dt.timedelta(minutes=5), REFRESH_TOKEN_TYPE, status.HTTP_401_UNAUTHORIZED, None),  # noqa: E501
    ]
)
@pytest.mark.asyncio
async def test_refresh_token(
    test_client,
    monkeypatch,
    token_data,
    expires_delta,
    token_type,
    expected_status_code,
    expected_exception
):
    user = User(
        username='test',
        email=EmailStr("valid@example.com"),
        is_active=True,
        is_superuser=False,
        id=1,
        password_hash='test',
        created_at=None,
        updated_at=None,
    )
    non_active_user = deepcopy(user)
    non_active_user.is_active = False
    non_active_user.email = EmailStr('not_active@example.com')
    users = {
        "valid@example.com": user,
        "not_active@example.com": non_active_user,
    }

    async def mock_get_user_by_email(db, email) -> User:
        if email not in users:
            raise api_v1.UserDoesNotExistError
        return users[email]
    monkeypatch.setattr(api_v1, 'get_user_by_email', mock_get_user_by_email)

    token = create_jwt_token(
        data=token_data,
        expires_delta=expires_delta,
        token_type=token_type,
    )

    try:
        response = test_client.post("/api/v1/refresh", headers={"authorization": f"Bearer {token}"})
        assert response.status_code == expected_status_code

        if str(expected_status_code)[0] == '2':
            result = AccessToken(**response.json())

            assert isinstance(result, AccessToken)
            decoded = verify_decode_access_token(result.token)
            for key in token_data:
                assert decoded[key] == token_data[key]
    except Exception as e:
        if isinstance(e, AssertionError):
            raise e
        assert isinstance(e, expected_exception)
