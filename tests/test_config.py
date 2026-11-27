"""Tests for server configuration, token cleanup, and credential security."""

import os
from unittest import mock

from pydantic import SecretStr

from github_mcp.config import PROJECT_ROOT, ServerConfig


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


def test_token_strips_quotes_and_whitespace():
    with mock.patch.dict(
        os.environ,
        {"GITHUB_PERSONAL_ACCESS_TOKEN": '  "ghp_token_with_quotes"  '},
        clear=True,
    ):
        config = ServerConfig.from_env()
        assert config.has_token
        assert config.get_token_value() == "ghp_token_with_quotes"


def test_github_token_fallback():
    with mock.patch.dict(
        os.environ,
        {"GITHUB_TOKEN": "ghp_classic_fallback_token"},
        clear=True,
    ):
        config = ServerConfig.from_env()
        assert config.has_token
        assert config.get_token_value() == "ghp_classic_fallback_token"


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


def test_project_root_identified():
    assert PROJECT_ROOT.exists()
    assert (PROJECT_ROOT / "pyproject.toml").exists()


def test_placeholder_token_ignored():
    with mock.patch.dict(
        os.environ,
        {"GITHUB_PERSONAL_ACCESS_TOKEN": "your_github_personal_access_token_here"},
        clear=True,
    ):
        config = ServerConfig.from_env()
        assert not config.has_token
        assert config.get_token_value() is None


def test_safe_configuration_status_and_logging_never_leak_token():
    secret_token = "ghp_super_secret_never_leak_this_token_9999"
    config = ServerConfig(github_token=SecretStr(secret_token))

    from github_mcp.config import get_configuration_status, log_startup_configuration

    status = get_configuration_status(config)
    assert status["token_configured"] is True
    assert "5,000" in status["rate_limit_tier"]
    # Secret must not appear in any value of status dict
    for key, value in status.items():
        assert secret_token not in str(value)

    # Test logger output
    import logging

    test_logger = logging.getLogger("test_security_logger")
    log_messages = []

    class CapturingHandler(logging.Handler):
        def emit(self, record):
            log_messages.append(record.getMessage())

    handler = CapturingHandler()
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)

    try:
        log_startup_configuration(config=config, log=test_logger)
        all_logs = "\n".join(log_messages)
        assert "Authentication: CONFIGURED" in all_logs
        assert "5,000 requests/hour" in all_logs
        assert secret_token not in all_logs, "CRITICAL: Secret token leaked into startup log!"
    finally:
        test_logger.removeHandler(handler)
