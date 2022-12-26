import os

from dotenv import load_dotenv

load_dotenv()


def _get_envvar(name: str) -> str:
    var = os.getenv(name, None)
    if var is None:
        raise ValueError(f"Environment variable {name} not set.")
    return var


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


# Application config
VERBOSE: bool = _parse_bool(_get_envvar("VERBOSE"))

# Database
AUTH_DB_CONNECTION_STRING: str = _get_envvar("AUTH_DB_CONNECTION_STRING")

# JWT
JWT_SECRET_KEY: str = _get_envvar("JWT_SECRET_KEY")
JWT_ALGORITHM: str = "HS256"

# Server
HOST: str = _get_envvar("HOST")
PORT: int = int(_get_envvar("PORT"))
