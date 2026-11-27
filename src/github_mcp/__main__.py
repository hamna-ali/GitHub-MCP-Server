"""Executable module entrypoint for `python -m github_mcp`.

Supports:
- Default (`python -m github_mcp`): Runs the official MCP server over stdio for AI assistants.
- UI Mode (`python -m github_mcp --ui` or `python -m github_mcp ui`): Launches the client-facing web application.
"""

import sys


def main() -> None:
    """Route execution between MCP stdio server and client-facing Web UI."""
    args = sys.argv[1:]
    if any(arg in ("--ui", "--web", "ui", "web") for arg in args):
        port = 8000
        for i, arg in enumerate(args):
            if arg in ("--port", "-p") and i + 1 < len(args):
                try:
                    port = int(args[i + 1])
                except ValueError:
                    port = 8000
        from github_mcp.ui import run_ui_server

        run_ui_server(port=port)
    else:
        from github_mcp.server import main as server_main

        server_main()


if __name__ == "__main__":
    main()
