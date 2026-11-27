"""Tests for custom error classes and secret protection."""

from github_mcp.errors import (
    GitHubAuthError,
    GitHubContentError,
    GitHubError,
    GitHubNetworkError,
    GitHubNotFoundError,
    GitHubPermissionError,
    GitHubRateLimitError,
    GitHubTimeoutError,
)


def test_error_hierarchy():
    assert issubclass(GitHubAuthError, GitHubError)
    assert issubclass(GitHubPermissionError, GitHubAuthError)
    assert issubclass(GitHubNotFoundError, GitHubError)
    assert issubclass(GitHubRateLimitError, GitHubError)
    assert issubclass(GitHubContentError, GitHubError)
    assert issubclass(GitHubNetworkError, GitHubError)
    assert issubclass(GitHubTimeoutError, GitHubNetworkError)


def test_rate_limit_error_formatting():
    err = GitHubRateLimitError(reset_time=1700000000)
    assert "rate limit" in str(err).lower()
    assert "1700000000" in str(err)
    assert err.status_code == 403


def test_unauthenticated_rate_limit_formatting():
    err = GitHubRateLimitError(reset_time=1700000000, limit=60)
    assert "unauthenticated requests (60 req/hr limit reached)" in str(err)
    assert "GITHUB_PERSONAL_ACCESS_TOKEN" in str(err)
    assert err.limit == 60


def test_secondary_rate_limit_formatting():
    err = GitHubRateLimitError(is_secondary=True, retry_after=45)
    assert "secondary rate limit" in str(err).lower()
    assert "45 seconds" in str(err)
    assert err.retry_after == 45
    assert err.is_secondary is True


def test_auth_error_default():
    err = GitHubAuthError()
    assert "authentication failed" in str(err).lower()
    assert err.status_code == 401


def test_error_str_formatting():
    err = GitHubError("Bad request", status_code=400)
    assert str(err) == "[400] Bad request"

    err_no_code = GitHubError("General failure")
    assert str(err_no_code) == "General failure"


def test_permission_error_formatting():
    err = GitHubPermissionError("Repository access denied")
    assert err.status_code == 403
    assert "access denied" in str(err).lower()


def test_timeout_error_formatting():
    connect_err = GitHubTimeoutError(
        "Connection timed out", timeout_seconds=10.0, is_connect_timeout=True
    )
    assert connect_err.is_connect_timeout is True
    assert connect_err.timeout_seconds == 10.0
    assert "timed out" in str(connect_err)

    read_err = GitHubTimeoutError("Read timed out", timeout_seconds=20.0, is_connect_timeout=False)
    assert read_err.is_connect_timeout is False
    assert read_err.timeout_seconds == 20.0
