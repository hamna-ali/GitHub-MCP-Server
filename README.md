# GitHub Model Context Protocol (MCP) Server for ML Project Portfolios

An asynchronous Model Context Protocol (MCP) server engineered in Python 3.12 that connects AI coding assistants directly to GitHub to discover, inspect, and analyze machine learning repositories. Built specifically for technical screen-sharing demonstrations, portfolio evaluations, and technical interviews.

---

## 1. Architecture Overview

```
                          ┌──────────────────────────────┐
                          │   AI Assistant / MCP Client  │
                          │ (Antigravity, Claude, etc.)  │
                          └──────────────┬───────────────┘
                                         │  stdio (JSON-RPC)
                                         ▼
                     ┌───────────────────────────────────────┐
                     │           GitHub MCP Server           │
                     │       (mcp.server.mcpserver)          │
                     └───────────────────┬───────────────────┘
                                         │
        ┌────────────────────────────────┼────────────────────────────────┐
        │                                │                                │
        ▼                                ▼                                ▼
┌─────────────────┐            ┌──────────────────┐             ┌──────────────────┐
│   MCP Tools     │            │  GitHub Client   │             │   ML Analyzer    │
│                 │            │  (Async HTTP)    │             │                  │
│ • list_repos    │◄───────────┤ • Pagination     │◄────────────┤ • Problem Stmt   │
│ • get_details   │            │ • Rate Limiting  │             │ • ML Frameworks  │
│ • get_tree      │            │ • Token Masking  │             │ • Architecture   │
│ • get_file      │            │ • Tree & Blobs   │             │ • Datasets       │
│ • analyze_ml    │            └────────┬─────────┘             │ • Training Loop  │
└─────────────────┘                     │                       │ • Evaluation     │
                                        │ HTTPS                 │ • Deployment     │
                                        ▼                       └──────────────────┘
                          ┌──────────────────────────────┐
                          │       GitHub REST API        │
                          │   (https://api.github.com)   │
                          └──────────────────────────────┘
```

- **Transport**: Standard Input/Output (`stdio`) JSON-RPC via official `mcp` SDK.
- **HTTP Engine**: Asynchronous non-blocking `httpx.AsyncClient` with automatic pagination, rate-limit header parsing, and connection pooling.
- **Security**: Strict token isolation; zero credential leakage in error messages, representations, or execution logs.
- **Verification Engine**: Heuristic and deterministic AST/regex parser in `MLRepositoryAnalyzer` that inspects repository trees, configuration manifests (`requirements.txt`, `pyproject.toml`, `environment.yml`), and documentation to verify ML architectures and pipelines while clearly flagging unverified claims.

---

## 2. Implemented MCP Tools

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| `list_repositories` | `name_filter` (opt), `language_filter` (opt), `username` (opt) | Lists repositories accessible to the user or specified GitHub account, with case-insensitive name and language filtering. |
| `get_repository_details` | `owner`, `repo` | Fetches metadata: description, primary language, topics, license, default branch, clone URLs, stars, and timestamps. |
| `get_repository_tree` | `owner`, `repo`, `branch` (opt), `recursive` (opt) | Retrieves full directory and file tree using the Git Trees API, supporting branch selection. |
| `get_file_contents` | `owner`, `repo`, `path`, `branch` (opt), `max_size_bytes` (opt) | Reads and decodes file contents (README, source code, configs). Safely flags directories and truncates oversized files. |
| `analyze_ml_repository` | `owner`, `repo`, `branch` (opt) | Evaluates ML problem statement, frameworks, model backbone, datasets, training loop, evaluation metrics, and deployment readiness. |

---

## 3. Project File Structure

```
GitHub-MCP-Server/
├── .env.example              # Placeholder environment configuration template
├── .gitignore                # Protects secrets, .venv, caches, and build artifacts
├── pyproject.toml            # Project packaging, dependencies, pytest, and ruff settings
├── README.md                 # Complete documentation, demo prompts, and architecture guide
├── src/
│   └── github_mcp/
│       ├── __init__.py       # Package version declaration
│       ├── __main__.py       # CLI executable entrypoint (`python -m github_mcp`)
│       ├── config.py         # Pydantic configuration and credential masking
│       ├── errors.py         # Custom exceptions guaranteeing zero token leakage
│       ├── models.py         # Pydantic data models for structured inputs/outputs
│       ├── github_client.py  # Asynchronous HTTP client for GitHub REST API
│       ├── ml_analyzer.py    # Domain verification engine for ML repositories
│       └── server.py         # Official MCP server implementation
└── tests/
    ├── __init__.py
    ├── conftest.py           # Pytest fixtures and mock GitHub REST payloads
    ├── test_config.py        # Configuration and secret masking verification
    ├── test_errors.py        # Custom exception hierarchy and safety tests
    ├── test_github_client.py # Mocked HTTP tests (pagination, rate limits, 404, errors)
    ├── test_ml_analyzer.py   # ML verification tests (full ML, tabular, non-ML, missing doc)
    └── test_server.py        # MCP server tool registration and routing tests
```

---

## 4. Setup and Installation

### Prerequisites
- Python 3.12+ (tested on Python 3.12.1)
- Git

### Step-by-Step Installation

1. **Clone or open the repository**:
   ```bash
   cd "d:\ML Projects\GitHub-MCP-Server"
   ```

2. **Create and activate a virtual environment**:
   ```powershell
   # Windows PowerShell:
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -e .
   pip install pytest pytest-asyncio ruff
   ```

4. **Configure your GitHub Personal Access Token**:
   Copy `.env.example` to `.env`:
   ```powershell
   Copy-Item .env.example .env
   ```
   Open `.env` in your editor and insert your GitHub token:
   ```env
   GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_actual_token_here
   GITHUB_API_URL=https://api.github.com
   ```

---

## 5. Creating a GitHub Token with Minimum Required Permissions

To follow the principle of least privilege, create a token with **read-only** permissions:

1. Log in to your GitHub account and go to **Settings** > **Developer settings** > **Personal access tokens**.
2. **Option A: Fine-Grained Personal Access Token (Recommended)**:
   - Click **Generate new token**.
   - **Repository access**: Select *"All repositories"* or *"Only select repositories"* (choose your ML portfolio repos).
   - **Permissions**:
     - `Contents`: Read-only (allows reading README, code, and config files).
     - `Metadata`: Read-only (mandatory default, allows reading repo details and tree).
3. **Option B: Classic Personal Access Token**:
   - Check `public_repo` (access to public repositories).
   - If analyzing private repositories, select `repo` (Full control of private repositories - read operations only will be used).
4. Click **Generate token** and copy the string into your `.env` file as `GITHUB_PERSONAL_ACCESS_TOKEN`.
5. **Security Guarantee**: The server only performs `GET` requests against the GitHub REST API and never exposes the token in tool returns, logs, or error responses.

---

## 6. Local MCP Client Configuration

### Connecting to Antigravity / Claude Desktop / Cursor / VSCode

Add the server to your MCP client configuration file (e.g., `mcp_config.json` or `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "github-portfolio-mcp": {
      "command": "d:\\ML Projects\\GitHub-MCP-Server\\.venv\\Scripts\\python.exe",
      "args": [
        "-m",
        "github_mcp"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
      }
    }
  }
}
```

*Note: Replace `d:\\ML Projects\\GitHub-MCP-Server` with your actual workspace path if installed in another directory.*

### Testing with Official MCP Inspector

You can run and test all tools interactively in your browser using the official MCP Inspector:

```powershell
npx @modelcontextprotocol/inspector .\.venv\Scripts\python.exe -m github_mcp
```

---

## 7. Running Tests and Verification

### Run the Automated Test Suite (30 unit & integration tests)
```powershell
.\.venv\Scripts\pytest.exe -v
```
*Expected result*: `30 passed` in ~2.5 seconds.

### Run Code Formatting and Lint Checks
```powershell
.\.venv\Scripts\ruff.exe check src tests
.\.venv\Scripts\ruff.exe format --check src tests
```

### Launch the Server Manually
```powershell
.\.venv\Scripts\python.exe -m github_mcp
```
*(Server listens on stdio for JSON-RPC messages from the MCP client)*

---

## 8. Live-Demo Script (5 Natural-Language Prompts)

During your screen-sharing presentation, demonstrate the end-to-end integration by asking the AI assistant these 5 progressive prompts:

### Prompt 1: Portfolio Discovery
> *"Can you use our GitHub MCP server to list all repositories in my account, and filter specifically for projects written in Python?"*
- **Tool invoked**: `list_repositories(language_filter="Python")`
- **What to highlight**: The assistant dynamically retrieves accessible repositories, star counts, descriptions, and update timestamps.

### Prompt 2: Metadata and Architecture Inspection
> *"Retrieve the details for the repository '<owner>/<repo>', and check its primary language, topics, license, and default branch."*
- **Tool invoked**: `get_repository_details(owner="...", repo="...")`
- **What to highlight**: Demonstrates structured extraction of tags, license compliance (e.g. MIT/Apache-2.0), and git URLs.

### Prompt 3: Directory and File Structure Exploration
> *"Show me the directory tree of this repository. Does it follow a standard ML project structure with separate data, models, and training directories?"*
- **Tool invoked**: `get_repository_tree(owner="...", repo="...", recursive=True)`
- **What to highlight**: Recursive tree inspection identifies key directories (`src/`, `models/`, `data/`) and detects weights files or notebooks.

### Prompt 4: Inspecting Model Training and Config Files
> *"Read the requirements.txt and README.md files for this repository to see the exact library versions and training setup."*
- **Tool invoked**: `get_file_contents(owner="...", repo="...", path="requirements.txt")` and `get_file_contents(owner="...", repo="...", path="README.md")`
- **What to highlight**: Safe decoding of file contents, handling of size limits, and absence of raw token leakage.

### Prompt 5: Automated Deep ML Portfolio Analysis
> *"Perform a full ML portfolio analysis on '<owner>/<repo>'. Summarize its problem statement, ML frameworks, model backbone, datasets, evaluation metrics, and deployment approach. Make sure to distinguish what is verified in the code from what is unverified."*
- **Tool invoked**: `analyze_ml_repository(owner="...", repo="...")`
- **What to highlight**: The tool returns a structured breakdown marking fields as `[DOCUMENTED]` (with exact citations to lines/files) vs `[UNVERIFIED]`, providing an instant assessment of code quality and engineering maturity.

---

## 9. Feature Summary and Limitations

### Implemented Features
- [x] Full MCP stdio transport compatibility with MCP SDK 2.x (`mcp.server.mcpserver`).
- [x] Asynchronous GitHub REST API client with retry and error translation.
- [x] Resilient handling of HTTP 401 (Auth), 403/429 (Rate Limit with reset timestamp), 404 (Missing resource), and network dropouts.
- [x] Safe file reader handling base64 decoding, directories, and large files.
- [x] Domain-aware ML repository verification engine checking for 30+ ML frameworks across Deep Learning, Tabular ML, NLP, CV, MLOps, and Serving.
- [x] Strict verification classification (`documented`, `inferred`, `unverified`) with concrete evidence citations.
- [x] 100% automated test coverage (30 passing tests) across client, analyzer, server, and config.
- [x] Zero credential exposure guarantee.

### Current Limitations & Future Enhancements
- **Rate Limits for Unauthenticated Access**: Unauthenticated GitHub API calls are limited by GitHub to 60 requests/hour. Configuring a personal access token raises the limit to 5,000 requests/hour.
- **Read-Only Scope**: The server intentionally supports only read operations (`GET`). Pull request creation, issue creation, and git push are explicitly omitted to ensure safety during demos.
- **Git Tree Truncation**: Repositories containing more than 100,000 files may have their tree truncated by GitHub's Tree API; the server detects and flags the `truncated=True` flag if this occurs.
