"""Tests for MCP server tool registration, routing, and error responses."""

from unittest import mock

import pytest

from github_mcp.errors import GitHubNotFoundError
from github_mcp.models import (
    RepositoryDetails,
    RepositorySummary,
)
from github_mcp.server import create_server


def test_server_initialization_and_tool_registration(test_config):
    server = create_server(config=test_config)
    assert server.name == "github-mcp-server"

    tool_names = list(server._tool_manager._tools.keys())
    expected_tools = [
        "list_repositories",
        "get_repository_details",
        "get_repository_tree",
        "get_file_contents",
        "analyze_ml_repository",
    ]
    for tool in expected_tools:
        assert tool in tool_names, f"Expected tool '{tool}' not found in registered tools"


@pytest.mark.asyncio
async def test_server_list_repositories_tool_success(test_config):
    server = create_server(config=test_config)
    tool_fn = server._tool_manager._tools["list_repositories"].fn

    mock_summary = RepositorySummary(
        id=1,
        name="test-repo",
        full_name="user/test-repo",
        owner="user",
        description="ML test repo",
        language="Python",
        default_branch="main",
        html_url="https://github.com/user/test-repo",
        is_private=False,
    )

    with mock.patch("github_mcp.server.GitHubClient") as mock_client_cls:
        mock_instance = mock.AsyncMock()
        mock_instance.list_repositories.return_value = [mock_summary]
        mock_client_cls.return_value.__aenter__.return_value = mock_instance

        result = await tool_fn(name_filter="test", language_filter="Python")
        assert result["count"] == 1
        assert result["authenticated"] is True
        assert result["repositories"][0]["name"] == "test-repo"
        assert result["filters"]["name_filter"] == "test"


@pytest.mark.asyncio
async def test_server_get_repository_details_tool_success(test_config):
    server = create_server(config=test_config)
    tool_fn = server._tool_manager._tools["get_repository_details"].fn

    mock_details = RepositoryDetails(
        id=1,
        name="test-repo",
        full_name="user/test-repo",
        owner="user",
        description="ML test repo",
        language="Python",
        default_branch="main",
        html_url="https://github.com/user/test-repo",
        clone_url="https://github.com/user/test-repo.git",
        topics=["ml", "deep-learning"],
    )

    with mock.patch("github_mcp.server.GitHubClient") as mock_client_cls:
        mock_instance = mock.AsyncMock()
        mock_instance.get_repository_details.return_value = mock_details
        mock_client_cls.return_value.__aenter__.return_value = mock_instance

        result = await tool_fn(owner="user", repo="test-repo")
        assert result["name"] == "test-repo"
        assert result["topics"] == ["ml", "deep-learning"]


@pytest.mark.asyncio
async def test_server_get_file_contents_tool_error_handling(test_config):
    server = create_server(config=test_config)
    tool_fn = server._tool_manager._tools["get_file_contents"].fn

    with mock.patch("github_mcp.server.GitHubClient") as mock_client_cls:
        mock_instance = mock.AsyncMock()
        mock_instance.get_file_contents.side_effect = GitHubNotFoundError(
            "File not found: missing.py"
        )
        mock_client_cls.return_value.__aenter__.return_value = mock_instance

        result = await tool_fn(owner="user", repo="test-repo", path="missing.py")
        assert result["error"] is True
        assert "File not found" in result["message"]
        assert result["status_code"] == 404
