"""Pydantic data models for structured inputs and outputs of GitHub MCP server."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class RepositorySummary(BaseModel):
    """Summary of a GitHub repository."""

    id: int = Field(description="GitHub repository ID")
    name: str = Field(description="Repository name")
    full_name: str = Field(description="Full repository name (owner/name)")
    owner: str = Field(description="Owner username or organization")
    description: Optional[str] = Field(default=None, description="Repository description")
    language: Optional[str] = Field(default=None, description="Primary programming language")
    default_branch: str = Field(description="Default branch name, e.g. main or master")
    html_url: str = Field(description="Web URL to the repository on GitHub")
    is_private: bool = Field(description="Whether the repository is private")
    stargazers_count: int = Field(default=0, description="Number of stars")
    forks_count: int = Field(default=0, description="Number of forks")
    open_issues_count: int = Field(default=0, description="Number of open issues")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp (ISO 8601)")


class RepositoryDetails(BaseModel):
    """Detailed metadata for a GitHub repository."""

    id: int = Field(description="GitHub repository ID")
    name: str = Field(description="Repository name")
    full_name: str = Field(description="Full repository name (owner/name)")
    owner: str = Field(description="Owner username or organization")
    description: Optional[str] = Field(default=None, description="Repository description")
    language: Optional[str] = Field(default=None, description="Primary programming language")
    default_branch: str = Field(description="Default branch name")
    html_url: str = Field(description="Web URL to repository")
    clone_url: str = Field(description="Git HTTPS clone URL")
    ssh_url: Optional[str] = Field(default=None, description="Git SSH clone URL")
    topics: list[str] = Field(default_factory=list, description="Repository topic tags")
    license_name: Optional[str] = Field(default=None, description="SPDX identifier or license name")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp (ISO 8601)")
    updated_at: Optional[str] = Field(default=None, description="Last update timestamp (ISO 8601)")
    pushed_at: Optional[str] = Field(default=None, description="Last push timestamp (ISO 8601)")
    size_kb: int = Field(default=0, description="Repository size in KB")
    stargazers_count: int = Field(default=0, description="Number of stars")
    forks_count: int = Field(default=0, description="Number of forks")
    open_issues_count: int = Field(default=0, description="Number of open issues")
    is_archived: bool = Field(default=False, description="Whether the repository is archived")
    is_fork: bool = Field(default=False, description="Whether the repository is a fork")


class TreeItem(BaseModel):
    """An individual file or directory in a Git tree."""

    path: str = Field(description="Relative path of file or directory")
    mode: str = Field(description="Git file mode")
    type: str = Field(description="Git object type ('blob' for file, 'tree' for directory)")
    size: Optional[int] = Field(default=None, description="File size in bytes (blobs only)")
    sha: str = Field(description="Git SHA of the object")


class RepositoryTree(BaseModel):
    """Directory structure tree of a repository."""

    owner: str = Field(description="Repository owner")
    repo: str = Field(description="Repository name")
    branch: str = Field(description="Branch or commit SHA queried")
    tree_sha: str = Field(description="Git SHA of the root tree")
    truncated: bool = Field(default=False, description="Whether GitHub truncated the tree result")
    total_items: int = Field(description="Number of items returned in tree")
    items: list[TreeItem] = Field(description="List of tree entries")


class FileContent(BaseModel):
    """Content and metadata of a file retrieved from GitHub."""

    path: str = Field(description="Path of the file in the repository")
    name: str = Field(description="File name")
    size_bytes: int = Field(description="Size of the file in bytes")
    encoding: str = Field(default="utf-8", description="Encoding format")
    content: str = Field(description="Decoded file content or summary message")
    is_truncated: bool = Field(
        default=False, description="Whether content was truncated due to size limit"
    )
    is_binary: bool = Field(default=False, description="Whether file appears to be binary")
    download_url: Optional[str] = Field(default=None, description="Raw download URL from GitHub")
    message: Optional[str] = Field(
        default=None, description="Notice or warning, e.g. truncation notice"
    )


VerificationStatus = Literal["documented", "unverified", "inferred"]


class AnalysisField(BaseModel):
    """Structured assessment field distinguishing verified/documented evidence from unverified claims."""

    status: VerificationStatus = Field(
        description="Whether this information is explicitly documented, unverified, or inferred"
    )
    details: str = Field(description="Detailed finding or description")
    evidence: list[str] = Field(
        default_factory=list,
        description="List of specific evidence items (e.g. file paths, config entries, or README excerpts)",
    )


class FrameworkItem(BaseModel):
    """Detected ML framework, library, or tool."""

    name: str = Field(description="Name of framework (e.g. PyTorch, HuggingFace Transformers)")
    category: str = Field(
        description="Category (e.g. Deep Learning, NLP, Computer Vision, MLOps, Serving)"
    )
    verified_in_dependencies: bool = Field(
        description="True if verified in requirements.txt, pyproject.toml, or environment.yml"
    )
    mentioned_in_readme: bool = Field(description="True if mentioned in repository documentation")
    evidence: str = Field(description="Exact dependency specification or documentation reference")


class MLRepositoryAnalysis(BaseModel):
    """Comprehensive, structured analysis of a Machine Learning repository."""

    repository: str = Field(description="Full repository name (owner/repo)")
    analyzed_branch: str = Field(description="Branch evaluated")
    is_ml_project: bool = Field(
        description="High-confidence indicator if this repository is an ML project"
    )
    ml_confidence_score: float = Field(
        ge=0.0, le=1.0, description="Confidence score that repo is an ML project (0.0 to 1.0)"
    )
    problem_statement: AnalysisField = Field(
        description="Project objective, problem definition, and task domain"
    )
    frameworks: list[FrameworkItem] = Field(
        default_factory=list,
        description="Identified ML/DL frameworks with dependency/documentation verification",
    )
    model_architecture: AnalysisField = Field(
        description="Model architecture, backbone, or algorithmic approach"
    )
    datasets: AnalysisField = Field(
        description="Datasets, data sources, preprocessing, or benchmarks used"
    )
    training_pipeline: AnalysisField = Field(
        description="Training setup, loss functions, optimizers, experiment tracking, or pipelines"
    )
    evaluation_metrics: AnalysisField = Field(
        description="Validation/test metrics, benchmarks, or evaluation protocols"
    )
    deployment_approach: AnalysisField = Field(
        description="Serving framework, containerization, API endpoints, or demo apps"
    )
    key_files_found: list[str] = Field(
        default_factory=list,
        description="Key ML and configuration files identified in repository tree",
    )
    summary_notes: str = Field(
        description="Executive summary highlighting portfolio-worthy strengths and unverified gaps"
    )
