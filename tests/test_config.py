"""Tests for server configuration and token security."""

import os
from unittest import mock

from pydantic import SecretStr

from github_mcp.config import ServerConfig


def test_server_config_defaults():
    config = ServerConfig()
    assert config.github_api_url == "https://api.github.com"
    assert config.request_timeout == 20.0
    assert not config.has_token
    assert config.get_token_value() is None


def test_server_config_with_token():
    config = ServerConfig(github_token=SecretStr("ghp_1234567890abcdef"))
    assert config.has_token
    assert config.get_token_value() == "ghp_1234567890abcdef"


def test_token_never_leaked_in_repr_or_str():
    raw_token = "ghp_super_secret_token_value_987654321"
    config = ServerConfig(github_token=SecretStr(raw_token))

    config_str = str(config)
    config_repr = repr(config)

    assert raw_token not in config_str
    assert raw_token not in config_repr
    assert "hidden" in config_str
    assert "hidden" in config_repr


def test_get_headers_with_and_without_token():
    # Without token
    config_no_token = ServerConfig()
    headers_no_token = config_no_token.get_headers()
    assert "Authorization" not in headers_no_token
    assert headers_no_token["Accept"] == "application/vnd.github+json"

    # With token
    token = "ghp_test_token_12345"
    config_token = ServerConfig(github_token=SecretStr(token))
    headers_token = config_token.get_headers()
    assert "Authorization" in headers_token
    assert headers_token["Authorization"] == f"Bearer {token}"


def test_config_from_env():
    with mock.patch.dict(
        os.environ,
        {
            "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_env_token_abcdef",
            "GITHUB_API_URL": "https://api.github.com/",
            "GITHUB_REQUEST_TIMEOUT": "15.5",
        },
    ):
        config = ServerConfig.from_env()
        assert config.has_token
        assert config.get_token_value() == "ghp_env_token_abcdef"
        assert config.github_api_url == "https://api.github.com"
        assert config.request_timeout == 15.5
