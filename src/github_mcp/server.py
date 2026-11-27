"""Official Model Context Protocol (MCP) Server for GitHub and ML Portfolio Analysis.

Exposes 5 specialized tools for listing repositories, retrieving metadata,
exploring directory trees, fetching file contents, and conducting comprehensive ML portfolio analyses.
"""

import logging
from typing import Any, Optional

from mcp.server.mcpserver import MCPServer

from github_mcp.config import ServerConfig, log_startup_configuration
from github_mcp.errors import (
    GitHubAuthError,
    GitHubError,
    GitHubPermissionError,
    GitHubRateLimitError,
    GitHubTimeoutError,
)
from github_mcp.github_client import GitHubClient
from github_mcp.ml_analyzer import MLRepositoryAnalyzer

logger = logging.getLogger("github_mcp.server")


def create_server(config: Optional[ServerConfig] = None) -> MCPServer:
    """Create and configure the GitHub MCP server with all 5 portfolio analysis tools."""

    def _resolve_config() -> ServerConfig:
        if config is not None:
            return config
        return ServerConfig.from_env()

    server = MCPServer(
        name="github-mcp-server",
        version="0.1.0",
        instructions=(
            "GitHub Model Context Protocol (MCP) server for Machine Learning portfolio analysis. "
            "Exposes tools to discover repositories, inspect directory trees, read documentation and source code, "
            "and conduct automated machine learning architecture and pipeline verification with evidence tracking."
        ),
    )

    @server.tool(
        name="list_repositories",
        description=(
            "Discover and list GitHub repositories accessible to the authenticated account or a specified user. "
            "Supports filtering by name/description keywords and primary programming language. "
            "Returns repository metadata including stars, forks, visibility, and authenticated rate-limit status."
        ),
    )
    async def list_repositories(
        name_filter: Optional[str] = None,
        language_filter: Optional[str] = None,
        username: Optional[str] = None,
        per_page: int = 100,
        max_pages: int = 3,
    ) -> dict[str, Any]:
        """List and filter repositories."""
        cfg = _resolve_config()
        try:
            async with GitHubClient(config=cfg) as client:
                repos = await client.list_repositories(
                    username=username,
                    name_filter=name_filter,
                    language_filter=language_filter,
                    per_page=per_page,
                    max_pages=max_pages,
                )
                return {
                    "count": len(repos),
                    "authenticated": cfg.has_token,
                    "rate_limit": client.get_rate_limit_info(),
                    "filters": {
                        "name_filter": name_filter,
                        "language_filter": language_filter,
                        "username": username
                        or ("(authenticated user)" if cfg.has_token else "(anonymous)"),
                    },
                    "repositories": [repo.model_dump() for repo in repos],
                }
        except GitHubTimeoutError as e:
            return {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            }
        except GitHubRateLimitError as e:
            return {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
                "is_secondary": e.is_secondary,
                "reset_time": e.reset_time,
                "retry_after": e.retry_after,
            }
        except GitHubPermissionError as e:
            return {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            }
        except GitHubAuthError as e:
            return {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except GitHubError as e:
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except Exception as e:
            logger.exception("Unexpected error in list_repositories")
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            }

    @server.tool(
        name="get_repository_details",
        description=(
            "Retrieve comprehensive metadata for a specific GitHub repository. "
            "Returns description, primary language, topics/tags, license, default branch, "
            "clone URLs, stars, forks, open issues count, and update timestamps."
        ),
    )
    async def get_repository_details(
        owner: str,
        repo: str,
    ) -> dict[str, Any]:
        """Get repository metadata and details."""
        cfg = _resolve_config()
        try:
            async with GitHubClient(config=cfg) as client:
                details = await client.get_repository_details(owner=owner, repo=repo)
                result = details.model_dump()
                result["_authenticated"] = cfg.has_token
                result["_rate_limit"] = client.get_rate_limit_info()
                return result
        except GitHubTimeoutError as e:
            return {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            }
        except GitHubRateLimitError as e:
            return {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
                "is_secondary": e.is_secondary,
                "reset_time": e.reset_time,
                "retry_after": e.retry_after,
            }
        except GitHubPermissionError as e:
            return {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            }
        except GitHubAuthError as e:
            return {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except GitHubError as e:
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except Exception as e:
            logger.exception("Unexpected error in get_repository_details")
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            }

    @server.tool(
        name="get_repository_tree",
        description=(
            "Inspect the directory structure and file tree of a GitHub repository. "
            "Can target a specific branch or commit SHA (defaults to default branch). "
            "Returns paths, object types ('blob' for files, 'tree' for folders), and file sizes in bytes."
        ),
    )
    async def get_repository_tree(
        owner: str,
        repo: str,
        branch: Optional[str] = None,
        recursive: bool = True,
    ) -> dict[str, Any]:
        """Retrieve directory structure of a repository."""
        cfg = _resolve_config()
        try:
            async with GitHubClient(config=cfg) as client:
                tree = await client.get_repository_tree(
                    owner=owner,
                    repo=repo,
                    branch=branch,
                    recursive=recursive,
                )
                result = tree.model_dump()
                result["_authenticated"] = cfg.has_token
                result["_rate_limit"] = client.get_rate_limit_info()
                return result
        except GitHubTimeoutError as e:
            return {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            }
        except GitHubRateLimitError as e:
            return {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
                "is_secondary": e.is_secondary,
                "reset_time": e.reset_time,
                "retry_after": e.retry_after,
            }
        except GitHubPermissionError as e:
            return {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            }
        except GitHubAuthError as e:
            return {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except GitHubError as e:
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except Exception as e:
            logger.exception("Unexpected error in get_repository_tree")
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            }

    @server.tool(
        name="get_file_contents",
        description=(
            "Read and decode file contents (README.md, requirements.txt, pyproject.toml, Python source code). "
            "Handles directories and oversized files gracefully with informative notices. "
            "Returns decoded text content, byte size, and truncation status."
        ),
    )
    async def get_file_contents(
        owner: str,
        repo: str,
        path: str,
        branch: Optional[str] = None,
        max_size_bytes: int = 500_000,
    ) -> dict[str, Any]:
        """Read and decode file contents safely."""
        cfg = _resolve_config()
        try:
            async with GitHubClient(config=cfg) as client:
                file_obj = await client.get_file_contents(
                    owner=owner,
                    repo=repo,
                    path=path,
                    branch=branch,
                    max_size_bytes=max_size_bytes,
                )
                result = file_obj.model_dump()
                result["_authenticated"] = cfg.has_token
                result["_rate_limit"] = client.get_rate_limit_info()
                return result
        except GitHubTimeoutError as e:
            return {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            }
        except GitHubRateLimitError as e:
            return {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
                "is_secondary": e.is_secondary,
                "reset_time": e.reset_time,
                "retry_after": e.retry_after,
            }
        except GitHubPermissionError as e:
            return {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            }
        except GitHubAuthError as e:
            return {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except GitHubError as e:
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except Exception as e:
            logger.exception("Unexpected error in get_file_contents")
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            }

    @server.tool(
        name="analyze_ml_repository",
        description=(
            "Perform an automated, evidence-backed Machine Learning portfolio evaluation on a repository. "
            "Analyzes documentation (README), tree structure, and dependency manifests (requirements.txt, "
            "pyproject.toml, environment.yml) to extract and verify problem statement, ML frameworks, "
            "model architecture, datasets, training pipeline, evaluation metrics, and deployment approach. "
            "Distinguishes documented facts from unverified claims with concrete evidence citations."
        ),
    )
    async def analyze_ml_repository(
        owner: str,
        repo: str,
        branch: Optional[str] = None,
    ) -> dict[str, Any]:
        """Analyze an ML repository and return structured portfolio evaluation."""
        cfg = _resolve_config()
        try:
            async with GitHubClient(config=cfg) as client:
                analyzer = MLRepositoryAnalyzer(client=client)
                analysis = await analyzer.analyze(owner=owner, repo=repo, branch=branch)
                result = analysis.model_dump()
                result["_authenticated"] = cfg.has_token
                result["_rate_limit"] = client.get_rate_limit_info()
                return result
        except GitHubTimeoutError as e:
            return {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            }
        except GitHubRateLimitError as e:
            return {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
                "is_secondary": e.is_secondary,
                "reset_time": e.reset_time,
                "retry_after": e.retry_after,
            }
        except GitHubPermissionError as e:
            return {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            }
        except GitHubAuthError as e:
            return {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except GitHubError as e:
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            }
        except Exception as e:
            logger.exception("Unexpected error in analyze_ml_repository")
            return {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            }

    return server


def main() -> None:
    """Entry point for running the GitHub MCP server over stdio transport."""
    import sys

    # Configure logging to stderr to prevent interference with stdio JSON-RPC transport
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )
    # Output safe startup configuration check to stderr
    log_startup_configuration(log=logger)
    logger.info("Starting GitHub MCP Server over stdio transport...")
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
