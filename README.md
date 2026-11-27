# GitHub Model Context Protocol (MCP) Server & Client-Facing Portfolio Assistant

An asynchronous Model Context Protocol (MCP) server and polished client-facing assistant interface engineered in Python 3.12. Connects AI coding assistants and non-technical reviewers directly to GitHub to discover, inspect, and evaluate machine learning repositories with verified evidence. Built specifically for technical screen-sharing demonstrations, portfolio evaluations, and technical interviews.

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

- **Dual-Interface Architecture**:
  1. **Official MCP stdio Server**: Runs locally over standard input/output (`stdio`) for AI assistants (`python -m github_mcp`).
  2. **Client-Facing Web Assistant**: Runs on `http://localhost:8000` via Starlette and Uvicorn (`python scripts/launch_ui.py` or `python -m github_mcp --ui`).
- **HTTP Engine**: Asynchronous non-blocking `httpx.AsyncClient` with automatic pagination, rate-limit header parsing, in-memory caching, and connection pooling.
- **Security**: Strict token isolation; zero credential leakage in error messages, representations, or execution logs.
- **Verification Engine**: Heuristic and deterministic AST/regex parser in `MLRepositoryAnalyzer` that inspects repository trees, configuration manifests (`requirements.txt`, `pyproject.toml`, `environment.yml`), and documentation to verify ML architectures and pipelines while clearly flagging unverified claims.

---

## 2. Client-Facing Web Interface

The project includes an approachable, high-contrast, client-facing web application that replaces developer-only inspector views with a clean product experience:

- **Workspace / Home**: Real-time system diagnostics, GitHub API rate limit tier indicator (`5,000 req/hr` vs `60 req/hr`), and one-click portfolio discovery for `hamna-ali`.
- **Explore**: Search any GitHub account, filter by language or keywords, inspect repository metadata cards, and drill down into:
  - **ML Portfolio Analysis**: Problem statement, detected ML frameworks (verified in dependencies vs mentioned in README), model architectures, datasets, training loops, evaluation metrics, and deployment readiness.
  - **Browse Files & Code**: Two-pane interactive file tree with formatted code viewer, line numbers, and truncation notices.
  - **Directory Tree**: Searchable tree structure with Git object types and file sizes.
  - **Advanced / Developer Details**: Expandable diagnostic accordion showing the underlying MCP tool invocations, parameter schemas, and raw JSON response for technical evaluators.
- **Connect Agent**: Step-by-step setup guides with copyable configuration snippets for Claude Desktop, Antigravity, and Cursor.
- **Activity**: In-session audit log tracking all queries, file reads, and ML evaluations.
- **Settings**: GitHub connection health, API URLs, and safe `.env` configuration guidance.

### Quick Start: Launching the Web UI
```powershell
.\.venv\Scripts\python.exe scripts\launch_ui.py
```
*(Or via module flag: `.\.venv\Scripts\python.exe -m github_mcp --ui`)*

Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 3. Implemented MCP Tools

| Tool Name | Parameters | Purpose |
| :--- | :--- | :--- |
| `list_repositories` | `name_filter` (opt), `language_filter` (opt), `username` (opt) | Lists repositories accessible to the user or specified GitHub account, with case-insensitive name and language filtering. |
| `get_repository_details` | `owner`, `repo` | Fetches metadata: description, primary language, topics, license, default branch, clone URLs, stars, and timestamps. |
| `get_repository_tree` | `owner`, `repo`, `branch` (opt), `recursive` (opt) | Retrieves full directory and file tree using the Git Trees API, supporting branch selection. |
| `get_file_contents` | `owner`, `repo`, `path`, `branch` (opt), `max_size_bytes` (opt) | Reads and decodes file contents (README, source code, configs). Safely flags directories and truncates oversized files. |
| `analyze_ml_repository` | `owner`, `repo`, `branch` (opt) | Evaluates ML problem statement, frameworks, model backbone, datasets, training loop, evaluation metrics, and deployment readiness. |

---

## 4. Project File Structure

```
GitHub-MCP-Server/
├── .env.example              # Placeholder environment configuration template
├── .gitignore                # Protects secrets, .venv, caches, and build artifacts
├── pyproject.toml            # Project packaging, dependencies, pytest, and ruff settings
├── README.md                 # Complete documentation, demo prompts, and architecture guide
├── scripts/
│   ├── launch_ui.py          # Standalone runner for the client-facing UI
│   └── verify_live.py        # Live integration verification script against GitHub API
├── src/
│   └── github_mcp/
│       ├── __init__.py       # Package version declaration
│       ├── __main__.py       # Dual entrypoint: stdio MCP server or Web UI (`--ui`)
│       ├── config.py         # Pydantic configuration, credential masking & safe check
│       ├── errors.py         # Custom exceptions guaranteeing zero token leakage
│       ├── models.py         # Pydantic data models for structured inputs/outputs
│       ├── github_client.py  # Asynchronous HTTP client for GitHub REST API with caching
│       ├── ml_analyzer.py    # Domain verification engine for ML repositories
│       ├── server.py         # Official MCP server implementation (stdio transport)
│       ├── ui.py             # Starlette application & API endpoints for client UI
│       └── ui_html.py        # Embedded responsive HTML/CSS/JS single-page application
└── tests/
    ├── __init__.py
    ├── conftest.py           # Pytest fixtures and mock GitHub REST payloads
    ├── test_config.py        # Configuration and secret masking verification
    ├── test_errors.py        # Custom exception hierarchy and safety tests
    ├── test_github_client.py # Mocked HTTP tests (headers, pagination, rate limits, 404)
    ├── test_ml_analyzer.py   # ML verification tests (full ML, tabular, non-ML, missing doc)
    ├── test_server.py        # MCP server tool registration and routing tests
    └── test_ui.py            # Starlette API endpoints and web UI tests
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

You can run and test all tools interactively in your browser using the official MCP Inspector.
The server automatically resolves `.env` from the project root regardless of the directory where the command is executed:

```powershell
npx @modelcontextprotocol/inspector "D:\ML Projects\GitHub-MCP-Server\.venv\Scripts\python.exe" -m github_mcp
```

Or from the repository root:
```powershell
npx @modelcontextprotocol/inspector .\.venv\Scripts\python.exe -m github_mcp
```

---

## 7. Running Tests and Verification

### Run the Automated Test Suite (51 unit & integration tests)
```powershell
.\.venv\Scripts\pytest.exe -v
```
*Expected result*: `51 passed` in ~3 seconds.

### Run Code Formatting and Lint Checks
```powershell
.\.venv\Scripts\ruff.exe check src tests scripts
.\.venv\Scripts\ruff.exe format --check src tests scripts
```

### Launch the Client-Facing Web UI
```powershell
.\.venv\Scripts\python.exe scripts\launch_ui.py
```
*(Starts the interactive web application at http://localhost:8000)*

### Launch the MCP Server Manually (stdio)
```powershell
.\.venv\Scripts\python.exe -m github_mcp
```
*(Server listens on stdio for JSON-RPC messages from the MCP client)*

### Run Automated Live GitHub API Verification
```powershell
.\.venv\Scripts\python.exe scripts\verify_live.py
```
*(Executes all 5 tools against real GitHub API endpoints for `hamna-ali/Customer-Churn-Prediction`)*

---

## 8. Live-Demo Script (5 Natural-Language Prompts)

During your screen-sharing presentation, demonstrate the end-to-end integration using your real GitHub account (`hamna-ali`) and ML repository (`Customer-Churn-Prediction`):

### Prompt 1: Portfolio Discovery
> *"Can you use our GitHub MCP server to list all repositories in my account (hamna-ali), and filter specifically for projects written in Python?"*
- **Tool invoked**: `list_repositories(username="hamna-ali", language_filter="Python")`
- **What to highlight**: The assistant dynamically retrieves accessible repositories, star counts, descriptions, and update timestamps.

### Prompt 2: Metadata and Architecture Inspection
> *"Retrieve the details for 'hamna-ali/Customer-Churn-Prediction', and check its primary language, topics, license, and default branch."*
- **Tool invoked**: `get_repository_details(owner="hamna-ali", repo="Customer-Churn-Prediction")`
- **What to highlight**: Demonstrates structured extraction of tags, license compliance, clone URLs, and default branch.

### Prompt 3: Directory and File Structure Exploration
> *"Show me the directory tree of Customer-Churn-Prediction. Does it follow a standard ML project structure with separate data, models, and training directories?"*
- **Tool invoked**: `get_repository_tree(owner="hamna-ali", repo="Customer-Churn-Prediction", recursive=True)`
- **What to highlight**: Recursive tree inspection identifies key directories (`app/`, `src/churn/models/`, `data/`) and detects weights files (`artifacts/best_model.joblib`) and notebooks (`notebooks/01_eda.ipynb`).

### Prompt 4: Inspecting Model Training and Config Files
> *"Read the requirements.txt and README.md files for Customer-Churn-Prediction to see the exact library versions and training setup."*
- **Tool invoked**: `get_file_contents(owner="hamna-ali", repo="Customer-Churn-Prediction", path="requirements.txt")` and `get_file_contents(owner="hamna-ali", repo="Customer-Churn-Prediction", path="README.md")`
- **What to highlight**: Safe decoding of file contents, handling of size limits, and absence of raw token leakage.

### Prompt 5: Automated Deep ML Portfolio Analysis
> *"Perform a full ML portfolio analysis on 'hamna-ali/Customer-Churn-Prediction'. Summarize its problem statement, ML frameworks, model backbone, datasets, evaluation metrics, and deployment approach. Make sure to distinguish what is verified in the code from what is unverified."*
- **Tool invoked**: `analyze_ml_repository(owner="hamna-ali", repo="Customer-Churn-Prediction")`
- **What to highlight**: The tool returns a structured breakdown marking fields as `[DOCUMENTED]` (with exact citations to lines/files) vs `[UNVERIFIED]`. Reuses in-memory cached responses to conserve GitHub API quota. Demonstrates verified detection of **Scikit-Learn**, **XGBoost**, **MLflow**, **FastAPI**, and **Streamlit** with a 1.0 confidence score!

---

## 9. Feature Summary and Limitations

### Implemented Features
- [x] Full MCP stdio transport compatibility with MCP SDK 2.x (`mcp.server.mcpserver`).
- [x] Asynchronous GitHub REST API client with retry and error translation.
- [x] Resilient handling of HTTP 401 (Auth), 403/429 (Rate Limit with reset timestamp), 404 (Missing resource), and network dropouts.
- [x] Safe file reader handling base64 decoding, directories, and large files.
- [x] Domain-aware ML repository verification engine checking for 30+ ML frameworks across Deep Learning, Tabular ML, NLP, CV, MLOps, and Serving.
- [x] Strict verification classification (`documented`, `inferred`, `unverified`) with concrete evidence citations.
- [x] Client-facing interactive Web UI on localhost (Starlette & Uvicorn) with live status diagnostics, repository browser, AST analysis view, and client setup guides.
- [x] 100% automated test coverage (51 passing tests) across client, analyzer, server, config, and web UI.
- [x] Zero credential exposure guarantee.

### Current Limitations & Future Enhancements
- **Rate Limits for Unauthenticated Access**: Unauthenticated GitHub API calls are limited by GitHub to 60 requests/hour. Configuring a personal access token raises the limit to 5,000 requests/hour.
- **Read-Only Scope**: The server intentionally supports only read operations (`GET`). Pull request creation, issue creation, and git push are explicitly omitted to ensure safety during demos.
- **Git Tree Truncation**: Repositories containing more than 100,000 files may have their tree truncated by GitHub's Tree API; the server detects and flags the `truncated=True` flag if this occurs.
