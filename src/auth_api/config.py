import os

from dotenv import load_dotenv

load_dotenv()


def _parse_bool(
    value: str | None,
    true_strs: frozenset[str] = frozenset(["yes", "true", "t", "y", "1"]),
    false_strs: frozenset[str] = frozenset(["no", "false", "f", "n", "0"]),
) -> bool:
    if value is None:
        raise ValueError("None is not a valid boolean string.")

    value = value.strip().lower()
    if value in true_strs:
        return True
    elif value in false_strs:
        return False
    else:
        raise ValueError("Invalid value for boolean conversion.")


def _verify_auth_db_connection_string(
    string: str | None,
    required_keys: frozenset[str] = frozenset([
        "{AUTH_DB_USER}", "{AUTH_DB_PASSWORD}", "{AUTH_DB_DOMAIN}", "{DB_PORT}"]
    ),
) -> str:
    if string is None:
        raise ValueError("AUTH_DB_CONNECTION_STRING not set")

    return string


AUTH_DB_CONNECTION_STRING: str = _verify_auth_db_connection_string(os.getenv("AUTH_DB_CONNECTION_STRING", None))
VERBOSE: bool = _parse_bool(os.getenv("VERBOSE"))
