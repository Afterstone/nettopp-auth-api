import typing as t

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

from auth_api.config import AUTH_DB_CONNECTION_STRING, VERBOSE

ENGINE = create_engine(AUTH_DB_CONNECTION_STRING, echo=VERBOSE)

SessionMaker = sessionmaker(bind=ENGINE)

Base = declarative_base()


def get_db() -> t.Generator[Session, None, None]:
    session = SessionMaker()
    try:
        yield session
    finally:
        session.close()
