"""Reusable asynchronous GitHub REST API client with robust error handling, caching, and rate limit tracking."""

import base64
import logging
import time
from typing import Any, Optional

import httpx

from github_mcp.config import ServerConfig
from github_mcp.errors import (
    GitHubAuthError,
    GitHubContentError,
    GitHubError,
    GitHubNetworkError,
    GitHubNotFoundError,
    GitHubRateLimitError,
)
from github_mcp.models import (
    FileContent,
    RepositoryDetails,
    RepositorySummary,
    RepositoryTree,
    TreeItem,
)

logger = logging.getLogger(__name__)


class GitHubClient:
    """Asynchronous client for GitHub REST API with in-memory caching and resilient rate limit parsing."""

    def __init__(self, config: Optional[ServerConfig] = None):
        self.config = config or ServerConfig.from_env()
        self._client: Optional[httpx.AsyncClient] = None
        # Short-lived in-memory cache for GET responses to avoid duplicate calls during a demo session
        self._cache: dict[tuple[str, tuple], tuple[float, httpx.Response]] = {}
        self._cache_ttl: float = 300.0  # 5 minutes

    async def __aenter__(self) -> "GitHubClient":
        headers = self.config.get_headers()
        self._client = httpx.AsyncClient(
            base_url=self.config.github_api_url,
            headers=headers,
            timeout=self.config.request_timeout,
            follow_redirects=True,
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = self.config.get_headers()
            self._client = httpx.AsyncClient(
                base_url=self.config.github_api_url,
                headers=headers,
                timeout=self.config.request_timeout,
                follow_redirects=True,
            )
        return self._client

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
        use_cache: bool = True,
    ) -> httpx.Response:
        """Execute HTTP request with caching, unified error translation, and rate limit defense."""
        # Check in-memory cache for GET requests
        cache_key = (
            endpoint,
            tuple(sorted((k, str(v)) for k, v in params.items())) if params else (),
        )
        if method.upper() == "GET" and use_cache and cache_key in self._cache:
            ts, cached_resp = self._cache[cache_key]
            if time.time() - ts < self._cache_ttl:
                logger.debug("Serving cached response for %s", endpoint)
                return cached_resp

        client = self._get_client()
        # Merge configuration headers (which include Authorization if a token is configured)
        req_headers = dict(self.config.get_headers())
        if headers:
            req_headers.update(headers)

        try:
            response = await client.request(
                method=method,
                url=endpoint,
                params=params,
                headers=req_headers,
            )
        except (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            httpx.ReadTimeout,
            httpx.NetworkError,
        ) as e:
            logger.error("Network communication error with GitHub API: %s", type(e).__name__)
            raise GitHubNetworkError(
                f"Failed to communicate with GitHub API ({type(e).__name__}). Check network connection."
            ) from None
        except Exception as e:
            logger.error("Unexpected error communicating with GitHub API: %s", type(e).__name__)
            raise GitHubNetworkError(
                f"Network request to GitHub failed: {type(e).__name__}"
            ) from None

        # Inspect rate limit headers on successful response
        if response.status_code == 200:
            remaining = response.headers.get("x-ratelimit-remaining")
            if remaining and remaining.isdigit() and int(remaining) <= 5:
                logger.warning(
                    "GitHub API quota running low: %s remaining (limit %s)",
                    remaining,
                    response.headers.get("x-ratelimit-limit"),
                )
            if method.upper() == "GET" and use_cache:
                self._cache[cache_key] = (time.time(), response)
            return response

        # Handle specific GitHub API HTTP status codes
        if response.status_code == 401:
            raise GitHubAuthError(
                "GitHub authentication failed (401 Unauthorized). "
                "Ensure GITHUB_PERSONAL_ACCESS_TOKEN is valid and has read permissions."
            )

        if response.status_code in (403, 429):
            rate_remaining = response.headers.get("x-ratelimit-remaining")
            rate_limit_hdr = response.headers.get("x-ratelimit-limit")
            reset_ts = response.headers.get("x-ratelimit-reset")
            retry_after_hdr = response.headers.get("retry-after")

            remaining = int(rate_remaining) if rate_remaining and rate_remaining.isdigit() else None
            limit = int(rate_limit_hdr) if rate_limit_hdr and rate_limit_hdr.isdigit() else None
            reset_time = int(reset_ts) if reset_ts and reset_ts.isdigit() else None
            retry_after = (
                int(retry_after_hdr) if retry_after_hdr and retry_after_hdr.isdigit() else None
            )

            resp_text_lower = response.text.lower()
            is_secondary = (
                retry_after is not None
                or "secondary rate limit" in resp_text_lower
                or "please wait a few minutes" in resp_text_lower
            )
            is_rate_limit = (
                is_secondary
                or remaining == 0
                or "rate limit" in resp_text_lower
                or response.status_code == 429
            )

            if is_rate_limit:
                raise GitHubRateLimitError(
                    reset_time=reset_time,
                    retry_after=retry_after,
                    limit=limit,
                    remaining=remaining,
                    is_secondary=is_secondary,
                    status_code=response.status_code,
                )

            # Other 403 forbidden error (permissions)
            err_msg = "Forbidden (403). Your token may lack permissions for this resource."
            try:
                data = response.json()
                if "message" in data:
                    err_msg = f"GitHub API Forbidden: {data['message']}"
            except Exception:
                pass
            raise GitHubAuthError(err_msg, status_code=403)

        if response.status_code == 404:
            clean_endpoint = endpoint.split("?")[0]
            raise GitHubNotFoundError(
                f"Resource not found on GitHub: {clean_endpoint}",
                status_code=404,
            )

        if response.status_code >= 400:
            err_msg = f"GitHub API request failed with status {response.status_code}"
            try:
                data = response.json()
                if "message" in data:
                    err_msg += f": {data['message']}"
            except Exception:
                pass
            raise GitHubError(err_msg, status_code=response.status_code)

        return response

    async def list_repositories(
        self,
        username: Optional[str] = None,
        name_filter: Optional[str] = None,
        language_filter: Optional[str] = None,
        per_page: int = 100,
        max_pages: int = 3,
    ) -> list[RepositorySummary]:
        """List repositories accessible to the user with optional name and language filtering."""
        all_repos: list[RepositorySummary] = []

        if username:
            endpoint = f"/users/{username}/repos"
            base_params = {"sort": "updated", "per_page": min(per_page, 100), "type": "all"}
        else:
            if not self.config.has_token:
                raise GitHubAuthError(
                    "No username was provided and GITHUB_PERSONAL_ACCESS_TOKEN is not configured. "
                    "Either specify a GitHub username or set a token in .env."
                )
            endpoint = "/user/repos"
            base_params = {
                "affiliation": "owner,collaborator,organization_member",
                "sort": "updated",
                "per_page": min(per_page, 100),
            }

        page = 1
        while page <= max_pages:
            params = {**base_params, "page": page}
            response = await self._request("GET", endpoint, params=params)
            items = response.json()
            if not isinstance(items, list) or len(items) == 0:
                break

            for item in items:
                summary = RepositorySummary(
                    id=item["id"],
                    name=item["name"],
                    full_name=item["full_name"],
                    owner=item["owner"]["login"] if "owner" in item and item["owner"] else "",
                    description=item.get("description"),
                    language=item.get("language"),
                    default_branch=item.get("default_branch", "main"),
                    html_url=item.get("html_url", ""),
                    is_private=item.get("private", False),
                    stargazers_count=item.get("stargazers_count", 0),
                    forks_count=item.get("forks_count", 0),
                    open_issues_count=item.get("open_issues_count", 0),
                    updated_at=item.get("updated_at"),
                )

                # Filter by name (case-insensitive substring)
                if name_filter:
                    term = name_filter.lower()
                    name_match = (
                        term in summary.name.lower() or term in (summary.description or "").lower()
                    )
                    if not name_match:
                        continue

                # Filter by language (case-insensitive match)
                if language_filter:
                    lang_term = language_filter.lower()
                    repo_lang = (summary.language or "").lower()
                    if lang_term not in repo_lang:
                        continue

                all_repos.append(summary)

            # If less items than per_page returned, we've reached the last page
            if len(items) < per_page:
                break
            page += 1

        return all_repos

    async def get_repository_details(self, owner: str, repo: str) -> RepositoryDetails:
        """Fetch complete repository details and metadata."""
        endpoint = f"/repos/{owner}/{repo}"
        response = await self._request("GET", endpoint)
        item = response.json()

        license_name = None
        if item.get("license") and isinstance(item["license"], dict):
            license_name = item["license"].get("spdx_id") or item["license"].get("name")

        return RepositoryDetails(
            id=item["id"],
            name=item["name"],
            full_name=item["full_name"],
            owner=item["owner"]["login"] if "owner" in item and item["owner"] else owner,
            description=item.get("description"),
            language=item.get("language"),
            default_branch=item.get("default_branch", "main"),
            html_url=item.get("html_url", ""),
            clone_url=item.get("clone_url", ""),
            ssh_url=item.get("ssh_url"),
            topics=item.get("topics", []),
            license_name=license_name,
            created_at=item.get("created_at"),
            updated_at=item.get("updated_at"),
            pushed_at=item.get("pushed_at"),
            size_kb=item.get("size", 0),
            stargazers_count=item.get("stargazers_count", 0),
            forks_count=item.get("forks_count", 0),
            open_issues_count=item.get("open_issues_count", 0),
            is_archived=item.get("archived", False),
            is_fork=item.get("fork", False),
        )

    async def get_repository_tree(
        self,
        owner: str,
        repo: str,
        branch: Optional[str] = None,
        recursive: bool = True,
    ) -> RepositoryTree:
        """Retrieve directory structure of a repository using the Git Trees API."""
        # Use HEAD directly to avoid redundant get_repository_details calls
        target_branch = branch or "HEAD"
        endpoint = f"/repos/{owner}/{repo}/git/trees/{target_branch}"
        params = {"recursive": "1"} if recursive else {}

        try:
            response = await self._request("GET", endpoint, params=params)
        except GitHubNotFoundError:
            if not branch:
                # Fallback to querying default_branch explicitly if HEAD fails
                repo_meta = await self.get_repository_details(owner, repo)
                target_branch = repo_meta.default_branch
                endpoint = f"/repos/{owner}/{repo}/git/trees/{target_branch}"
                response = await self._request("GET", endpoint, params=params)
            else:
                raise

        data = response.json()

        tree_items: list[TreeItem] = []
        raw_tree = data.get("tree", [])
        for entry in raw_tree:
            tree_items.append(
                TreeItem(
                    path=entry["path"],
                    mode=entry.get("mode", ""),
                    type=entry.get("type", "blob"),
                    size=entry.get("size"),
                    sha=entry.get("sha", ""),
                )
            )

        return RepositoryTree(
            owner=owner,
            repo=repo,
            branch=target_branch,
            tree_sha=data.get("sha", ""),
            truncated=data.get("truncated", False),
            total_items=len(tree_items),
            items=tree_items,
        )

    async def get_file_contents(
        self,
        owner: str,
        repo: str,
        path: str,
        branch: Optional[str] = None,
        max_size_bytes: Optional[int] = None,
    ) -> FileContent:
        """Retrieve and decode file content safely, handling directories, large files, and binaries."""
        clean_path = path.strip("/")
        endpoint = f"/repos/{owner}/{repo}/contents/{clean_path}"
        params = {}
        if branch:
            params["ref"] = branch

        response = await self._request("GET", endpoint, params=params)
        data = response.json()

        # If data is a list, the user requested a directory path
        if isinstance(data, list):
            item_names = [f"{item.get('name')} ({item.get('type')})" for item in data[:30]]
            preview = ", ".join(item_names)
            if len(data) > 30:
                preview += f" ... and {len(data) - 30} more items"
            raise GitHubContentError(
                f"Path '{clean_path}' is a directory containing {len(data)} items: [{preview}]. "
                "Use get_repository_tree to inspect directories, or specify an exact file path."
            )

        size_bytes = data.get("size", 0)
        encoding = data.get("encoding", "")
        raw_content = data.get("content", "")
        download_url = data.get("download_url")
        file_name = data.get("name", clean_path.split("/")[-1])
        limit = max_size_bytes or self.config.max_file_size_bytes

        # Check for large file
        if size_bytes > limit:
            return FileContent(
                path=clean_path,
                name=file_name,
                size_bytes=size_bytes,
                encoding=encoding or "raw",
                content=(
                    f"[File exceeds maximum size limit ({size_bytes:,} bytes > {limit:,} bytes). "
                    f"Use raw download URL if full download is necessary: {download_url}]"
                ),
                is_truncated=True,
                is_binary=False,
                download_url=download_url,
                message=f"File exceeds size threshold ({size_bytes:,} bytes). Content omitted for stability.",
            )

        # Decode base64 content if provided
        decoded_text = ""
        is_binary = False

        if encoding == "base64" and raw_content:
            try:
                decoded_bytes = base64.b64decode(raw_content)
                # Try decoding as UTF-8
                try:
                    decoded_text = decoded_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    try:
                        decoded_text = decoded_bytes.decode("latin-1")
                    except Exception:
                        is_binary = True
                        decoded_text = (
                            f"[Binary file: {len(decoded_bytes):,} bytes. Raw preview unavailable]"
                        )
            except Exception as e:
                logger.warning("Base64 decode failed for %s: %s", clean_path, e)
                decoded_text = f"[Base64 decode error: {e}]"
        elif not raw_content and download_url:
            # File might be larger than GitHub contents API inline limit (1MB) but below our limit
            try:
                raw_resp = await self._get_client().get(download_url)
                if raw_resp.status_code == 200:
                    try:
                        decoded_text = raw_resp.text
                    except Exception:
                        is_binary = True
                        decoded_text = f"[Binary file: {len(raw_resp.content):,} bytes]"
                else:
                    decoded_text = f"[Failed to fetch raw content from {download_url}]"
            except Exception as e:
                decoded_text = f"[Failed to download raw file: {e}]"
        else:
            decoded_text = str(raw_content)

        return FileContent(
            path=clean_path,
            name=file_name,
            size_bytes=size_bytes,
            encoding=encoding or "utf-8",
            content=decoded_text,
            is_truncated=False,
            is_binary=is_binary,
            download_url=download_url,
        )
