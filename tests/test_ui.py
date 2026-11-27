"""Tests for the client-facing Web UI and Starlette API endpoints."""

from unittest import mock

import pytest
from starlette.testclient import TestClient

from github_mcp.models import (
    AnalysisField,
    FileContent,
    MLRepositoryAnalysis,
    RepositoryDetails,
    RepositorySummary,
    RepositoryTree,
    TreeItem,
)
from github_mcp.ui import create_ui_app


@pytest.fixture
def client():
    app = create_ui_app()
    return TestClient(app)


def test_ui_index_html_serving(client):
    """Verify that GET / returns the client-facing UI HTML application."""
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert "GitHub MCP Assistant" in resp.text
    assert "Workspace" in resp.text
    assert "Connect Agent" in resp.text
    assert "ML Portfolio Analysis" in resp.text


def test_api_status_endpoint(client):
    """Verify that GET /api/status returns safe diagnostic metadata without tokens."""
    resp = client.get("/api/status")
    assert resp.status_code == 200
    data = resp.json()
    assert "api_url" in data
    assert "token_configured" in data
    assert data["transport"] == "stdio"
    assert data["tools_available"] == 5
    # Guarantee no secret fields exist in response
    assert "token" not in data
    assert "github_token" not in data


def test_api_tools_endpoint(client):
    """Verify that GET /api/tools enumerates all 5 MCP tools."""
    resp = client.get("/api/tools")
    assert resp.status_code == 200
    data = resp.json()
    assert data["count"] == 5
    tool_names = [t["name"] for t in data["tools"]]
    assert "list_repositories" in tool_names
    assert "get_repository_details" in tool_names
    assert "get_repository_tree" in tool_names
    assert "get_file_contents" in tool_names
    assert "analyze_ml_repository" in tool_names


def test_api_client_configs(client):
    """Verify that GET /api/client-configs returns copyable configs with resolved paths."""
    resp = client.get("/api/client-configs")
    assert resp.status_code == 200
    data = resp.json()
    assert "claude_desktop" in data
    assert "antigravity" in data
    assert "cursor" in data
    assert "generic_stdio" in data
    assert "python_executable" in data
    assert "-m" in data["claude_desktop"]["snippet"]
    assert "github_mcp" in data["claude_desktop"]["snippet"]


def test_api_list_repositories(client):
    """Verify GET /api/repos returns formatted repository summaries."""
    mock_summary = RepositorySummary(
        id=1,
        name="Customer-Churn-Prediction",
        full_name="hamna-ali/Customer-Churn-Prediction",
        owner="hamna-ali",
        description="Tabular ML churn model",
        language="Python",
        default_branch="main",
        html_url="https://github.com/hamna-ali/Customer-Churn-Prediction",
        is_private=False,
    )

    with mock.patch("github_mcp.ui.GitHubClient") as mock_client_cls:
        mock_instance = mock.AsyncMock()
        mock_instance.list_repositories.return_value = [mock_summary]
        mock_client_cls.return_value.__aenter__.return_value = mock_instance

        resp = client.get("/api/repos?username=hamna-ali")
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["repositories"][0]["name"] == "Customer-Churn-Prediction"


def test_api_get_repository_details(client):
    """Verify GET /api/repos/{owner}/{repo} returns metadata."""
    mock_details = RepositoryDetails(
        id=101,
        name="Customer-Churn-Prediction",
        full_name="hamna-ali/Customer-Churn-Prediction",
        owner="hamna-ali",
        description="Tabular ML churn model",
        language="Python",
        default_branch="main",
        html_url="https://github.com/hamna-ali/Customer-Churn-Prediction",
        clone_url="https://github.com/hamna-ali/Customer-Churn-Prediction.git",
        topics=["machine-learning", "xgboost"],
        license_name="MIT",
    )

    with mock.patch("github_mcp.ui.GitHubClient") as mock_client_cls:
        mock_instance = mock.AsyncMock()
        mock_instance.get_repository_details.return_value = mock_details
        mock_client_cls.return_value.__aenter__.return_value = mock_instance

        resp = client.get("/api/repos/hamna-ali/Customer-Churn-Prediction")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Customer-Churn-Prediction"
        assert data["license_name"] == "MIT"
        assert "xgboost" in data["topics"]


def test_api_get_repository_tree(client):
    """Verify GET /api/repos/{owner}/{repo}/tree returns tree items."""
    mock_tree = RepositoryTree(
        owner="hamna-ali",
        repo="Customer-Churn-Prediction",
        branch="main",
        tree_sha="tree_sha_123",
        truncated=False,
        total_items=2,
        items=[
            TreeItem(path="README.md", mode="100644", type="blob", size=100, sha="s1"),
            TreeItem(path="src", mode="040000", type="tree", sha="s2"),
        ],
    )

    with mock.patch("github_mcp.ui.GitHubClient") as mock_client_cls:
        mock_instance = mock.AsyncMock()
        mock_instance.get_repository_tree.return_value = mock_tree
        mock_client_cls.return_value.__aenter__.return_value = mock_instance

        resp = client.get("/api/repos/hamna-ali/Customer-Churn-Prediction/tree")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_items"] == 2
        assert data["items"][0]["path"] == "README.md"


def test_api_get_file_contents(client):
    """Verify GET /api/repos/{owner}/{repo}/file returns file content."""
    mock_file = FileContent(
        path="README.md",
        name="README.md",
        size_bytes=42,
        content="# Customer Churn Model\nPredict customer churn.",
        is_truncated=False,
        is_binary=False,
    )

    with mock.patch("github_mcp.ui.GitHubClient") as mock_client_cls:
        mock_instance = mock.AsyncMock()
        mock_instance.get_file_contents.return_value = mock_file
        mock_client_cls.return_value.__aenter__.return_value = mock_instance

        resp = client.get("/api/repos/hamna-ali/Customer-Churn-Prediction/file?path=README.md")
        assert resp.status_code == 200
        data = resp.json()
        assert data["path"] == "README.md"
        assert "Customer Churn Model" in data["content"]


def test_api_get_file_contents_missing_path(client):
    """Verify GET /api/repos/{owner}/{repo}/file without path returns helpful error."""
    resp = client.get("/api/repos/hamna-ali/Customer-Churn-Prediction/file")
    assert resp.status_code == 200
    data = resp.json()
    assert data["error"] is True
    assert "Missing required query parameter: 'path'" in data["message"]


def test_api_analyze_ml_repository(client):
    """Verify POST /api/repos/{owner}/{repo}/analyze returns structured ML analysis."""
    mock_analysis = MLRepositoryAnalysis(
        repository="hamna-ali/Customer-Churn-Prediction",
        analyzed_branch="main",
        is_ml_project=True,
        ml_confidence_score=0.92,
        problem_statement=AnalysisField(
            status="documented",
            details="Binary classification of customer churn.",
            evidence=["README.md"],
        ),
        frameworks=[],
        model_architecture=AnalysisField(
            status="documented",
            details="XGBoost Classifier with tree ensemble.",
            evidence=["model.py"],
        ),
        datasets=AnalysisField(
            status="documented",
            details="Telco churn tabular dataset.",
            evidence=["data/churn.csv"],
        ),
        training_pipeline=AnalysisField(
            status="documented",
            details="Scikit-learn pipeline with standard scaling.",
            evidence=["train.py"],
        ),
        evaluation_metrics=AnalysisField(
            status="documented",
            details="ROC-AUC of 0.85 and F1-score.",
            evidence=["evaluate.py"],
        ),
        deployment_approach=AnalysisField(
            status="unverified",
            details="No serving API or Dockerfile found.",
            evidence=[],
        ),
        key_files_found=["README.md", "requirements.txt", "train.py"],
        summary_notes="Well-structured tabular ML project with strong documentation.",
    )

    with mock.patch("github_mcp.ui.MLRepositoryAnalyzer") as mock_analyzer_cls:
        mock_instance = mock.AsyncMock()
        mock_instance.analyze.return_value = mock_analysis
        mock_analyzer_cls.return_value = mock_instance

        resp = client.post("/api/repos/hamna-ali/Customer-Churn-Prediction/analyze")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_ml_project"] is True
        assert data["ml_confidence_score"] == 0.92
        assert data["problem_statement"]["status"] == "documented"
        assert data["deployment_approach"]["status"] == "unverified"
