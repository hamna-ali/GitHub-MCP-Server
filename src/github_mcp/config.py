"""Configuration and credential management for GitHub MCP Server.

Ensures tokens are reliably loaded from project root .env and environment variables,
and guarantees secrets are never leaked in representations, logs, or error responses.
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr

# Determine canonical project root (directory containing pyproject.toml and .env)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Load from canonical project root .env first, then fallback to current working directory
_project_env = PROJECT_ROOT / ".env"
if _project_env.exists():
    load_dotenv(dotenv_path=_project_env, override=False)
else:
    # Also check current working directory
    load_dotenv(override=False)


class ServerConfig(BaseModel):
    """Server configuration loaded from environment variables."""

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
        description="HTTP request timeout in seconds",
    )
    max_file_size_bytes: int = Field(
        default=500_000,
        description="Maximum file size in bytes to retrieve contents (default 500 KB)",
    )

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Load configuration from environment variables, reloading project .env if needed."""
        # Ensure latest environment variables from project root .env are loaded
        if _project_env.exists():
            load_dotenv(dotenv_path=_project_env, override=False)

        raw_token = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
        clean_token = raw_token.strip().strip("'\"") if raw_token else None

        api_url = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
        timeout_str = os.getenv("GITHUB_REQUEST_TIMEOUT", "20.0")

        try:
            timeout = float(timeout_str)
        except ValueError:
            timeout = 20.0

        return cls(
            github_token=SecretStr(clean_token) if clean_token else None,
            github_api_url=api_url,
            request_timeout=timeout,
        )

    @property
    def has_token(self) -> bool:
        """Return True if a GitHub token is configured."""
        if not self.github_token:
            return False
        val = self.github_token.get_secret_value().strip()
        return len(val) > 0

    def get_token_value(self) -> Optional[str]:
        """Safely retrieve raw token string for internal API authorization header only."""
        if self.github_token:
            val = self.github_token.get_secret_value().strip().strip("'\"")
            return val if len(val) > 0 else None
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
