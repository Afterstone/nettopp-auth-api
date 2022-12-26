from pydantic import BaseModel

ACCESS_TOKEN_TYPE = "access"  # nosec B105
REFRESH_TOKEN_TYPE = "refresh"  # nosec B105


class BaseToken(BaseModel):
    token: str


class AccessToken(BaseToken):
    pass


class RefreshToken(BaseToken):
    pass


class TokenPair(BaseModel):
    access_token: AccessToken
    refresh_token: RefreshToken
