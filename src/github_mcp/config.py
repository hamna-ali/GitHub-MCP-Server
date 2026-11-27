"""Configuration and credential management for GitHub MCP Server.

Ensures tokens are read from environment variables and never leaked in representations or logs.
"""

import os
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr

# Load variables from .env file if present
load_dotenv()


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
        """Load configuration from environment variables."""
        token_val = os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN") or os.getenv("GITHUB_TOKEN")
        api_url = os.getenv("GITHUB_API_URL", "https://api.github.com").rstrip("/")
        timeout_str = os.getenv("GITHUB_REQUEST_TIMEOUT", "20.0")

        try:
            timeout = float(timeout_str)
        except ValueError:
            timeout = 20.0

        return cls(
            github_token=SecretStr(token_val) if token_val else None,
            github_api_url=api_url,
            request_timeout=timeout,
        )

    @property
    def has_token(self) -> bool:
        """Return True if a GitHub token is configured."""
        return (
            self.github_token is not None and len(self.github_token.get_secret_value().strip()) > 0
        )

    def get_token_value(self) -> Optional[str]:
        """Safely retrieve raw token string for internal API authorization header only."""
        if self.github_token:
            return self.github_token.get_secret_value()
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
