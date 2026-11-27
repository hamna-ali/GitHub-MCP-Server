"""Standalone runner script for launching the client-facing GitHub MCP Assistant UI."""

import argparse
import sys
from pathlib import Path

# Add project src to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from github_mcp.ui import run_ui_server  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser(description="Launch GitHub MCP Assistant Client UI")
    parser.add_argument("--host", default="127.0.0.1", help="Binding host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    parser.add_argument("--reload", action="store_true", help="Enable automatic reload")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_ui_server(host=args.host, port=args.port, reload=args.reload)
