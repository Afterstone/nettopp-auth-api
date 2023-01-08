

import datetime as dt

import jose.exceptions as jose_exceptions

from auth_api import security


def test_can_has_and_verify():
    password = "test"
    hashed_password = security.hash_password(password)
    assert hashed_password != password
    assert security.verify_password(password, hashed_password)


def test_can_create_and_decode_token():
    data = {"test": "test"}
    token = security.create_jwt_token(data, dt.timedelta(minutes=15), "test")
    assert token != ""
    decoded = security.decode_jwt_token(token)

    assert decoded["test"] == "test"
    assert decoded["token_type"] == "test"
    assert decoded["jti"] != ""
    assert decoded["exp"] != ""
    assert decoded["exp"] > dt.datetime.now(dt.timezone.utc).timestamp()

    verified = security.verify_decode_access_token(token)
    # These dicts might not have the same reference, but the contents should be the same.
    assert verified == decoded


def test_decode_expired_token():
    data = {"test": "test"}
    token = security.create_jwt_token(data, dt.timedelta(minutes=-15), "test")
    assert token != ""
    try:
        security.verify_decode_access_token(token)
        assert False
    except jose_exceptions.ExpiredSignatureError:
        assert True
