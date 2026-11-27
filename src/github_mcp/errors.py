"""Custom exceptions for GitHub MCP server.

Tokens and credentials are guaranteed never to appear in error messages.
"""

from typing import Optional


class GitHubError(Exception):
    """Base exception for all GitHub API client errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self) -> str:
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class GitHubAuthError(GitHubError):
    """Raised when authentication fails or required token is missing."""

    def __init__(
        self,
        message: str = "Authentication failed. Please verify that your GitHub personal access token is valid and has required read permissions.",
        status_code: int = 401,
    ):
        super().__init__(message, status_code=status_code)


class GitHubNotFoundError(GitHubError):
    """Raised when a requested resource (repository, branch, file) is not found."""

    def __init__(self, message: str = "Resource not found on GitHub.", status_code: int = 404):
        super().__init__(message, status_code=status_code)


class GitHubRateLimitError(GitHubError):
    """Raised when GitHub API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "GitHub API rate limit exceeded.",
        reset_time: Optional[int] = None,
        status_code: int = 403,
    ):
        full_message = message
        if reset_time:
            full_message = f"{message} Rate limit resets at Unix timestamp {reset_time}."
        super().__init__(full_message, status_code=status_code)
        self.reset_time = reset_time


class GitHubContentError(GitHubError):
    """Raised when file content cannot be retrieved (e.g., path is directory or too large)."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, status_code=status_code)


class GitHubNetworkError(GitHubError):
    """Raised when network communication with GitHub API fails."""

    def __init__(self, message: str = "Failed to connect to GitHub API due to a network error."):
        super().__init__(message, status_code=None)
