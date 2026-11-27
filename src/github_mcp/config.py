"""Configuration and credential management for GitHub MCP Server.

Ensures tokens are reliably loaded from project root .env and environment variables,
and guarantees secrets are never leaked in representations, logs, or error responses.
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr

logger = logging.getLogger(__name__)

# Determine canonical project root (directory containing pyproject.toml and .env)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Placeholders from templates that should not be treated as real tokens
_TOKEN_PLACEHOLDERS = {
    "",
    "your_github_personal_access_token_here",
    "ghp_your_token_here",
    "your_token_here",
    "<your_token_here>",
    "your_personal_access_token",
}


def load_env_files(override: bool = False) -> Optional[Path]:
    """Find and load .env from canonical project root or current working directory.

    Args:
        override: If True, values from .env overwrite existing environment variables.
            Defaults to False so explicit CLI or test environment variables are preserved.

    Returns:
        The Path to the loaded .env file, or None if not found.
    """
    if not override and (
        "GITHUB_PERSONAL_ACCESS_TOKEN" in os.environ or "GITHUB_TOKEN" in os.environ
    ):
        return None

    candidates = [
        PROJECT_ROOT / ".env",
        Path.cwd() / ".env",
    ]
    for candidate in candidates:
        if candidate.is_file():
            load_dotenv(dotenv_path=candidate, override=override)
            return candidate
    return None


# Initial load at module import
_loaded_env_path = load_env_files(override=False)


class ServerConfig(BaseModel):
    """Server configuration loaded from environment variables and .env file."""

    github_token: Optional[SecretStr] = Field(
        default=None,
        description="GitHub personal access token for API requests",
    )
    github_api_url: str = Field(
        default="https://api.github.com",
        description="Base URL for GitHub REST API",
    )
    request_timeout: float = Field(
        default=20.0,
        description="HTTP request read timeout in seconds",
    )
    connect_timeout: float = Field(
        default=10.0,
        description="HTTP connection timeout in seconds",
    )
    max_file_size_bytes: int = Field(
        default=500_000,
        description="Maximum file size in bytes to retrieve contents (default 500 KB)",
    )

    @classmethod
    def from_env(cls, reload_env: bool = True) -> "ServerConfig":
        """Load configuration from environment variables, loading project .env if needed."""
        if reload_env:
            load_env_files(override=False)

        raw_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
        clean_token = raw_token.strip().strip("'\"") if raw_token else None

        # Filter out common placeholders from documentation/templates
        if clean_token in _TOKEN_PLACEHOLDERS:
            clean_token = None

        api_url = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
        timeout_str = os.getenv("GITHUB_REQUEST_TIMEOUT", "20.0")
        connect_timeout_str = os.getenv("GITHUB_CONNECT_TIMEOUT", "10.0")

        try:
            timeout = float(timeout_str)
        except ValueError:
            timeout = 20.0

        try:
            connect_timeout = float(connect_timeout_str)
        except ValueError:
            connect_timeout = 10.0

        return cls(
            github_token=SecretStr(clean_token) if clean_token else None,
            github_api_url=api_url,
            request_timeout=timeout,
            connect_timeout=connect_timeout,
        )

    @property
    def has_token(self) -> bool:
        """Return True if a valid non-empty GitHub token is configured."""
        if not self.github_token:
            return False
        val = self.github_token.get_secret_value().strip()
        return len(val) > 0 and val not in _TOKEN_PLACEHOLDERS

    def get_token_value(self) -> Optional[str]:
        """Safely retrieve raw token string for internal API authorization header only."""
        if self.github_token:
            val = self.github_token.get_secret_value().strip().strip("'\"")
            return val if len(val) > 0 and val not in _TOKEN_PLACEHOLDERS else None
        return None

    def get_headers(self) -> dict[str, str]:
        """Generate HTTP headers for GitHub REST API calls without leaking token in logs."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHub-MCP-Server-ML/0.1.0",
        }
        token = self.get_token_value()
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def __repr__(self) -> str:
        token_status = "configured (hidden)" if self.has_token else "not configured"
        return f"ServerConfig(api_url='{self.github_api_url}', token={token_status})"

    def __str__(self) -> str:
        return self.__repr__()


def get_configuration_status(config: Optional[ServerConfig] = None) -> dict[str, Any]:
    """Inspect current configuration safely without exposing sensitive token values."""
    cfg = config or ServerConfig.from_env()
    token_configured = cfg.has_token
    env_file_detected = (PROJECT_ROOT / ".env").is_file() or (Path.cwd() / ".env").is_file()

    return {
        "api_url": cfg.github_api_url,
        "token_configured": token_configured,
        "rate_limit_tier": (
            "5,000 requests/hour (authenticated)"
            if token_configured
            else "60 requests/hour (unauthenticated IP limit)"
        ),
        "env_file_detected": env_file_detected,
        "request_timeout": cfg.request_timeout,
        "connect_timeout": cfg.connect_timeout,
    }


def log_startup_configuration(
    config: Optional[ServerConfig] = None,
    log: Optional[logging.Logger] = None,
) -> None:
    """Log startup configuration to stderr safely, verifying authentication status without leaking tokens."""
    cfg = config or ServerConfig.from_env()
    target_logger = log or logger

    status = get_configuration_status(cfg)

    target_logger.info("=== GitHub MCP Server Startup Configuration ===")
    target_logger.info("GitHub API URL: %s", status["api_url"])
    target_logger.info(
        ".env file detected: %s",
        "Yes" if status["env_file_detected"] else "No (.env file not found)",
    )

    if status["token_configured"]:
        target_logger.info(
            "Authentication: CONFIGURED (Token securely loaded in memory, never logged)"
        )
        target_logger.info("Rate Limit Tier: 5,000 requests/hour")
    else:
        target_logger.warning(
            "Authentication: NOT CONFIGURED (No GITHUB_PERSONAL_ACCESS_TOKEN detected)"
        )
        target_logger.warning("Rate Limit Tier: 60 requests/hour (unauthenticated IP limit)")
        target_logger.warning(
            "To unlock 5,000 req/hr and avoid rate limit 403 errors, create .env in project root with:"
        )
        target_logger.warning("  GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here")
    target_logger.info("================================================")
