from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from auth_api.config import AUTH_DB_CONNECTION_STRING, VERBOSE

ENGINE = create_engine(AUTH_DB_CONNECTION_STRING, echo=VERBOSE)

Session = sessionmaker(bind=ENGINE)
