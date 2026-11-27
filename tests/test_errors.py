"""Tests for custom error classes and secret protection."""

from github_mcp.errors import (
    GitHubAuthError,
    GitHubContentError,
    GitHubError,
    GitHubNetworkError,
    GitHubNotFoundError,
    GitHubRateLimitError,
)


def test_error_hierarchy():
    assert issubclass(GitHubAuthError, GitHubError)
    assert issubclass(GitHubNotFoundError, GitHubError)
    assert issubclass(GitHubRateLimitError, GitHubError)
    assert issubclass(GitHubContentError, GitHubError)
    assert issubclass(GitHubNetworkError, GitHubError)


def test_rate_limit_error_formatting():
    err = GitHubRateLimitError(reset_time=1700000000)
    assert "rate limit" in str(err).lower()
    assert "1700000000" in str(err)
    assert err.status_code == 403


def test_auth_error_default():
    err = GitHubAuthError()
    assert "authentication failed" in str(err).lower()
    assert err.status_code == 401


def test_error_str_formatting():
    err = GitHubError("Bad request", status_code=400)
    assert str(err) == "[400] Bad request"

    err_no_code = GitHubError("General failure")
    assert str(err_no_code) == "General failure"
