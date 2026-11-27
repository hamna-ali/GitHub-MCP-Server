"""Tests for Machine Learning repository analysis and verification logic."""

import httpx
import pytest

from github_mcp.github_client import GitHubClient
from github_mcp.ml_analyzer import MLRepositoryAnalyzer
from tests.conftest import (
    SAMPLE_ML_README,
    SAMPLE_ML_REQUIREMENTS,
    SAMPLE_ML_TREE,
    encode_github_content,
)


@pytest.mark.asyncio
async def test_analyze_full_ml_repository(test_config):
    readme_payload = encode_github_content(SAMPLE_ML_README)
    reqs_payload = encode_github_content(SAMPLE_ML_REQUIREMENTS)

    def handler(request: httpx.Request) -> httpx.Response:
        url_path = request.url.path
        if "/git/trees/" in url_path:
            return httpx.Response(200, json=SAMPLE_ML_TREE)
        if "/contents/README.md" in url_path:
            return httpx.Response(200, json=readme_payload)
        if "/contents/requirements.txt" in url_path:
            return httpx.Response(200, json=reqs_payload)
        if "/contents/pyproject.toml" in url_path:
            return httpx.Response(404, json={"message": "Not Found"})
        return httpx.Response(404, json={"message": "Not Found"})

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    analyzer = MLRepositoryAnalyzer(client=client)
    analysis = await analyzer.analyze(
        owner="ml-engineer", repo="vision-transformer-classifier", branch="main"
    )

    # 1. Project-level assessment
    assert analysis.is_ml_project is True
    assert analysis.ml_confidence_score >= 0.70
    assert analysis.repository == "ml-engineer/vision-transformer-classifier"

    # 2. Problem statement
    assert analysis.problem_statement.status == "documented"
    assert "classification" in analysis.problem_statement.details.lower()
    assert len(analysis.problem_statement.evidence) > 0

    # 3. ML Frameworks
    fw_names = [f.name for f in analysis.frameworks]
    assert "PyTorch" in fw_names
    assert "PyTorch Lightning" in fw_names
    assert "Hugging Face Transformers" in fw_names
    assert "Weights & Biases (W&B)" in fw_names
    assert "FastAPI" in fw_names

    # Check verified in dependencies
    torch_fw = next(f for f in analysis.frameworks if f.name == "PyTorch")
    assert torch_fw.verified_in_dependencies is True
    assert "requirements.txt" in torch_fw.evidence

    # 4. Architecture
    assert analysis.model_architecture.status == "documented"
    assert "Transformer" in analysis.model_architecture.details

    # 5. Datasets
    assert analysis.datasets.status == "documented"
    assert "ImageNet" in analysis.datasets.details

    # 6. Training Pipeline
    assert analysis.training_pipeline.status == "documented"
    assert (
        "Weights & Biases" in analysis.training_pipeline.details
        or "PyTorch" in analysis.training_pipeline.details
    )

    # 7. Evaluation metrics
    assert analysis.evaluation_metrics.status == "documented"
    assert "ACCURACY" in analysis.evaluation_metrics.details.upper()
    assert "F1" in analysis.evaluation_metrics.details.upper()

    # 8. Deployment approach
    assert analysis.deployment_approach.status == "documented"
    assert "FastAPI" in analysis.deployment_approach.details
    assert "Containerized" in analysis.deployment_approach.details

    # 9. Key files found
    assert "src/train.py" in analysis.key_files_found
    assert "src/models/vit.py" in analysis.key_files_found
    assert "Dockerfile" in analysis.key_files_found

    await client.close()


@pytest.mark.asyncio
async def test_analyze_non_ml_repository(test_config):
    """Test analysis on a non-ML utility repository."""
    non_ml_tree = {
        "sha": "non_ml_tree_sha",
        "url": "https://api.github.com/repos/user/string-utils/git/trees/main",
        "truncated": False,
        "tree": [
            {
                "path": "README.md",
                "mode": "100644",
                "type": "blob",
                "sha": "sha_readme",
                "size": 150,
            },
            {"path": "utils.py", "mode": "100644", "type": "blob", "sha": "sha_utils", "size": 300},
        ],
    }

    readme_content = """# String Utils
A simple Python library containing string formatting helpers.
"""
    readme_payload = encode_github_content(readme_content)

    def handler(request: httpx.Request) -> httpx.Response:
        url_path = request.url.path
        if "/git/trees/" in url_path:
            return httpx.Response(200, json=non_ml_tree)
        if "/contents/README.md" in url_path:
            return httpx.Response(200, json=readme_payload)
        return httpx.Response(404, json={"message": "Not Found"})

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    analyzer = MLRepositoryAnalyzer(client=client)
    analysis = await analyzer.analyze(owner="user", repo="string-utils", branch="main")

    assert analysis.is_ml_project is False
    assert analysis.ml_confidence_score < 0.35
    assert len(analysis.frameworks) == 0
    assert analysis.model_architecture.status == "unverified"
    assert analysis.datasets.status == "unverified"
    assert analysis.training_pipeline.status == "unverified"
    assert analysis.evaluation_metrics.status == "unverified"
    assert analysis.deployment_approach.status == "unverified"
    assert "Improvement Opportunity" in analysis.summary_notes

    await client.close()


@pytest.mark.asyncio
async def test_analyze_ml_repo_missing_readme(test_config):
    """Test ML repo that has ML code and requirements but no README."""
    tree = {
        "sha": "tree_sha",
        "url": "...",
        "truncated": False,
        "tree": [
            {
                "path": "requirements.txt",
                "mode": "100644",
                "type": "blob",
                "sha": "sha_reqs",
                "size": 100,
            },
            {
                "path": "train.py",
                "mode": "100644",
                "type": "blob",
                "sha": "sha_train",
                "size": 1000,
            },
            {
                "path": "model.py",
                "mode": "100644",
                "type": "blob",
                "sha": "sha_model",
                "size": 1000,
            },
        ],
    }
    reqs = encode_github_content("torch>=2.0.0\nscikit-learn\n")

    def handler(request: httpx.Request) -> httpx.Response:
        url_path = request.url.path
        if "/git/trees/" in url_path:
            return httpx.Response(200, json=tree)
        if "/contents/requirements.txt" in url_path:
            return httpx.Response(200, json=reqs)
        return httpx.Response(404, json={"message": "Not Found"})

    client = GitHubClient(config=test_config)
    client._client = httpx.AsyncClient(
        transport=httpx.MockTransport(handler), base_url="https://api.github.com"
    )

    analyzer = MLRepositoryAnalyzer(client=client)
    analysis = await analyzer.analyze(owner="user", repo="code-only-ml", branch="main")

    # Should still detect ML because of torch and train.py / model.py
    assert analysis.is_ml_project is True
    # But problem statement is unverified
    assert analysis.problem_statement.status == "unverified"
    # Architecture and pipeline are inferred from code files
    assert analysis.model_architecture.status == "inferred"
    assert analysis.training_pipeline.status == "inferred"

    await client.close()
