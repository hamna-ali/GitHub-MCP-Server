"""Custom exceptions for GitHub MCP server.

Tokens and credentials are guaranteed never to appear in error messages.
"""

import datetime
import time
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
    """Raised when authentication fails or required token is missing/invalid."""

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
    """Raised when GitHub API primary or secondary rate limit is exceeded."""

    def __init__(
        self,
        message: str = "GitHub API rate limit exceeded.",
        reset_time: Optional[int] = None,
        retry_after: Optional[int] = None,
        limit: Optional[int] = None,
        remaining: Optional[int] = None,
        is_secondary: bool = False,
        status_code: int = 403,
    ):
        self.reset_time = reset_time
        self.retry_after = retry_after
        self.limit = limit
        self.remaining = remaining
        self.is_secondary = is_secondary

        formatted_msg = message
        if is_secondary:
            wait_sec = retry_after or 60
            formatted_msg = (
                f"GitHub API secondary rate limit triggered (concurrent/burst requests). "
                f"Please wait {wait_sec} seconds before retrying."
            )
        elif reset_time:
            now = time.time()
            diff_sec = max(0, int(reset_time - now))
            mins = diff_sec // 60
            secs = diff_sec % 60
            time_str = datetime.datetime.fromtimestamp(reset_time, datetime.timezone.utc).strftime(
                "%H:%M:%S UTC"
            )

            if limit == 60:
                formatted_msg = (
                    f"GitHub API rate limit exceeded for unauthenticated requests (60 req/hr limit reached). "
                    f"Quota resets at {time_str} (in ~{mins}m {secs}s). "
                    f"To get 5,000 requests/hr, configure GITHUB_PERSONAL_ACCESS_TOKEN in your .env file."
                )
            elif limit == 5000:
                formatted_msg = (
                    f"GitHub API rate limit exceeded for authenticated account (5,000 req/hr limit reached). "
                    f"Quota resets at {time_str} (in ~{mins}m {secs}s)."
                )
            else:
                formatted_msg = f"{message} Quota resets at {time_str} (in ~{mins}m {secs}s, Unix timestamp {reset_time})."

        super().__init__(formatted_msg, status_code=status_code)


class GitHubContentError(GitHubError):
    """Raised when file content cannot be retrieved (e.g., path is directory or too large)."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message, status_code=status_code)


class GitHubNetworkError(GitHubError):
    """Raised when network communication with GitHub API fails."""

    def __init__(self, message: str = "Failed to connect to GitHub API due to a network error."):
        super().__init__(message, status_code=None)
