"""Official Model Context Protocol (MCP) Server for GitHub and ML Portfolio Analysis.

Exposes 5 specialized tools for listing repositories, retrieving metadata,
exploring directory trees, fetching file contents, and conducting comprehensive ML portfolio analyses.
"""

import logging
from typing import Any, Optional

from mcp.server.mcpserver import MCPServer

from github_mcp.config import ServerConfig
from github_mcp.errors import GitHubError
from github_mcp.github_client import GitHubClient
from github_mcp.ml_analyzer import MLRepositoryAnalyzer

logger = logging.getLogger("github_mcp.server")


def create_server(config: Optional[ServerConfig] = None) -> MCPServer:
    """Create and configure the GitHub MCP server with all 5 portfolio analysis tools."""
    cfg = config or ServerConfig.from_env()
    server = MCPServer(
        name="github-mcp-server",
        version="0.1.0",
        instructions=(
            "GitHub Model Context Protocol (MCP) server for Machine Learning portfolio analysis. "
            "Use these tools to discover repositories, inspect code trees, read documentation and source code, "
            "and conduct automated machine learning architecture and pipeline verification."
        ),
    )

    @server.tool(
        name="list_repositories",
        description=(
            "List repositories accessible to the user or an optionally specified GitHub account. "
            "Supports filtering by repository name (or description keywords) and programming language. "
            "Returns a structured list of repository summaries with star counts, primary languages, and update dates."
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
                    "filters": {
                        "name_filter": name_filter,
                        "language_filter": language_filter,
                        "username": username or "(authenticated user)",
                    },
                    "repositories": [repo.model_dump() for repo in repos],
                }
        except GitHubError as e:
            return {"error": True, "message": str(e), "status_code": e.status_code}
        except Exception as e:
            logger.exception("Unexpected error in list_repositories")
            return {"error": True, "message": f"Unexpected error: {type(e).__name__} - {e}"}

    @server.tool(
        name="get_repository_details",
        description=(
            "Fetch detailed metadata for a specific GitHub repository, including description, "
            "topics, license, default branch, primary language, clone URLs, stars, forks, and timestamps."
        ),
    )
    async def get_repository_details(
        owner: str,
        repo: str,
    ) -> dict[str, Any]:
        """Get repository metadata and details."""
        try:
            async with GitHubClient(config=cfg) as client:
                details = await client.get_repository_details(owner=owner, repo=repo)
                return details.model_dump()
        except GitHubError as e:
            return {"error": True, "message": str(e), "status_code": e.status_code}
        except Exception as e:
            logger.exception("Unexpected error in get_repository_details")
            return {"error": True, "message": f"Unexpected error: {type(e).__name__} - {e}"}

    @server.tool(
        name="get_repository_tree",
        description=(
            "Retrieve the directory structure and file tree of a GitHub repository. "
            "Can target a specific branch or commit SHA (defaults to repository default branch). "
            "Returns paths, object types ('blob' for files, 'tree' for folders), and file sizes."
        ),
    )
    async def get_repository_tree(
        owner: str,
        repo: str,
        branch: Optional[str] = None,
        recursive: bool = True,
    ) -> dict[str, Any]:
        """Retrieve directory structure of a repository."""
        try:
            async with GitHubClient(config=cfg) as client:
                tree = await client.get_repository_tree(
                    owner=owner,
                    repo=repo,
                    branch=branch,
                    recursive=recursive,
                )
                return tree.model_dump()
        except GitHubError as e:
            return {"error": True, "message": str(e), "status_code": e.status_code}
        except Exception as e:
            logger.exception("Unexpected error in get_repository_tree")
            return {"error": True, "message": f"Unexpected error: {type(e).__name__} - {e}"}

    @server.tool(
        name="get_file_contents",
        description=(
            "Read file contents such as README.md, requirements.txt, pyproject.toml, and Python scripts. "
            "Handles directories and large files gracefully with informative messages. "
            "Returns decoded text content, file size, and truncation status."
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
        try:
            async with GitHubClient(config=cfg) as client:
                file_obj = await client.get_file_contents(
                    owner=owner,
                    repo=repo,
                    path=path,
                    branch=branch,
                    max_size_bytes=max_size_bytes,
                )
                return file_obj.model_dump()
        except GitHubError as e:
            return {"error": True, "message": str(e), "status_code": e.status_code}
        except Exception as e:
            logger.exception("Unexpected error in get_file_contents")
            return {"error": True, "message": f"Unexpected error: {type(e).__name__} - {e}"}

    @server.tool(
        name="analyze_ml_repository",
        description=(
            "Perform an automated, structured Machine Learning portfolio analysis on a repository. "
            "Analyzes README documentation, repository tree structure, and dependency files (requirements.txt, "
            "pyproject.toml, environment.yml) to identify the problem statement, ML frameworks, "
            "model architecture, datasets, training pipeline, evaluation metrics, and deployment approach. "
            "Clearly distinguishes documented and verified findings from unverified aspects."
        ),
    )
    async def analyze_ml_repository(
        owner: str,
        repo: str,
        branch: Optional[str] = None,
    ) -> dict[str, Any]:
        """Analyze an ML repository and return structured portfolio evaluation."""
        try:
            async with GitHubClient(config=cfg) as client:
                analyzer = MLRepositoryAnalyzer(client=client)
                analysis = await analyzer.analyze(owner=owner, repo=repo, branch=branch)
                return analysis.model_dump()
        except GitHubError as e:
            return {"error": True, "message": str(e), "status_code": e.status_code}
        except Exception as e:
            logger.exception("Unexpected error in analyze_ml_repository")
            return {"error": True, "message": f"Unexpected error: {type(e).__name__} - {e}"}

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
    logger.info("Starting GitHub MCP Server over stdio transport...")
    server = create_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
