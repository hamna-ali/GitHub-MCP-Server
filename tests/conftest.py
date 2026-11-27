"""Pytest fixtures and mock GitHub REST API responses."""

import base64

import pytest
from pydantic import SecretStr

from github_mcp.config import ServerConfig

# Sample repository payload
SAMPLE_REPOS = [
    {
        "id": 101,
        "name": "vision-transformer-classifier",
        "full_name": "ml-engineer/vision-transformer-classifier",
        "owner": {"login": "ml-engineer"},
        "description": "PyTorch Vision Transformer for fine-grained image classification",
        "language": "Python",
        "default_branch": "main",
        "html_url": "https://github.com/ml-engineer/vision-transformer-classifier",
        "private": False,
        "stargazers_count": 142,
        "forks_count": 28,
        "open_issues_count": 3,
        "updated_at": "2026-03-15T12:00:00Z",
    },
    {
        "id": 102,
        "name": "customer-churn-xgboost",
        "full_name": "ml-engineer/customer-churn-xgboost",
        "owner": {"login": "ml-engineer"},
        "description": "Production tabular churn prediction with XGBoost and Scikit-Learn",
        "language": "Python",
        "default_branch": "main",
        "html_url": "https://github.com/ml-engineer/customer-churn-xgboost",
        "private": False,
        "stargazers_count": 45,
        "forks_count": 8,
        "open_issues_count": 1,
        "updated_at": "2026-02-10T08:30:00Z",
    },
    {
        "id": 103,
        "name": "react-ml-dashboard",
        "full_name": "ml-engineer/react-ml-dashboard",
        "owner": {"login": "ml-engineer"},
        "description": "Frontend monitoring dashboard in TypeScript",
        "language": "TypeScript",
        "default_branch": "master",
        "html_url": "https://github.com/ml-engineer/react-ml-dashboard",
        "private": True,
        "stargazers_count": 12,
        "forks_count": 2,
        "open_issues_count": 0,
        "updated_at": "2026-01-05T14:20:00Z",
    },
]

# Detailed repository payload
SAMPLE_REPO_DETAILS = {
    "id": 101,
    "name": "vision-transformer-classifier",
    "full_name": "ml-engineer/vision-transformer-classifier",
    "owner": {"login": "ml-engineer"},
    "description": "PyTorch Vision Transformer for fine-grained image classification",
    "language": "Python",
    "default_branch": "main",
    "html_url": "https://github.com/ml-engineer/vision-transformer-classifier",
    "clone_url": "https://github.com/ml-engineer/vision-transformer-classifier.git",
    "ssh_url": "git@github.com:ml-engineer/vision-transformer-classifier.git",
    "topics": ["deep-learning", "pytorch", "vision-transformer", "computer-vision"],
    "license": {"spdx_id": "MIT", "name": "MIT License"},
    "created_at": "2025-06-01T10:00:00Z",
    "updated_at": "2026-03-15T12:00:00Z",
    "pushed_at": "2026-03-15T11:45:00Z",
    "size": 4200,
    "stargazers_count": 142,
    "forks_count": 28,
    "open_issues_count": 3,
    "archived": False,
    "fork": False,
}

# Git tree payload for ML repository
SAMPLE_ML_TREE = {
    "sha": "tree_sha_12345",
    "url": "https://api.github.com/repos/ml-engineer/vision-transformer-classifier/git/trees/tree_sha_12345",
    "truncated": False,
    "tree": [
        {"path": "README.md", "mode": "100644", "type": "blob", "sha": "blob_readme", "size": 1850},
        {
            "path": "requirements.txt",
            "mode": "100644",
            "type": "blob",
            "sha": "blob_reqs",
            "size": 320,
        },
        {
            "path": "pyproject.toml",
            "mode": "100644",
            "type": "blob",
            "sha": "blob_pyproject",
            "size": 650,
        },
        {"path": "Dockerfile", "mode": "100644", "type": "blob", "sha": "blob_docker", "size": 480},
        {"path": "src", "mode": "040000", "type": "tree", "sha": "tree_src"},
        {
            "path": "src/train.py",
            "mode": "100644",
            "type": "blob",
            "sha": "blob_train",
            "size": 3400,
        },
        {
            "path": "src/models/vit.py",
            "mode": "100644",
            "type": "blob",
            "sha": "blob_model",
            "size": 2900,
        },
        {
            "path": "src/data/dataset.py",
            "mode": "100644",
            "type": "blob",
            "sha": "blob_data",
            "size": 1800,
        },
        {
            "path": "src/evaluate.py",
            "mode": "100644",
            "type": "blob",
            "sha": "blob_eval",
            "size": 2100,
        },
        {
            "path": "src/serve.py",
            "mode": "100644",
            "type": "blob",
            "sha": "blob_serve",
            "size": 1500,
        },
    ],
}

# README content
SAMPLE_ML_README = """# Vision Transformer Classifier

## Overview
This project solves fine-grained multi-class image classification using a Vision Transformer (ViT-B/16) backbone fine-tuned on ImageNet and custom fine-grained datasets.

## Architecture
We use a Vision Transformer (ViT-B/16) with multi-head self-attention, pre-trained on ImageNet-21k. An MLP classification head is fine-tuned with cross-entropy loss and AdamW optimizer.

## Dataset
Trained on ImageNet validation subsets and CIFAR-100 benchmarks. Data preprocessing includes RandAugment and Albumentations for image transformations.

## Training Pipeline
Fine-tuning is implemented with PyTorch Lightning and logged using Weights & Biases (wandb).
Run training:
```bash
python src/train.py --epochs 50 --batch_size 64 --lr 3e-4 --wandb
```

## Evaluation & Results
Evaluated on holdout test benchmarks:
- Top-1 Accuracy: 89.4%
- Macro F1-Score: 0.887
- Inference Latency: 14ms on NVIDIA T4 GPU

## Deployment
Packaged as a lightweight containerized microservice with FastAPI and Docker.
```bash
docker build -t vit-service .
docker run -p 8000:8000 vit-service
```
"""

# Requirements.txt content
SAMPLE_ML_REQUIREMENTS = """torch>=2.2.0
torchvision>=0.17.0
pytorch-lightning>=2.1.0
transformers>=4.38.0
timm>=0.9.12
albumentations>=1.4.0
wandb>=0.16.0
fastapi>=0.110.0
uvicorn>=0.28.0
scikit-learn>=1.4.0
"""


def encode_github_content(text: str) -> dict:
    """Helper to encode text into GitHub Contents API response format."""
    encoded_bytes = base64.b64encode(text.encode("utf-8"))
    return {
        "name": "file.txt",
        "path": "file.txt",
        "size": len(text.encode("utf-8")),
        "encoding": "base64",
        "content": encoded_bytes.decode("ascii"),
        "sha": "mock_sha_12345",
        "type": "file",
        "download_url": "https://raw.githubusercontent.com/test/test/main/file.txt",
    }


@pytest.fixture
def test_config() -> ServerConfig:
    """Return a test server configuration with a mock secret token."""
    return ServerConfig(
        github_token=SecretStr("ghp_mocktesttoken1234567890abcdef"),
        github_api_url="https://api.github.com",
        request_timeout=5.0,
        max_file_size_bytes=500_000,
    )
