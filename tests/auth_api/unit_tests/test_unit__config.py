from __future__ import annotations

import pytest

import auth_api.config as config


def test_can_get_envvar(monkeypatch):
    monkeypatch.setenv("TEST", "test")
    assert config._get_envvar("TEST") == "test"


def test_can_get_envvar_default(monkeypatch):
    monkeypatch.delenv("TEST", raising=False)
    assert config._get_envvar("TEST", "test") == "test"


def test_cant_get_envvar(monkeypatch):
    monkeypatch.delenv("TEST", raising=False)
    with pytest.raises(ValueError):
        config._get_envvar("TEST")


# def _parse_bool(
#     value: str | None,
#     true_strs: frozenset[str] = frozenset(["yes", "true", "t", "y", "1"]),
#     false_strs: frozenset[str] = frozenset(["no", "false", "f", "n", "0"]),
# ) -> bool:
#     if value is None:
#         raise ValueError("None is not a valid boolean string.")

#     value = value.strip().lower()
#     if value in true_strs:
#         return True
#     elif value in false_strs:
#         return False
#     else:
#         raise ValueError("Invalid value for boolean conversion.")

@pytest.mark.parametrize(
    "values, expected",
    [
        ([None], ValueError()),
        ([""], ValueError()),
        (["yes", "true", "t", "y", "1"], True),
        (["no", "false", "f", "n", "0"], False),
    ]
)
def test_can_parse_bool(values: list[str], expected: bool | Exception):
    if isinstance(expected, Exception):
        for value in values:
            with pytest.raises(type(expected)):
                config._parse_bool(value)
    else:
        for value in values:
            assert config._parse_bool(value) == expected
            assert config._parse_bool(value.upper()) == expected
            assert config._parse_bool(value.lower()) == expected
            assert config._parse_bool(value.capitalize()) == expected
