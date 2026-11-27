"""Tests for asynchronous GitHub REST API client."""

import httpx
import pytest

from github_mcp.config import ServerConfig
from github_mcp.errors import (
    GitHubAuthError,
    GitHubContentError,
    GitHubNetworkError,
    GitHubNotFoundError,
    GitHubPermissionError,
    GitHubRateLimitError,
    GitHubTimeoutError,
)
from github_mcp.github_client import GitHubClient
from tests.conftest import (
    SAMPLE_REPO_DETAILS,
    SAMPLE_REPOS,
    encode_github_content,
)


@pytest.mark.asyncio
async def test_list_repositories_authenticated(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/user/repos"
        # Verify Authorization header is sent with Bearer mock token
        assert "authorization" in request.headers
        assert request.headers["authorization"] == f"Bearer {test_config.get_token_value()}"
        return httpx.Response(200, json=SAMPLE_REPOS)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    repos = await client.list_repositories()
    assert len(repos) == 3
    assert repos[0].name == "vision-transformer-classifier"
    assert repos[0].owner == "ml-engineer"
    assert repos[0].language == "Python"
    assert repos[0].stargazers_count == 142
    await client.close()


@pytest.mark.asyncio
async def test_list_repositories_username_includes_authorization_header(test_config):
    """Verify that when a token is configured, requests by username include the Authorization header."""
    recorded_headers = {}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users/hamna-ali/repos"
        recorded_headers.update(dict(request.headers))
        return httpx.Response(200, json=SAMPLE_REPOS)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    repos = await client.list_repositories(username="hamna-ali")
    assert len(repos) == 3
    assert "authorization" in recorded_headers
    assert recorded_headers["authorization"] == f"Bearer {test_config.get_token_value()}"
    await client.close()


@pytest.mark.asyncio
async def test_list_repositories_username_without_token_omits_authorization_header():
    """Verify that requests by username without a token omit the Authorization header (unauthenticated tier)."""
    config = ServerConfig()  # No token
    recorded_headers = {}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users/hamna-ali/repos"
        recorded_headers.update(dict(request.headers))
        return httpx.Response(200, json=SAMPLE_REPOS)

    client = GitHubClient(config=config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    repos = await client.list_repositories(username="hamna-ali")
    assert len(repos) == 3
    assert "authorization" not in recorded_headers
    await client.close()


@pytest.mark.asyncio
async def test_list_repositories_filter_name(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=SAMPLE_REPOS)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    # Filter for "transformer"
    filtered = await client.list_repositories(name_filter="transformer")
    assert len(filtered) == 1
    assert filtered[0].name == "vision-transformer-classifier"

    # Filter case-insensitive for "XGBOOST"
    filtered_xg = await client.list_repositories(name_filter="XGBOOST")
    assert len(filtered_xg) == 1
    assert filtered_xg[0].name == "customer-churn-xgboost"
    await client.close()


@pytest.mark.asyncio
async def test_list_repositories_filter_language(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=SAMPLE_REPOS)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    # Filter Python
    py_repos = await client.list_repositories(language_filter="python")
    assert len(py_repos) == 2

    # Filter TypeScript
    ts_repos = await client.list_repositories(language_filter="typescript")
    assert len(ts_repos) == 1
    assert ts_repos[0].name == "react-ml-dashboard"
    await client.close()


@pytest.mark.asyncio
async def test_list_repositories_by_username():
    config = ServerConfig()  # No token

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/users/octocat/repos"
        return httpx.Response(200, json=SAMPLE_REPOS)

    client = GitHubClient(config=config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    repos = await client.list_repositories(username="octocat")
    assert len(repos) == 3
    await client.close()


@pytest.mark.asyncio
async def test_list_repositories_missing_token_and_username():
    config = ServerConfig()  # No token
    client = GitHubClient(config=config)
    with pytest.raises(GitHubAuthError) as exc_info:
        await client.list_repositories()
    assert "No username was provided and GITHUB_PERSONAL_ACCESS_TOKEN is not configured" in str(
        exc_info.value
    )
    await client.close()


@pytest.mark.asyncio
async def test_get_repository_details(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/repos/ml-engineer/vision-transformer-classifier"
        return httpx.Response(200, json=SAMPLE_REPO_DETAILS)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    details = await client.get_repository_details("ml-engineer", "vision-transformer-classifier")
    assert details.name == "vision-transformer-classifier"
    assert details.full_name == "ml-engineer/vision-transformer-classifier"
    assert details.license_name == "MIT"
    assert "vision-transformer" in details.topics
    assert details.clone_url == "https://github.com/ml-engineer/vision-transformer-classifier.git"
    await client.close()


@pytest.mark.asyncio
async def test_get_repository_tree(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/repos/ml-engineer/test-repo":
            return httpx.Response(200, json={"default_branch": "main", **SAMPLE_REPO_DETAILS})
        if request.url.path == "/repos/ml-engineer/test-repo/git/trees/main":
            return httpx.Response(
                200,
                json={
                    "sha": "tree123",
                    "truncated": False,
                    "tree": [
                        {
                            "path": "README.md",
                            "type": "blob",
                            "size": 100,
                            "sha": "sha1",
                            "mode": "100644",
                        },
                        {"path": "src", "type": "tree", "sha": "sha2", "mode": "040000"},
                    ],
                },
            )
        return httpx.Response(404)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    tree = await client.get_repository_tree("ml-engineer", "test-repo")
    assert tree.branch == "main"
    assert tree.total_items == 2
    assert tree.items[0].path == "README.md"
    assert tree.items[0].type == "blob"
    assert tree.items[1].path == "src"
    assert tree.items[1].type == "tree"
    await client.close()


@pytest.mark.asyncio
async def test_get_file_contents_normal(test_config):
    payload = encode_github_content("print('Hello Machine Learning!')\n")

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/repos/owner/repo/contents/src/main.py"
        return httpx.Response(200, json=payload)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    file_obj = await client.get_file_contents("owner", "repo", "src/main.py")
    assert file_obj.path == "src/main.py"
    assert file_obj.content == "print('Hello Machine Learning!')\n"
    assert not file_obj.is_truncated
    assert not file_obj.is_binary
    await client.close()


@pytest.mark.asyncio
async def test_get_file_contents_directory_error(test_config):
    # GitHub contents API returns a list when querying a directory
    dir_payload = [
        {"name": "file1.py", "type": "file"},
        {"name": "subfolder", "type": "dir"},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=dir_payload)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    with pytest.raises(GitHubContentError) as exc_info:
        await client.get_file_contents("owner", "repo", "src")
    assert "directory" in str(exc_info.value).lower()
    await client.close()


@pytest.mark.asyncio
async def test_get_file_contents_large_file(test_config):
    large_payload = {
        "name": "huge_weights.pt",
        "path": "huge_weights.pt",
        "size": 5_000_000,  # 5 MB > 500 KB limit
        "encoding": "base64",
        "content": "",
        "download_url": "https://raw.githubusercontent.com/owner/repo/main/huge_weights.pt",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=large_payload)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    file_obj = await client.get_file_contents("owner", "repo", "huge_weights.pt")
    assert file_obj.is_truncated
    assert "exceeds" in file_obj.content.lower()
    await client.close()


@pytest.mark.asyncio
async def test_get_file_contents_not_found(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"message": "Not Found"})

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    with pytest.raises(GitHubNotFoundError):
        await client.get_file_contents("owner", "repo", "non_existent.py")
    await client.close()


@pytest.mark.asyncio
async def test_rate_limit_handling(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        headers = {
            "x-ratelimit-remaining": "0",
            "x-ratelimit-reset": "1750000000",
        }
        return httpx.Response(403, headers=headers, json={"message": "API rate limit exceeded"})

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    with pytest.raises(GitHubRateLimitError) as exc_info:
        await client.get_repository_details("owner", "repo")
    assert exc_info.value.reset_time == 1750000000
    assert "rate limit exceeded" in str(exc_info.value).lower()
    await client.close()


@pytest.mark.asyncio
async def test_authentication_error(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"message": "Bad credentials"})

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    with pytest.raises(GitHubAuthError):
        await client.get_repository_details("owner", "repo")
    await client.close()


@pytest.mark.asyncio
async def test_network_error_translation(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("Connection refused")

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    with pytest.raises(GitHubNetworkError):
        await client.get_repository_details("owner", "repo")
    await client.close()


@pytest.mark.asyncio
async def test_secondary_rate_limit_handling(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        headers = {"retry-after": "60"}
        return httpx.Response(
            403,
            headers=headers,
            json={"message": "You have exceeded a secondary rate limit. Please wait 60 seconds."},
        )

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    with pytest.raises(GitHubRateLimitError) as exc_info:
        await client.get_repository_details("owner", "repo")
    assert exc_info.value.is_secondary is True
    assert exc_info.value.retry_after == 60
    assert "secondary rate limit" in str(exc_info.value).lower()
    await client.close()


@pytest.mark.asyncio
async def test_client_in_memory_caching(test_config):
    call_count = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, json=SAMPLE_REPO_DETAILS)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    # First call triggers handler
    res1 = await client.get_repository_details("ml-engineer", "vision-transformer-classifier")
    assert call_count == 1
    assert res1.name == "vision-transformer-classifier"

    # Second call uses in-memory cache and does not call handler again
    res2 = await client.get_repository_details("ml-engineer", "vision-transformer-classifier")
    assert call_count == 1
    assert res2.name == "vision-transformer-classifier"

    await client.close()


@pytest.mark.asyncio
async def test_connect_timeout_raises_github_timeout_error(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectTimeout("Connect timeout to api.github.com")

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    with pytest.raises(GitHubTimeoutError) as exc_info:
        await client.get_repository_details("owner", "repo")
    assert exc_info.value.is_connect_timeout is True
    assert "ConnectTimeout" in str(exc_info.value)
    await client.close()


@pytest.mark.asyncio
async def test_read_timeout_raises_github_timeout_error(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("Read timeout from api.github.com")

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    with pytest.raises(GitHubTimeoutError) as exc_info:
        await client.get_repository_details("owner", "repo")
    assert exc_info.value.is_connect_timeout is False
    assert "Read timed out" in str(exc_info.value)
    await client.close()


@pytest.mark.asyncio
async def test_permission_error_on_403(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403, json={"message": "Resource not accessible by personal access token"}
        )

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    with pytest.raises(GitHubPermissionError) as exc_info:
        await client.get_repository_details("owner", "private-repo")
    assert exc_info.value.status_code == 403
    assert "Resource not accessible" in str(exc_info.value)
    await client.close()


@pytest.mark.asyncio
async def test_rate_limit_tracking(test_config):
    def handler(request: httpx.Request) -> httpx.Response:
        headers = {
            "x-ratelimit-limit": "5000",
            "x-ratelimit-remaining": "4950",
            "x-ratelimit-reset": "1750001234",
            "x-ratelimit-used": "50",
        }
        return httpx.Response(200, headers=headers, json=SAMPLE_REPO_DETAILS)

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    await client.get_repository_details("ml-engineer", "vision-transformer-classifier")
    info = client.get_rate_limit_info()
    assert info["limit"] == 5000
    assert info["remaining"] == 4950
    assert info["used"] == 50
    assert info["reset_epoch"] == 1750001234
    assert info["authenticated"] is True
    await client.close()
