import pytest

from auth_api.main import root


@pytest.mark.asyncio
async def test_root():
    assert (await root()) == {"message": "Hello Worlds"}
