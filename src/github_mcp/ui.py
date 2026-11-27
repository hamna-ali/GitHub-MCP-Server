"""Client-facing Web Application and API server for GitHub MCP Server.

Provides a clean, human-friendly interface for non-technical users and technical evaluators
to explore repositories, inspect ML project architectures, and copy MCP client configuration snippets.
"""

import inspect
import json
import logging
import sys
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route

from github_mcp.config import PROJECT_ROOT, ServerConfig, get_configuration_status
from github_mcp.errors import (
    GitHubAuthError,
    GitHubError,
    GitHubPermissionError,
    GitHubRateLimitError,
    GitHubTimeoutError,
)
from github_mcp.github_client import GitHubClient
from github_mcp.ml_analyzer import MLRepositoryAnalyzer
from github_mcp.server import create_server

logger = logging.getLogger("github_mcp.ui")


def get_mcp_tools_metadata() -> list[dict[str, Any]]:
    """Extract metadata and schemas from registered MCP tools."""
    server = create_server()
    tools_data = []

    for name, tool_obj in server._tool_manager._tools.items():
        fn = tool_obj.fn
        sig = inspect.signature(fn)
        params = []
        for param_name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation is int:
                param_type = "integer"
            elif param.annotation is bool:
                param_type = "boolean"

            default_val = None if param.default is inspect.Parameter.empty else param.default
            is_required = param.default is inspect.Parameter.empty

            params.append(
                {
                    "name": param_name,
                    "type": param_type,
                    "required": is_required,
                    "default": default_val,
                }
            )

        tools_data.append(
            {
                "name": name,
                "description": tool_obj.description or "",
                "parameters": params,
                "transport": "stdio",
            }
        )

    return tools_data


def generate_client_configs() -> dict[str, Any]:
    """Generate exact, copyable MCP client configuration snippets using the real environment paths."""
    py_exec = sys.executable
    project_dir = str(PROJECT_ROOT.resolve())

    claude_desktop_config = {
        "mcpServers": {
            "github-mcp": {
                "command": py_exec,
                "args": ["-m", "github_mcp"],
                "cwd": project_dir,
            }
        }
    }

    antigravity_config = {
        "mcp_servers": {
            "github-mcp": {
                "command": py_exec,
                "args": ["-m", "github_mcp"],
                "cwd": project_dir,
            }
        }
    }

    cursor_config = {
        "name": "github-mcp",
        "type": "command",
        "command": f'"{py_exec}" -m github_mcp',
    }

    generic_stdio_config = {
        "server_name": "github-mcp-server",
        "transport": "stdio",
        "executable": py_exec,
        "arguments": ["-m", "github_mcp"],
        "working_directory": project_dir,
    }

    return {
        "python_executable": py_exec,
        "project_directory": project_dir,
        "claude_desktop": {
            "file_location": "%APPDATA%\\Claude\\claude_desktop_config.json (Windows) or ~/Library/Application Support/Claude/claude_desktop_config.json (macOS)",
            "snippet": json.dumps(claude_desktop_config, indent=2),
        },
        "antigravity": {
            "file_location": ".gemini/antigravity/mcp_config.json or workspace configuration",
            "snippet": json.dumps(antigravity_config, indent=2),
        },
        "cursor": {
            "file_location": "Cursor Settings > Features > MCP > Add New MCP Server",
            "snippet": json.dumps(cursor_config, indent=2),
        },
        "generic_stdio": {
            "file_location": "Any MCP-compatible client supporting stdio JSON-RPC",
            "snippet": json.dumps(generic_stdio_config, indent=2),
        },
    }


# ============================================================================
# API Route Handlers
# ============================================================================


def _extract_rate_limit(client: Any) -> dict[str, Any]:
    """Safely extract rate limit dictionary from client, handling mock instances gracefully."""
    try:
        info = client.get_rate_limit_info()
        if isinstance(info, dict):
            return info
    except Exception:
        pass
    return {}


async def api_status(request: Request) -> Response:
    """Return runtime configuration, GitHub authentication status, and rate limit diagnostics."""
    cfg = ServerConfig.from_env()
    status = get_configuration_status(cfg)
    status["transport"] = "stdio"
    status["version"] = "0.1.0"
    status["tools_available"] = 5
    return JSONResponse(status)


async def api_tools(request: Request) -> Response:
    """Return metadata and schemas of the 5 implemented MCP tools."""
    tools = get_mcp_tools_metadata()
    return JSONResponse({"tools": tools, "count": len(tools)})


async def api_client_configs(request: Request) -> Response:
    """Return copyable configurations for MCP clients."""
    configs = generate_client_configs()
    return JSONResponse(configs)


async def api_list_repositories(request: Request) -> Response:
    """Search and list repositories for a username with optional filters."""
    username = request.query_params.get("username", "").strip() or None
    name_filter = request.query_params.get("name_filter", "").strip() or None
    language_filter = request.query_params.get("language_filter", "").strip() or None

    cfg = ServerConfig.from_env()
    try:
        async with GitHubClient(config=cfg) as client:
            repos = await client.list_repositories(
                username=username,
                name_filter=name_filter,
                language_filter=language_filter,
                per_page=100,
                max_pages=3,
            )
            return JSONResponse(
                {
                    "count": len(repos),
                    "authenticated": cfg.has_token,
                    "rate_limit": _extract_rate_limit(client),
                    "filters": {
                        "username": username or "(authenticated user)",
                        "name_filter": name_filter,
                        "language_filter": language_filter,
                    },
                    "repositories": [repo.model_dump() for repo in repos],
                }
            )
    except GitHubTimeoutError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubRateLimitError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
                "is_secondary": e.is_secondary,
                "reset_time": e.reset_time,
                "retry_after": e.retry_after,
            },
            status_code=200,
        )
    except GitHubPermissionError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubAuthError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except Exception as e:
        logger.exception("Error in api_list_repositories")
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            },
            status_code=200,
        )


async def api_get_repository_details(request: Request) -> Response:
    """Fetch repository metadata and details."""
    owner = request.path_params["owner"]
    repo = request.path_params["repo"]

    cfg = ServerConfig.from_env()
    try:
        async with GitHubClient(config=cfg) as client:
            details = await client.get_repository_details(owner=owner, repo=repo)
            result = details.model_dump()
            result["_authenticated"] = cfg.has_token
            result["_rate_limit"] = _extract_rate_limit(client)
            return JSONResponse(result)
    except GitHubTimeoutError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubRateLimitError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
                "is_secondary": e.is_secondary,
                "reset_time": e.reset_time,
                "retry_after": e.retry_after,
            },
            status_code=200,
        )
    except GitHubPermissionError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubAuthError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except Exception as e:
        logger.exception("Error in api_get_repository_details")
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            },
            status_code=200,
        )


async def api_get_repository_tree(request: Request) -> Response:
    """Fetch repository directory structure and file tree."""
    owner = request.path_params["owner"]
    repo = request.path_params["repo"]
    branch = request.query_params.get("branch", "").strip() or None

    cfg = ServerConfig.from_env()
    try:
        async with GitHubClient(config=cfg) as client:
            tree = await client.get_repository_tree(
                owner=owner, repo=repo, branch=branch, recursive=True
            )
            result = tree.model_dump()
            result["_authenticated"] = cfg.has_token
            result["_rate_limit"] = _extract_rate_limit(client)
            return JSONResponse(result)
    except GitHubTimeoutError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubRateLimitError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubPermissionError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubAuthError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except Exception as e:
        logger.exception("Error in api_get_repository_tree")
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            },
            status_code=200,
        )


async def api_get_file_contents(request: Request) -> Response:
    """Fetch file content from a repository."""
    owner = request.path_params["owner"]
    repo = request.path_params["repo"]
    path = request.query_params.get("path", "").strip()
    branch = request.query_params.get("branch", "").strip() or None

    if not path:
        return JSONResponse(
            {"error": True, "message": "Missing required query parameter: 'path'"}, status_code=200
        )

    cfg = ServerConfig.from_env()
    try:
        async with GitHubClient(config=cfg) as client:
            file_obj = await client.get_file_contents(
                owner=owner, repo=repo, path=path, branch=branch
            )
            result = file_obj.model_dump()
            result["_authenticated"] = cfg.has_token
            result["_rate_limit"] = _extract_rate_limit(client)
            return JSONResponse(result)
    except GitHubTimeoutError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubRateLimitError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubPermissionError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubAuthError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except Exception as e:
        logger.exception("Error in api_get_file_contents")
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            },
            status_code=200,
        )


async def api_analyze_ml_repository(request: Request) -> Response:
    """Conduct ML portfolio analysis on a repository."""
    owner = request.path_params["owner"]
    repo = request.path_params["repo"]
    branch = request.query_params.get("branch", "").strip() or None

    cfg = ServerConfig.from_env()
    try:
        async with GitHubClient(config=cfg) as client:
            analyzer = MLRepositoryAnalyzer(client=client)
            analysis = await analyzer.analyze(owner=owner, repo=repo, branch=branch)
            result = analysis.model_dump()
            result["_authenticated"] = cfg.has_token
            result["_rate_limit"] = _extract_rate_limit(client)
            return JSONResponse(result)
    except GitHubTimeoutError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "ConnectTimeout" if e.is_connect_timeout else "ReadTimeout",
                "message": str(e),
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubRateLimitError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "RateLimitExceeded",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubPermissionError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "PermissionDenied",
                "message": str(e),
                "status_code": 403,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubAuthError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": "AuthenticationFailed",
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except GitHubError as e:
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": str(e),
                "status_code": e.status_code,
                "authenticated": cfg.has_token,
            },
            status_code=200,
        )
    except Exception as e:
        logger.exception("Error in api_analyze_ml_repository")
        return JSONResponse(
            {
                "error": True,
                "error_type": type(e).__name__,
                "message": f"Unexpected error: {type(e).__name__} - {e}",
            },
            status_code=200,
        )


async def render_ui(request: Request) -> Response:
    """Serve the client-facing single-page application."""
    from github_mcp.ui_html import HTML_TEMPLATE

    return HTMLResponse(HTML_TEMPLATE)


# ============================================================================
# Application Factory
# ============================================================================


def create_ui_app() -> Starlette:
    """Create and configure the Starlette web application."""
    routes = [
        Route("/", endpoint=render_ui, methods=["GET"]),
        Route("/api/status", endpoint=api_status, methods=["GET"]),
        Route("/api/tools", endpoint=api_tools, methods=["GET"]),
        Route("/api/client-configs", endpoint=api_client_configs, methods=["GET"]),
        Route("/api/repos", endpoint=api_list_repositories, methods=["GET"]),
        Route("/api/repos/{owner}/{repo}", endpoint=api_get_repository_details, methods=["GET"]),
        Route("/api/repos/{owner}/{repo}/tree", endpoint=api_get_repository_tree, methods=["GET"]),
        Route("/api/repos/{owner}/{repo}/file", endpoint=api_get_file_contents, methods=["GET"]),
        Route(
            "/api/repos/{owner}/{repo}/analyze",
            endpoint=api_analyze_ml_repository,
            methods=["POST", "GET"],
        ),
    ]

    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    return Starlette(debug=False, routes=routes, middleware=middleware)


def run_ui_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Launch the client-facing UI application with Uvicorn."""
    app = create_ui_app()
    cfg = ServerConfig.from_env()
    status = get_configuration_status(cfg)

    print("\n" + "=" * 65)
    print("  GitHub MCP Server - Client-Facing Assistant UI")
    print("=" * 65)
    print(f"  Web Interface URL : http://{host}:{port}")
    print(f"  GitHub API Base   : {status['api_url']}")
    print(
        f"  Authentication    : {'CONFIGURED (5,000 req/hr)' if status['token_configured'] else 'UNAUTHENTICATED (60 req/hr limit)'}"
    )
    print("  MCP Transport     : stdio (for connected AI clients)")
    print("=" * 65 + "\n")

    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    run_ui_server()
