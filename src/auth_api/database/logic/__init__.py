

import datetime as dt

from psycopg2.errors import UniqueViolation
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session

from auth_api.database.models import AuthUser
from auth_api.models.user import User


class SqlError(Exception):
    pass


class UserAlreadyExistsError(SqlError):
    pass


class UserDoesNotExistError(SqlError):
    pass


async def _get_user_by_predicate(db: Session, predicate) -> User:
    auth_user = db.query(AuthUser).filter(predicate).first()
    if auth_user is None:
        raise UserDoesNotExistError()

    return User(
        id=auth_user.id,
        username=auth_user.username,
        email=EmailStr(auth_user.email),
        password_hash=auth_user.password_hash,
        is_superuser=auth_user.is_superuser,
        is_active=auth_user.is_active,
        created_at=auth_user.created_at,
        updated_at=auth_user.updated_at,
    )


async def get_user_by_email(db: Session, email: str) -> User:
    return await _get_user_by_predicate(db, AuthUser.email == email)


async def get_user_by_username(db: Session, username: str) -> User:
    return await _get_user_by_predicate(db, AuthUser.username == username)


async def get_user_by_id(db: Session, user_id: int) -> User:
    return await _get_user_by_predicate(db, AuthUser.id == user_id)


async def create_user(db: Session, user: User) -> None:
    try:
        db_user = AuthUser(
            username=user.username,
            email=str(user.email),
            password_hash=user.password_hash,
            is_superuser=user.is_superuser,
            is_active=user.is_active,
            created_at=dt.datetime.utcnow(),
        )
        db.add(db_user)
        db.commit()
    except IntegrityError as ie:
        db.rollback()
        if isinstance(ie.orig, UniqueViolation):
            raise UserAlreadyExistsError()
        else:
            raise ie
    except Exception as e:
        db.rollback()
        raise e
