from pydantic import BaseModel


class BaseToken(BaseModel):
    token: str
    token_type: str


class AccessToken(BaseToken):
    token_type: str = "access"


class RefreshToken(BaseToken):
    token_type: str = "refresh"


class TokenPair(BaseModel):
    access_token: AccessToken
    refresh_token: RefreshToken
