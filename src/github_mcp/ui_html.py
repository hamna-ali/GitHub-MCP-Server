"""Embedded HTML, CSS, and JavaScript for the client-facing GitHub MCP Assistant UI."""

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>GitHub MCP Assistant — ML Portfolio & Repository Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      /* GitHub Primer Design System Dark Palette */
      --bg-base: #0d1117;
      --bg-surface: #161b22;
      --bg-surface-elevated: #21262d;
      --bg-surface-hover: #30363d;
      --border-subtle: #21262d;
      --border-default: #30363d;
      --border-focus: #58a6ff;

      --text-main: #f0f6fc;
      --text-muted: #8b949e;
      --text-subtle: #6e7681;

      --accent-primary: #58a6ff;
      --accent-primary-hover: #79c0ff;
      --accent-primary-subtle: rgba(56, 139, 253, 0.15);

      --badge-success: #3fb950;
      --badge-success-bg: rgba(46, 160, 67, 0.15);
      --badge-warning: #d29922;
      --badge-warning-bg: rgba(187, 128, 9, 0.15);
      --badge-danger: #f85149;
      --badge-danger-bg: rgba(248, 81, 73, 0.15);
      --badge-neutral: #6e7681;
      --badge-neutral-bg: rgba(110, 118, 129, 0.15);

      --primer-tab-active: #f78166;

      --radius-sm: 6px;
      --radius-md: 6px;
      --radius-lg: 8px;
      --radius-pill: 20px;

      --shadow-sm: 0 1px 0 rgba(1, 4, 9, 0.8);
      --shadow-md: 0 3px 6px rgba(1, 4, 9, 0.4);
      --shadow-lg: 0 8px 24px rgba(1, 4, 9, 0.6);

      --font-sans: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
      --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      background-color: var(--bg-base);
      color: var(--text-main);
      font-family: var(--font-sans);
      font-size: 14px;
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }

    a {
      color: var(--accent-primary);
      text-decoration: none;
      transition: color 0.15s ease;
    }
    a:hover {
      color: #79c0ff;
    }

    /* GitHub Primer Top Navigation Bar */
    header.app-header {
      background-color: var(--bg-surface);
      border-bottom: 1px solid var(--border-default);
      position: sticky;
      top: 0;
      z-index: 50;
      padding: 0 1.5rem;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .brand-group {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .brand-icon {
      width: 32px;
      height: 32px;
      background: linear-gradient(135deg, #1f6feb, #238636);
      border-radius: var(--radius-md);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      box-shadow: 0 0 12px rgba(88, 166, 255, 0.25);
    }

    .brand-title {
      font-weight: 700;
      font-size: 1rem;
      letter-spacing: -0.01em;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .brand-tag {
      font-size: 0.7rem;
      font-weight: 600;
      padding: 2px 7px;
      background: var(--accent-primary-subtle);
      color: var(--accent-primary);
      border: 1px solid rgba(88, 166, 255, 0.3);
      border-radius: var(--radius-pill);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    /* Primer UnderlineNav */
    nav.main-nav {
      display: flex;
      align-items: center;
      gap: 0.35rem;
      height: 100%;
    }

    .nav-btn {
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      color: var(--text-muted);
      font-family: var(--font-sans);
      font-size: 14px;
      font-weight: 500;
      padding: 0 0.85rem;
      height: 100%;
      border-radius: 0;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.45rem;
      transition: color 0.12s ease, border-color 0.12s ease;
    }

    .nav-btn:hover {
      color: var(--text-main);
      border-bottom-color: var(--border-default);
    }

    .nav-btn.active {
      color: var(--text-main);
      border-bottom-color: var(--primer-tab-active);
      font-weight: 600;
    }

    .header-status-area {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 0.45rem;
      font-size: 0.75rem;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: var(--radius-pill);
      background-color: var(--bg-surface-elevated);
      border: 1px solid var(--border-default);
      color: var(--text-muted);
    }

    .status-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background-color: var(--badge-neutral);
    }

    .status-dot.active {
      background-color: var(--badge-success);
      box-shadow: 0 0 8px var(--badge-success);
    }

    .status-dot.warning {
      background-color: var(--badge-warning);
      box-shadow: 0 0 8px var(--badge-warning);
    }

    /* Layout Containers */
    main.app-content {
      flex: 1;
      max-width: 1280px;
      width: 100%;
      margin: 0 auto;
      padding: 1.75rem 1.5rem 3rem 1.5rem;
    }

    .view-pane {
      display: none;
    }
    .view-pane.active {
      display: block;
      animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Cards and Surfaces */
    .card {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 1.25rem;
      box-shadow: var(--shadow-sm);
    }

    .card-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border-subtle);
    }

    .card-title {
      font-size: 1rem;
      font-weight: 600;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    /* Hero Banner */
    .hero-banner {
      background: radial-gradient(circle at 10% 20%, rgba(56, 189, 248, 0.08) 0%, transparent 40%),
                  radial-gradient(circle at 90% 80%, rgba(99, 102, 241, 0.08) 0%, transparent 45%),
                  var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 2.25rem 2rem;
      margin-bottom: 2rem;
      position: relative;
      overflow: hidden;
    }

    .hero-title {
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
      margin-bottom: 0.65rem;
      color: var(--text-main);
      line-height: 1.25;
    }

    .hero-subtitle {
      font-size: 1rem;
      color: var(--text-muted);
      max-width: 680px;
      line-height: 1.6;
      margin-bottom: 1.5rem;
    }

    .hero-actions {
      display: flex;
      align-items: center;
      gap: 1rem;
      flex-wrap: wrap;
    }

    /* GitHub Primer Buttons */
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 0.45rem;
      font-family: var(--font-sans);
      font-size: 14px;
      font-weight: 500;
      padding: 5px 16px;
      border-radius: var(--radius-md);
      border: 1px solid var(--border-default);
      cursor: pointer;
      transition: all 0.15s ease;
      white-space: nowrap;
      line-height: 20px;
    }

    .btn:focus-visible {
      outline: 2px solid var(--border-focus);
      outline-offset: 2px;
    }

    .btn-primary {
      background-color: #238636;
      color: #ffffff;
      border-color: rgba(240, 246, 252, 0.1);
      font-weight: 600;
    }
    .btn-primary:hover {
      background-color: #2ea043;
      border-color: rgba(240, 246, 252, 0.1);
      color: #ffffff;
    }

    .btn-secondary {
      background-color: #21262d;
      color: #c9d1d9;
      border-color: var(--border-default);
    }
    .btn-secondary:hover {
      background-color: #30363d;
      border-color: #8b949e;
      color: #f0f6fc;
    }

    .btn-sm {
      padding: 3px 12px;
      font-size: 12px;
      line-height: 18px;
    }

    /* Grid Layouts */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .stat-card {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      padding: 1.15rem;
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }

    .stat-label {
      font-size: 0.8rem;
      font-weight: 500;
      color: var(--text-subtle);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .stat-value {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--text-main);
    }

    .stat-detail {
      font-size: 0.775rem;
      color: var(--text-muted);
    }

    /* Search & Filter Bar */
    .search-bar {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
      flex-wrap: wrap;
    }

    .input-group {
      display: flex;
      align-items: center;
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      padding: 0.45rem 0.75rem;
      gap: 0.5rem;
      flex: 1;
      min-width: 200px;
    }
    .input-group:focus-within {
      border-color: var(--border-focus);
      box-shadow: 0 0 0 2px var(--accent-primary-subtle);
    }

    .input-group svg {
      color: var(--text-subtle);
      flex-shrink: 0;
    }

    .input-field {
      background: transparent;
      border: none;
      color: var(--text-main);
      font-family: var(--font-sans);
      font-size: 0.875rem;
      width: 100%;
      outline: none;
    }
    .input-field::placeholder {
      color: var(--text-subtle);
    }

    select.select-field {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      padding: 0.55rem 0.85rem;
      color: var(--text-main);
      font-family: var(--font-sans);
      font-size: 0.875rem;
      outline: none;
      cursor: pointer;
    }
    select.select-field:focus {
      border-color: var(--border-focus);
    }

    /* Repository Cards Grid */
    .repo-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .repo-card {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: all 0.2s ease;
      cursor: pointer;
    }

    .repo-card:hover {
      border-color: #475569;
      transform: translateY(-2px);
      box-shadow: var(--shadow-md);
    }

    .repo-card.active-repo {
      border-color: var(--accent-primary);
      background-color: rgba(56, 189, 248, 0.04);
    }

    .repo-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 0.5rem;
      margin-bottom: 0.5rem;
    }

    .repo-name {
      font-size: 1.05rem;
      font-weight: 600;
      color: var(--text-main);
      word-break: break-word;
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }

    .repo-visibility {
      font-size: 0.7rem;
      padding: 1px 6px;
      border-radius: var(--radius-pill);
      background-color: var(--bg-surface-elevated);
      border: 1px solid var(--border-default);
      color: var(--text-subtle);
      font-weight: 500;
    }

    .repo-description {
      font-size: 0.825rem;
      color: var(--text-muted);
      line-height: 1.5;
      margin-bottom: 1rem;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      min-height: 2.5rem;
    }

    .repo-meta {
      display: flex;
      align-items: center;
      gap: 1rem;
      font-size: 0.775rem;
      color: var(--text-subtle);
      margin-bottom: 1rem;
      flex-wrap: wrap;
    }

    .repo-meta-item {
      display: flex;
      align-items: center;
      gap: 0.3rem;
    }

    .lang-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background-color: var(--accent-primary);
    }

    .repo-footer {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding-top: 0.75rem;
      border-top: 1px solid var(--border-subtle);
    }

    /* Selected Repository Workspace View */
    .repo-workspace {
      margin-top: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .repo-banner {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .repo-banner-top {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 1rem;
      flex-wrap: wrap;
    }

    .repo-banner-info h2 {
      font-size: 1.4rem;
      font-weight: 700;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 0.6rem;
      margin-bottom: 0.35rem;
    }

    .repo-topics {
      display: flex;
      align-items: center;
      gap: 0.4rem;
      flex-wrap: wrap;
      margin-top: 0.5rem;
    }

    .topic-pill {
      font-size: 0.725rem;
      padding: 2px 8px;
      background-color: var(--bg-surface-elevated);
      color: var(--accent-primary);
      border: 1px solid rgba(56, 189, 248, 0.2);
      border-radius: var(--radius-pill);
      font-weight: 500;
    }

    .sub-tabs {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      border-bottom: 1px solid var(--border-default);
      padding-bottom: 0;
      margin-bottom: 1.25rem;
      overflow-x: auto;
    }

    .sub-tab-btn {
      background: transparent;
      border: none;
      border-bottom: 2px solid transparent;
      color: var(--text-muted);
      font-family: var(--font-sans);
      font-size: 14px;
      font-weight: 500;
      padding: 0.65rem 1rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.45rem;
      transition: color 0.12s ease, border-color 0.12s ease;
      white-space: nowrap;
    }
    .sub-tab-btn:hover {
      color: var(--text-main);
      border-bottom-color: var(--border-default);
    }
    .sub-tab-btn.active {
      color: var(--text-main);
      border-bottom-color: var(--primer-tab-active);
      font-weight: 600;
    }

    /* ML Analysis Layout */
    .analysis-summary-banner {
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.08) 0%, rgba(56, 189, 248, 0.08) 100%), var(--bg-surface);
      border: 1px solid rgba(16, 185, 129, 0.3);
      border-radius: var(--radius-lg);
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1.5rem;
      flex-wrap: wrap;
    }

    .analysis-score-box {
      display: flex;
      align-items: center;
      gap: 1.25rem;
    }

    .score-circle {
      width: 58px;
      height: 58px;
      border-radius: 50%;
      background-color: var(--bg-surface-elevated);
      border: 3px solid var(--badge-success);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.2rem;
      font-weight: 700;
      color: var(--text-main);
    }

    .analysis-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
      gap: 1.25rem;
      margin-bottom: 1.5rem;
    }

    .finding-card {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 1.25rem;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .finding-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
    }

    .finding-title {
      font-size: 0.95rem;
      font-weight: 600;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 0.45rem;
    }

    .status-tag {
      font-size: 0.7rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      padding: 2px 8px;
      border-radius: var(--radius-pill);
    }

    .status-tag.documented {
      background-color: var(--badge-success-bg);
      color: var(--badge-success);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .status-tag.unverified {
      background-color: var(--badge-warning-bg);
      color: var(--badge-warning);
      border: 1px solid rgba(245, 158, 11, 0.3);
    }

    .status-tag.inferred {
      background-color: var(--badge-neutral-bg);
      color: var(--text-muted);
      border: 1px solid var(--border-default);
    }

    .finding-detail {
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.55;
    }

    .evidence-box {
      background-color: var(--bg-base);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-md);
      padding: 0.65rem 0.85rem;
      font-size: 0.775rem;
      color: var(--text-subtle);
      display: flex;
      flex-direction: column;
      gap: 0.35rem;
    }

    .evidence-title {
      font-weight: 600;
      color: var(--text-muted);
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .evidence-item {
      font-family: var(--font-mono);
      word-break: break-all;
    }

    /* Framework Table */
    .frameworks-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.825rem;
      margin-top: 0.5rem;
    }

    .frameworks-table th {
      text-align: left;
      padding: 0.6rem 0.75rem;
      border-bottom: 1px solid var(--border-default);
      color: var(--text-subtle);
      font-weight: 600;
      text-transform: uppercase;
      font-size: 0.7rem;
    }

    .frameworks-table td {
      padding: 0.65rem 0.75rem;
      border-bottom: 1px solid var(--border-subtle);
      color: var(--text-muted);
    }

    /* File Explorer */
    .file-explorer-container {
      display: grid;
      grid-template-columns: 280px 1fr;
      gap: 1rem;
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      overflow: hidden;
      min-height: 480px;
    }

    .file-tree-sidebar {
      border-right: 1px solid var(--border-default);
      background-color: rgba(15, 23, 42, 0.5);
      padding: 0.75rem;
      overflow-y: auto;
      max-height: 600px;
    }

    .file-tree-item {
      display: flex;
      align-items: center;
      gap: 0.45rem;
      padding: 0.4rem 0.6rem;
      border-radius: var(--radius-sm);
      font-size: 0.825rem;
      color: var(--text-muted);
      cursor: pointer;
      font-family: var(--font-mono);
      transition: all 0.1s ease;
    }

    .file-tree-item:hover {
      background-color: var(--bg-surface-elevated);
      color: var(--text-main);
    }

    .file-tree-item.active {
      background-color: var(--accent-primary-subtle);
      color: var(--accent-primary);
      font-weight: 600;
    }

    .file-viewer-pane {
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .file-viewer-header {
      padding: 0.75rem 1rem;
      border-bottom: 1px solid var(--border-default);
      display: flex;
      align-items: center;
      justify-content: space-between;
      background-color: var(--bg-surface-elevated);
      font-family: var(--font-mono);
      font-size: 0.825rem;
    }

    .file-viewer-content {
      flex: 1;
      padding: 1rem;
      overflow: auto;
      max-height: 550px;
      background-color: var(--bg-base);
    }

    pre.code-block {
      font-family: var(--font-mono);
      font-size: 0.825rem;
      line-height: 1.6;
      color: #e2e8f0;
      white-space: pre-wrap;
      word-break: break-word;
    }

    /* Code Snippets & Accordions */
    .code-snippet-box {
      position: relative;
      background-color: var(--bg-base);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      padding: 1rem;
      margin-top: 0.75rem;
    }

    .copy-btn {
      position: absolute;
      top: 0.65rem;
      right: 0.65rem;
      background-color: var(--bg-surface-elevated);
      border: 1px solid var(--border-default);
      color: var(--text-muted);
      border-radius: var(--radius-sm);
      padding: 4px 8px;
      font-size: 0.725rem;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 0.3rem;
      transition: all 0.15s ease;
    }
    .copy-btn:hover {
      color: var(--text-main);
      border-color: #475569;
    }

    /* Setup Guides */
    .client-guide-card {
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-lg);
      padding: 1.5rem;
      margin-bottom: 1.5rem;
    }

    .client-guide-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 1rem;
    }

    .client-badge-supported {
      font-size: 0.7rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: var(--radius-pill);
      background-color: var(--badge-success-bg);
      color: var(--badge-success);
      border: 1px solid rgba(16, 185, 129, 0.3);
    }

    .client-badge-compatible {
      font-size: 0.7rem;
      font-weight: 600;
      padding: 3px 8px;
      border-radius: var(--radius-pill);
      background-color: var(--badge-neutral-bg);
      color: var(--text-muted);
      border: 1px solid var(--border-default);
    }

    ol.step-list {
      padding-left: 1.25rem;
      color: var(--text-muted);
      line-height: 1.7;
      font-size: 0.875rem;
      margin-bottom: 1rem;
    }

    ol.step-list li {
      margin-bottom: 0.5rem;
    }

    /* Activity Log */
    .activity-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .activity-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      background-color: var(--bg-surface);
      border: 1px solid var(--border-default);
      border-radius: var(--radius-md);
      padding: 0.85rem 1.15rem;
      gap: 1rem;
    }

    .activity-info {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }

    .activity-time {
      font-size: 0.75rem;
      color: var(--text-subtle);
    }

    /* Notification Toast */
    .toast-container {
      position: fixed;
      bottom: 1.5rem;
      right: 1.5rem;
      z-index: 100;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .toast {
      background-color: var(--bg-surface-elevated);
      border: 1px solid var(--border-default);
      border-left: 4px solid var(--accent-primary);
      color: var(--text-main);
      padding: 0.75rem 1rem;
      border-radius: var(--radius-md);
      box-shadow: var(--shadow-lg);
      font-size: 0.85rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
      animation: slideIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }

    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }

    /* GitHub Primer Blankslate */
    .blankslate {
      text-align: center;
      padding: 2.5rem 1.5rem;
      border: 1px dashed var(--border-default);
      border-radius: var(--radius-md);
      background-color: var(--bg-surface);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      margin: 1rem 0;
    }

    .blankslate-icon {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background-color: var(--bg-surface-elevated);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-subtle);
      margin-bottom: 0.5rem;
    }

    .blankslate-heading {
      font-size: 1.15rem;
      font-weight: 600;
      color: var(--text-main);
    }

    .blankslate-text {
      font-size: 0.875rem;
      color: var(--text-muted);
      max-width: 480px;
      line-height: 1.5;
    }

    .blankslate-action {
      margin-top: 0.75rem;
    }

    /* GitHub Primer Flash Banners (Alerts & Errors) */
    .flash {
      position: relative;
      padding: 12px 16px;
      font-size: 13px;
      line-height: 1.5;
      border: 1px solid;
      border-radius: var(--radius-md);
      margin-bottom: 1.25rem;
      display: flex;
      align-items: flex-start;
      gap: 12px;
    }

    .flash-error {
      color: #f85149;
      background-color: rgba(248, 81, 73, 0.1);
      border-color: rgba(248, 81, 73, 0.4);
    }

    .flash-warn {
      color: #d29922;
      background-color: rgba(187, 128, 9, 0.1);
      border-color: rgba(187, 128, 9, 0.4);
    }

    .flash-info {
      color: #58a6ff;
      background-color: rgba(56, 139, 253, 0.1);
      border-color: rgba(56, 139, 253, 0.4);
    }

    .flash-success {
      color: #3fb950;
      background-color: rgba(46, 160, 67, 0.1);
      border-color: rgba(46, 160, 67, 0.4);
    }

    .flash-title {
      font-weight: 600;
      display: block;
      margin-bottom: 3px;
    }

    /* Empty and Error states fallback */
    .state-box {
      text-align: center;
      padding: 3rem 1.5rem;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 0.75rem;
    }

    .state-icon {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      background-color: var(--bg-surface-elevated);
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--text-subtle);
      margin-bottom: 0.5rem;
    }

    .error-card {
      background-color: rgba(248, 81, 73, 0.1);
      border: 1px solid rgba(248, 81, 73, 0.4);
      border-radius: var(--radius-md);
      padding: 1rem 1.25rem;
      color: #f85149;
      font-size: 0.875rem;
      margin-bottom: 1.25rem;
      display: flex;
      align-items: flex-start;
      gap: 0.75rem;
    }

    /* Responsive */
    @media (max-width: 768px) {
      header.app-header {
        padding: 0 1rem;
        height: auto;
        flex-direction: column;
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
        gap: 0.75rem;
      }
      .file-explorer-container {
        grid-template-columns: 1fr;
      }
      .file-tree-sidebar {
        border-right: none;
        border-bottom: 1px solid var(--border-default);
        max-height: 200px;
      }
    }
  </style>
</head>
<body>

  <!-- Top Navigation Header -->
  <header class="app-header">
    <div class="brand-group">
      <div class="brand-icon">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path>
          <path d="M9 18c-4.51 2-5-2-7-2"></path>
        </svg>
      </div>
      <div>
        <div class="brand-title">
          GitHub MCP Assistant
          <span class="brand-tag">v0.1.0</span>
        </div>
      </div>
    </div>

    <nav class="main-nav" role="tablist">
      <button class="nav-btn active" onclick="switchView('workspace')" id="nav-workspace">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
        Workspace
      </button>
      <button class="nav-btn" onclick="switchView('explore')" id="nav-explore">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
        Explore
      </button>
      <button class="nav-btn" onclick="switchView('connect')" id="nav-connect">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
        Connect Agent
      </button>
      <button class="nav-btn" onclick="switchView('activity')" id="nav-activity">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        Activity
      </button>
      <button class="nav-btn" onclick="switchView('settings')" id="nav-settings">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
        Settings
      </button>
    </nav>

    <div class="header-status-area">
      <div class="status-pill" id="header-rate-limit-badge" title="Live GitHub API Quota">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
        <span id="header-rate-limit-text">Quota: Checking...</span>
      </div>
      <div class="status-pill" id="header-auth-badge" title="GitHub API Authentication Tier">
        <span class="status-dot" id="header-auth-dot"></span>
        <span id="header-auth-text">Checking status...</span>
      </div>
      <div class="status-pill" title="Local MCP Server Protocol Status">
        <span class="status-dot active"></span>
        <span>stdio MCP 2.x</span>
      </div>
    </div>
  </header>

  <!-- Main View Area -->
  <main class="app-content">

    <!-- 1. WORKSPACE VIEW -->
    <section id="view-workspace" class="view-pane active">
      <div class="hero-banner">
        <h1 class="hero-title">Client-Facing GitHub Repository & ML Portfolio Intelligence</h1>
        <p class="hero-subtitle">
          Connect your favorite AI agent through Model Context Protocol (MCP) to seamlessly discover repositories, inspect directory trees, and conduct automated Machine Learning architecture audits with verified evidence.
        </p>
        <div class="hero-actions">
          <button class="btn btn-primary" onclick="quickExplore('hamna-ali')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polygon points="16.24 7.76 14.12 14.12 7.76 16.24 9.88 9.88 16.24 7.76"></polygon></svg>
            Explore Portfolio (hamna-ali)
          </button>
          <button class="btn btn-secondary" onclick="switchView('connect')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
            Connect an AI Agent
          </button>
        </div>
      </div>

      <!-- Quick Status Grid -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-label">MCP Protocol Server</span>
          <span class="stat-value" id="dash-mcp-status">Active (stdio)</span>
          <span class="stat-detail">Official Model Context Protocol SDK 2.x</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">GitHub Rate Limit Tier</span>
          <span class="stat-value" id="dash-rate-limit">Loading...</span>
          <span class="stat-detail" id="dash-auth-detail">Checking token...</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Available Tools</span>
          <span class="stat-value">5 Registered</span>
          <span class="stat-detail">Discovery, Inspection, Trees, Files, ML Analysis</span>
        </div>
        <div class="stat-card">
          <span class="stat-label">Target Architecture</span>
          <span class="stat-value">Localhost Demo</span>
          <span class="stat-detail">Zero external deployments or database dependencies</span>
        </div>
      </div>

      <!-- Portfolio Highlight Card -->
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
            Featured Portfolio Repositories
          </h2>
          <span class="brand-tag">Instant Verification</span>
        </div>
        <p style="color: var(--text-muted); font-size: 0.875rem; margin-bottom: 1.25rem;">
          Select a verified machine learning repository to evaluate its architecture, problem statement, model backbones, and pipeline evidence:
        </p>
        <div class="repo-grid" id="featured-repo-grid">
          <div class="repo-card" onclick="selectAndInspectRepo('hamna-ali', 'Customer-Churn-Prediction')">
            <div class="repo-header">
              <span class="repo-name">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                Customer-Churn-Prediction
              </span>
              <span class="repo-visibility">Public</span>
            </div>
            <p class="repo-description">
              Production Machine Learning project predicting telecom customer churn using Scikit-Learn, XGBoost, and full training/evaluation pipelines.
            </p>
            <div class="repo-meta">
              <span class="repo-meta-item"><span class="lang-dot"></span> Python / Jupyter</span>
              <span class="repo-meta-item">Tabular Classification</span>
            </div>
            <div class="repo-footer">
              <span class="brand-tag" style="background: rgba(16, 185, 129, 0.12); color: #10b981; border-color: rgba(16, 185, 129, 0.3);">ML Ready</span>
              <button class="btn btn-primary btn-sm">Inspect & Analyze &rarr;</button>
            </div>
          </div>

          <div class="repo-card" onclick="selectAndInspectRepo('hamna-ali', 'GitHub-MCP-Server')">
            <div class="repo-header">
              <span class="repo-name">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                GitHub-MCP-Server
              </span>
              <span class="repo-visibility">Public</span>
            </div>
            <p class="repo-description">
              Official Model Context Protocol server exposing GitHub tools for repository exploration and automated ML portfolio analysis.
            </p>
            <div class="repo-meta">
              <span class="repo-meta-item"><span class="lang-dot"></span> Python 3.12</span>
              <span class="repo-meta-item">MCP Protocol</span>
            </div>
            <div class="repo-footer">
              <span class="brand-tag">Current Project</span>
              <button class="btn btn-secondary btn-sm">Inspect & Analyze &rarr;</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 2. EXPLORE VIEW -->
    <section id="view-explore" class="view-pane">
      <div class="search-bar">
        <div class="input-group" style="max-width: 280px;">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
          <input type="text" id="input-username" class="input-field" placeholder="GitHub account (e.g. hamna-ali)" value="hamna-ali" onkeydown="if(event.key==='Enter') fetchRepositories()">
        </div>

        <div class="input-group">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          <input type="text" id="input-name-filter" class="input-field" placeholder="Filter repositories by name or topic..." oninput="filterRepositoriesLocally()">
        </div>

        <select id="select-language" class="select-field" onchange="filterRepositoriesLocally()">
          <option value="">All Languages</option>
          <option value="python">Python</option>
          <option value="jupyter notebook">Jupyter Notebook</option>
          <option value="typescript">TypeScript</option>
          <option value="javascript">JavaScript</option>
        </select>

        <button class="btn btn-primary" onclick="fetchRepositories()" id="btn-fetch-repos">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
          Fetch Repositories
        </button>
      </div>

      <!-- GitHub Primer Flash Notice Box -->
      <div id="explore-error-box" class="flash flash-error" style="display: none;">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="flex-shrink: 0; margin-top: 1px;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
        <div style="flex: 1;">
          <span class="flash-title" id="explore-error-title">Request Notice</span>
          <div id="explore-error-msg" style="margin-top: 0.25rem;"></div>
        </div>
      </div>

      <!-- Repositories Grid Container -->
      <div id="repo-list-container">
        <div class="blankslate">
          <div class="blankslate-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
          </div>
          <h3 class="blankslate-heading">No repositories loaded</h3>
          <p class="blankslate-text">Click "Fetch Repositories" above to query the GitHub REST API and browse repositories for the selected account.</p>
          <div class="blankslate-action">
            <button class="btn btn-primary btn-sm" onclick="fetchRepositories()">Fetch Repositories</button>
          </div>
        </div>
      </div>

      <!-- Selected Repository Workspace (Interactive Details, ML Analysis, Tree, Files) -->
      <div id="selected-repo-workspace" class="repo-workspace" style="display: none;">
        <div class="repo-banner">
          <div class="repo-banner-top">
            <div class="repo-banner-info">
              <h2 id="active-repo-name">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                <span id="active-repo-fullname">owner/repo</span>
              </h2>
              <p id="active-repo-description" style="color: var(--text-muted); font-size: 0.9rem; max-width: 800px; margin-top: 0.25rem;">
                Repository description loading...
              </p>
              <div class="repo-topics" id="active-repo-topics"></div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;">
              <button class="btn btn-primary" onclick="runMLAnalysisForActiveRepo()" id="btn-run-analysis">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                Analyze ML Project
              </button>
              <a id="active-repo-github-link" href="#" target="_blank" class="btn btn-secondary" title="View on GitHub">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                GitHub
              </a>
            </div>
          </div>

          <div class="repo-meta" style="margin-bottom: 0;">
            <span class="repo-meta-item" id="meta-stars"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg> 0 stars</span>
            <span class="repo-meta-item" id="meta-forks"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1-9 9"></path></svg> 0 forks</span>
            <span class="repo-meta-item" id="meta-branch"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="6" y1="3" x2="6" y2="21"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1-9 9"></path></svg> Default: main</span>
            <span class="repo-meta-item" id="meta-license"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg> License: MIT</span>
            <span class="repo-meta-item" id="meta-updated"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg> Updated: recent</span>
          </div>
        </div>

        <!-- Sub Tabs -->
        <div class="sub-tabs">
          <button class="sub-tab-btn active" onclick="switchSubTab('analysis')" id="tab-analysis">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
            ML Portfolio Analysis
          </button>
          <button class="sub-tab-btn" onclick="switchSubTab('files')" id="tab-files">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
            Browse Files & Code
          </button>
          <button class="sub-tab-btn" onclick="switchSubTab('tree')" id="tab-tree">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
            Directory Tree
          </button>
          <button class="sub-tab-btn" onclick="switchSubTab('developer')" id="tab-developer">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
            Advanced / Developer Details
          </button>
        </div>

        <!-- Sub Tab 1: ML Analysis Panel -->
        <div id="subtab-panel-analysis" class="subtab-content">
          <div id="analysis-loading-state" class="state-box" style="display: none;">
            <div class="state-icon" style="animation: spin 1s linear infinite;">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
            </div>
            <p style="font-weight: 600;">Evaluating Machine Learning Architecture...</p>
            <p style="font-size: 0.85rem;">Inspecting README documentation, AST configurations, and dependency manifests...</p>
          </div>

          <div id="analysis-results-box" style="display: none;">
            <div class="analysis-summary-banner">
              <div class="analysis-score-box">
                <div class="score-circle" id="analysis-score-val">95%</div>
                <div>
                  <h3 style="font-size: 1.15rem; font-weight: 700; color: var(--text-main);" id="analysis-headline">
                    Machine Learning Project Verified
                  </h3>
                  <p style="color: var(--text-muted); font-size: 0.85rem;" id="analysis-summary-notes">
                    Evaluation completed with documented pipeline evidence.
                  </p>
                </div>
              </div>
              <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                <span class="status-tag documented">Verified Evidence</span>
                <span class="status-tag unverified">Unverified Claims Flagged</span>
              </div>
            </div>

            <!-- Structured Findings Grid -->
            <div class="analysis-grid">
              <!-- Problem Statement -->
              <div class="finding-card">
                <div class="finding-header">
                  <span class="finding-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                    Problem Statement
                  </span>
                  <span class="status-tag" id="tag-problem-status">documented</span>
                </div>
                <p class="finding-detail" id="detail-problem">Loading problem statement...</p>
                <div class="evidence-box">
                  <span class="evidence-title">Documented Evidence</span>
                  <div id="evidence-problem" class="evidence-item">None</div>
                </div>
              </div>

              <!-- Model Architecture -->
              <div class="finding-card">
                <div class="finding-header">
                  <span class="finding-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
                    Model Architecture & Backbone
                  </span>
                  <span class="status-tag" id="tag-model-status">documented</span>
                </div>
                <p class="finding-detail" id="detail-model">Loading model architecture...</p>
                <div class="evidence-box">
                  <span class="evidence-title">Documented Evidence</span>
                  <div id="evidence-model" class="evidence-item">None</div>
                </div>
              </div>

              <!-- Datasets -->
              <div class="finding-card">
                <div class="finding-header">
                  <span class="finding-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path></svg>
                    Datasets & Data Pipeline
                  </span>
                  <span class="status-tag" id="tag-datasets-status">documented</span>
                </div>
                <p class="finding-detail" id="detail-datasets">Loading datasets...</p>
                <div class="evidence-box">
                  <span class="evidence-title">Documented Evidence</span>
                  <div id="evidence-datasets" class="evidence-item">None</div>
                </div>
              </div>

              <!-- Training Pipeline -->
              <div class="finding-card">
                <div class="finding-header">
                  <span class="finding-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                    Training Pipeline & Experiments
                  </span>
                  <span class="status-tag" id="tag-training-status">documented</span>
                </div>
                <p class="finding-detail" id="detail-training">Loading training loop...</p>
                <div class="evidence-box">
                  <span class="evidence-title">Documented Evidence</span>
                  <div id="evidence-training" class="evidence-item">None</div>
                </div>
              </div>

              <!-- Evaluation Metrics -->
              <div class="finding-card">
                <div class="finding-header">
                  <span class="finding-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
                    Evaluation Metrics & Benchmarks
                  </span>
                  <span class="status-tag" id="tag-eval-status">documented</span>
                </div>
                <p class="finding-detail" id="detail-eval">Loading evaluation metrics...</p>
                <div class="evidence-box">
                  <span class="evidence-title">Documented Evidence</span>
                  <div id="evidence-eval" class="evidence-item">None</div>
                </div>
              </div>

              <!-- Deployment Approach -->
              <div class="finding-card">
                <div class="finding-header">
                  <span class="finding-title">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path></svg>
                    Deployment & Serving Readiness
                  </span>
                  <span class="status-tag" id="tag-deployment-status">documented</span>
                </div>
                <p class="finding-detail" id="detail-deployment">Loading deployment approach...</p>
                <div class="evidence-box">
                  <span class="evidence-title">Documented Evidence</span>
                  <div id="evidence-deployment" class="evidence-item">None</div>
                </div>
              </div>
            </div>

            <!-- Frameworks Table Card -->
            <div class="card" style="margin-bottom: 1.5rem;">
              <div class="card-header">
                <h3 class="card-title">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
                  Detected ML Frameworks & Tooling
                </h3>
                <span class="brand-tag" id="frameworks-count-badge">0 Verified</span>
              </div>
              <div style="overflow-x: auto;">
                <table class="frameworks-table">
                  <thead>
                    <tr>
                      <th>Framework / Library</th>
                      <th>Domain Category</th>
                      <th>In Dependencies</th>
                      <th>In Documentation</th>
                      <th>Evidence Reference</th>
                    </tr>
                  </thead>
                  <tbody id="frameworks-table-body">
                    <tr><td colspan="5" style="text-align: center; color: var(--text-subtle);">No frameworks detected.</td></tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Key Files List -->
            <div class="card">
              <div class="card-header">
                <h3 class="card-title">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                  Key Configuration & Source Files Found
                </h3>
              </div>
              <div id="key-files-list" style="display: flex; gap: 0.5rem; flex-wrap: wrap;"></div>
            </div>
          </div>
        </div>

        <!-- Sub Tab 2: File Explorer & Content Viewer -->
        <div id="subtab-panel-files" class="subtab-content" style="display: none;">
          <div class="file-explorer-container">
            <div class="file-tree-sidebar" id="file-tree-sidebar-list">
              <div style="padding: 0.5rem; color: var(--text-subtle); font-size: 0.8rem;">Loading tree...</div>
            </div>
            <div class="file-viewer-pane">
              <div class="file-viewer-header">
                <span id="active-file-path">README.md</span>
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                  <span id="active-file-size" style="font-size: 0.75rem; color: var(--text-subtle);">0 KB</span>
                  <button class="btn btn-secondary btn-sm" onclick="copyCurrentFileContent()">Copy Content</button>
                </div>
              </div>
              <div class="file-viewer-content">
                <pre class="code-block" id="active-file-content">Select a file from the repository tree on the left to inspect its contents.</pre>
              </div>
            </div>
          </div>
        </div>

        <!-- Sub Tab 3: Directory Tree Overview -->
        <div id="subtab-panel-tree" class="subtab-content" style="display: none;">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>
                Complete Git Tree Structure
              </h3>
              <span class="status-pill" id="tree-total-items-badge">0 items</span>
            </div>
            <div id="full-tree-container" style="max-height: 480px; overflow-y: auto;"></div>
          </div>
        </div>

        <!-- Sub Tab 4: Advanced / Developer Details -->
        <div id="subtab-panel-developer" class="subtab-content" style="display: none;">
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline></svg>
                Underlying MCP Tool Diagnostics
              </h3>
              <span class="brand-tag">JSON-RPC stdio</span>
            </div>
            <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1rem;">
              The client-facing UI executes the exact same underlying Python MCP tools that an AI agent calls via the official Model Context Protocol:
            </p>
            <div style="display: flex; flex-direction: column; gap: 0.75rem;">
              <div class="code-snippet-box">
                <div style="font-weight: 600; font-size: 0.8rem; color: var(--accent-primary); margin-bottom: 0.25rem;">
                  Last Executed Tool Invocation
                </div>
                <pre class="code-block" id="developer-last-call">{ "tool": "analyze_ml_repository", "status": "ready" }</pre>
              </div>
              <div class="code-snippet-box">
                <button class="copy-btn" onclick="copyRawJsonResponse()">Copy JSON</button>
                <div style="font-weight: 600; font-size: 0.8rem; color: var(--accent-primary); margin-bottom: 0.25rem;">
                  Raw MCP Output Payload
                </div>
                <pre class="code-block" id="developer-raw-response">No tool executed yet.</pre>
              </div>
            </div>
          </div>
        </div>

      </div>
    </section>

    <!-- 3. CONNECT AGENT VIEW -->
    <section id="view-connect" class="view-pane">
      <div class="hero-banner" style="margin-bottom: 1.5rem;">
        <h1 class="hero-title">Connect MCP-Compatible AI Clients</h1>
        <p class="hero-subtitle">
          This server implements the official <strong>Model Context Protocol (MCP)</strong> using standard I/O (<code>stdio</code>) transport. You can connect it directly to your favorite AI assistant so it can explore repositories, read source code, and analyze ML architectures during conversations.
        </p>
      </div>

      <!-- How It Works Educational Banner -->
      <div class="card" style="margin-bottom: 1.5rem;">
        <div class="card-header">
          <h2 class="card-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            How the MCP Architecture Works
          </h2>
          <span class="status-pill"><span class="status-dot active"></span> Local stdio Subprocess</span>
        </div>
        <div class="stats-grid" style="margin-bottom: 0;">
          <div class="stat-card">
            <span class="stat-label">1. MCP Server</span>
            <span class="stat-detail">Runs as a secure local process exposing GitHub inspection capabilities via standard input/output.</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">2. MCP Tools (5 Active)</span>
            <span class="stat-detail">Callable functions: <code>list_repositories</code>, <code>get_repository_details</code>, <code>get_repository_tree</code>, <code>get_file_contents</code>, <code>analyze_ml_repository</code>.</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">3. MCP Resources</span>
            <span class="stat-detail" style="color: var(--text-subtle);">Not exposed currently. Tools provide real-time on-demand repository inspection.</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">4. MCP Prompts</span>
            <span class="stat-detail" style="color: var(--text-subtle);">Not exposed currently. Connected AI models query tools with natural language directly.</span>
          </div>
        </div>
      </div>

      <!-- Supported Clients Guides -->
      <div class="client-guide-card">
        <div class="client-guide-header">
          <div style="display: flex; align-items: center; gap: 0.6rem;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main);">Claude Desktop</h3>
            <span class="client-badge-supported">Verified Supported Client</span>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="copySnippet('claude-desktop-snippet')">Copy Configuration</button>
        </div>
        <ol class="step-list">
          <li>Open your Claude Desktop configuration file at:
            <code id="claude-config-path" style="background: var(--bg-surface-elevated); padding: 2px 6px; border-radius: 4px; font-size: 0.775rem;">%APPDATA%\\Claude\\claude_desktop_config.json</code>
          </li>
          <li>Paste the following JSON snippet inside the <code>mcpServers</code> section:</li>
        </ol>
        <div class="code-snippet-box">
          <button class="copy-btn" onclick="copySnippet('claude-desktop-snippet')">Copy JSON</button>
          <pre class="code-block" id="claude-desktop-snippet">Loading configuration...</pre>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.75rem;">
          Restart Claude Desktop. The hammer icon will indicate that the 5 GitHub tools are connected and available in chat.
        </p>
      </div>

      <div class="client-guide-card">
        <div class="client-guide-header">
          <div style="display: flex; align-items: center; gap: 0.6rem;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main);">Antigravity / VS Code MCP</h3>
            <span class="client-badge-supported">Verified Supported Client</span>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="copySnippet('antigravity-snippet')">Copy Configuration</button>
        </div>
        <ol class="step-list">
          <li>In Antigravity or VS Code MCP configuration, register the local stdio server command:</li>
        </ol>
        <div class="code-snippet-box">
          <button class="copy-btn" onclick="copySnippet('antigravity-snippet')">Copy JSON</button>
          <pre class="code-block" id="antigravity-snippet">Loading configuration...</pre>
        </div>
      </div>

      <div class="client-guide-card">
        <div class="client-guide-header">
          <div style="display: flex; align-items: center; gap: 0.6rem;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main);">Cursor & Other MCP-Compatible Clients</h3>
            <span class="client-badge-compatible">MCP-Compatible Client</span>
          </div>
          <button class="btn btn-secondary btn-sm" onclick="copySnippet('cursor-snippet')">Copy Command</button>
        </div>
        <ol class="step-list">
          <li>Navigate to Settings &rarr; Features &rarr; MCP &rarr; Add New MCP Server.</li>
          <li>Select type <strong>command</strong> (stdio). Use the copyable command snippet below:</li>
        </ol>
        <div class="code-snippet-box">
          <button class="copy-btn" onclick="copySnippet('cursor-snippet')">Copy Command</button>
          <pre class="code-block" id="cursor-snippet">Loading configuration...</pre>
        </div>
        <p style="font-size: 0.8rem; color: var(--text-subtle); margin-top: 0.75rem;">
          <em>Note: Remote or cloud-hosted transports (HTTP/SSE) are not currently exposed. This server operates exclusively over local stdio transport for secure local execution.</em>
        </p>
      </div>
    </section>

    <!-- 4. ACTIVITY VIEW -->
    <section id="view-activity" class="view-pane">
      <div class="card">
        <div class="card-header">
          <h2 class="card-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
            Session Activity & Audit Log
          </h2>
          <button class="btn btn-secondary btn-sm" onclick="clearActivityLog()">Clear Session</button>
        </div>
        <p style="color: var(--text-muted); font-size: 0.85rem; margin-bottom: 1.25rem;">
          Real-time audit log of GitHub queries, file reads, and ML evaluations executed during this localhost session.
        </p>
        <div id="activity-log-container" class="activity-list">
          <div class="state-box" id="activity-empty-state">
            <p style="font-weight: 600;">No actions recorded yet</p>
            <p style="font-size: 0.8rem;">Explore repositories or run ML analyses to view activity history.</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 5. SETTINGS VIEW -->
    <section id="view-settings" class="view-pane">
      <div class="card" style="margin-bottom: 1.5rem;">
        <div class="card-header">
          <h2 class="card-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            GitHub Connection & Credential Status
          </h2>
          <span class="status-pill" id="settings-status-pill">Checking...</span>
        </div>
        <div class="stats-grid" style="margin-bottom: 1.25rem;">
          <div class="stat-card">
            <span class="stat-label">API Base URL</span>
            <span class="stat-value" style="font-size: 1rem;" id="settings-api-url">https://api.github.com</span>
            <span class="stat-detail">GitHub REST API v2022-11-28</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">Active Rate Limit</span>
            <span class="stat-value" style="font-size: 1rem;" id="settings-rate-tier">5,000 req/hr</span>
            <span class="stat-detail" id="settings-rate-sub">Token Authenticated</span>
          </div>
          <div class="stat-card">
            <span class="stat-label">Request Timeout</span>
            <span class="stat-value" style="font-size: 1rem;">20.0 seconds</span>
            <span class="stat-detail">Configured via ServerConfig</span>
          </div>
        </div>

        <div class="card" style="background-color: var(--bg-surface-elevated); border-color: var(--border-default);">
          <h3 style="font-size: 0.95rem; font-weight: 600; color: var(--text-main); margin-bottom: 0.5rem;">
            Safe Token Configuration Guidance
          </h3>
          <p style="font-size: 0.85rem; color: var(--text-muted); line-height: 1.6;">
            Authentication tokens are strictly loaded from the project root <code>.env</code> file into memory using Pydantic's <code>SecretStr</code>. Tokens are never logged, never returned in tool outputs, and never committed to Git.
          </p>
          <div class="code-snippet-box" style="margin-top: 0.75rem;">
            <pre class="code-block"># In D:\\ML Projects\\GitHub-MCP-Server\\.env
GITHUB_PERSONAL_ACCESS_TOKEN=ghp_your_token_here
GITHUB_API_URL=https://api.github.com</pre>
          </div>
          <p style="font-size: 0.8rem; color: var(--text-subtle); margin-top: 0.75rem;">
            Required GitHub Permissions: Read-only on public repositories (classic <code>public_repo</code> or fine-grained Contents/Metadata read-only).
          </p>
        </div>
      </div>
    </section>

  </main>

  <!-- Notification Toast Container -->
  <div class="toast-container" id="toast-container"></div>

  <!-- Client-Side JavaScript -->
  <script>
    // State store
    const state = {
      activeView: 'workspace',
      activeSubTab: 'analysis',
      username: 'hamna-ali',
      repositories: [],
      filteredRepositories: [],
      selectedRepo: null,
      activeRepoDetails: null,
      activeRepoTree: null,
      activeAnalysis: null,
      activeFilePath: 'README.md',
      activeFileContent: '',
      clientConfigs: null,
      activityLog: []
    };

    // Navigation View Switcher
    function switchView(viewName) {
      state.activeView = viewName;
      document.querySelectorAll('.view-pane').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.nav-btn').forEach(el => el.classList.remove('active'));

      const targetPane = document.getElementById(`view-${viewName}`);
      const targetNav = document.getElementById(`nav-${viewName}`);
      if (targetPane) targetPane.classList.add('active');
      if (targetNav) targetNav.classList.add('active');

      if (viewName === 'explore' && state.repositories.length === 0) {
        fetchRepositories();
      }
    }

    function switchSubTab(tabName) {
      state.activeSubTab = tabName;
      document.querySelectorAll('.subtab-content').forEach(el => el.style.display = 'none');
      document.querySelectorAll('.sub-tab-btn').forEach(el => el.classList.remove('active'));

      const targetPanel = document.getElementById(`subtab-panel-${tabName}`);
      const targetBtn = document.getElementById(`tab-${tabName}`);
      if (targetPanel) targetPanel.style.display = 'block';
      if (targetBtn) targetBtn.classList.add('active');

      if (tabName === 'files' && state.selectedRepo && !state.activeRepoTree) {
        loadRepositoryTree(state.selectedRepo.owner, state.selectedRepo.name);
      }
    }

    function showToast(message) {
      const container = document.getElementById('toast-container');
      const toast = document.createElement('div');
      toast.className = 'toast';
      toast.innerHTML = `<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg> <span>${message}</span>`;
      container.appendChild(toast);
      setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        toast.style.transition = 'all 0.2s ease';
        setTimeout(() => toast.remove(), 200);
      }, 2600);
    }

    function copySnippet(elementId) {
      const el = document.getElementById(elementId);
      if (el) {
        navigator.clipboard.writeText(el.innerText).then(() => {
          showToast('Configuration copied to clipboard!');
        });
      }
    }

    function copyRawJsonResponse() {
      const el = document.getElementById('developer-raw-response');
      if (el) {
        navigator.clipboard.writeText(el.innerText).then(() => {
          showToast('Raw JSON copied to clipboard!');
        });
      }
    }

    function copyCurrentFileContent() {
      if (state.activeFileContent) {
        navigator.clipboard.writeText(state.activeFileContent).then(() => {
          showToast(`Copied ${state.activeFilePath} to clipboard!`);
        });
      }
    }

    function recordActivity(action, target, status = 'success') {
      const item = {
        action,
        target,
        status,
        time: new Date().toLocaleTimeString()
      };
      state.activityLog.unshift(item);
      renderActivityLog();
    }

    function renderActivityLog() {
      const container = document.getElementById('activity-log-container');
      const emptyState = document.getElementById('activity-empty-state');
      if (state.activityLog.length === 0) {
        if (emptyState) emptyState.style.display = 'flex';
        return;
      }
      if (emptyState) emptyState.style.display = 'none';

      container.innerHTML = state.activityLog.map(act => `
        <div class="activity-item">
          <div class="activity-info">
            <span class="status-dot ${act.status === 'success' ? 'active' : 'warning'}"></span>
            <div>
              <span style="font-weight: 600; color: var(--text-main); font-size: 0.85rem;">${act.action}</span>
              <span style="color: var(--text-muted); font-size: 0.8rem; margin-left: 0.5rem; font-family: var(--font-mono);">${act.target}</span>
            </div>
          </div>
          <span class="activity-time">${act.time}</span>
        </div>
      `).join('');
    }

    function clearActivityLog() {
      state.activityLog = [];
      renderActivityLog();
      showToast('Activity history cleared.');
    }

    // GitHub Primer Live Rate Limit Tracker
    function updateRateLimit(rateLimit) {
      if (!rateLimit) return;
      const rateText = document.getElementById('header-rate-limit-text');
      const dashRate = document.getElementById('dash-rate-limit');
      const dashDetail = document.getElementById('dash-auth-detail');
      const setTier = document.getElementById('settings-rate-tier');
      const setSub = document.getElementById('settings-rate-sub');

      if (rateLimit.limit) {
        const remaining = rateLimit.remaining !== null && rateLimit.remaining !== undefined
          ? Number(rateLimit.remaining).toLocaleString()
          : (rateLimit.authenticated ? '5,000' : '60');
        const limit = Number(rateLimit.limit).toLocaleString();

        let resetStr = '';
        if (rateLimit.reset_epoch) {
          const resetDate = new Date(rateLimit.reset_epoch * 1000);
          resetStr = ` (resets ${resetDate.toLocaleTimeString()})`;
        }

        if (rateText) {
          rateText.innerText = `Quota: ${remaining} / ${limit}`;
          rateText.title = `GitHub API Rate Limit: ${remaining} requests remaining out of ${limit}${resetStr}`;
        }
        if (dashRate) {
          dashRate.innerText = `${remaining} / ${limit}`;
        }
        if (dashDetail) {
          dashDetail.innerText = resetStr ? `Resets at ${new Date(rateLimit.reset_epoch * 1000).toLocaleTimeString()}` : 'Live authenticated quota';
        }
        if (setTier) {
          setTier.innerText = `${remaining} / ${limit}`;
        }
        if (setSub && resetStr) {
          setSub.innerText = `Live quota resets at ${new Date(rateLimit.reset_epoch * 1000).toLocaleTimeString()}`;
        }
      }
    }

    // System Status Initialization
    async function loadSystemStatus() {
      try {
        const resp = await fetch('/api/status');
        const data = await resp.json();

        const authText = document.getElementById('header-auth-text');
        const authDot = document.getElementById('header-auth-dot');
        const rateText = document.getElementById('header-rate-limit-text');
        const dashRate = document.getElementById('dash-rate-limit');
        const dashDetail = document.getElementById('dash-auth-detail');
        const setPill = document.getElementById('settings-status-pill');
        const setTier = document.getElementById('settings-rate-tier');
        const setSub = document.getElementById('settings-rate-sub');

        if (data.token_configured) {
          if (authText) authText.innerText = 'Authenticated (5k req/hr)';
          if (authDot) authDot.className = 'status-dot active';
          if (rateText) rateText.innerText = 'Quota: 5,000 / 5,000';
          if (dashRate) dashRate.innerText = '5,000 req/hr';
          if (dashDetail) dashDetail.innerText = 'GitHub fine-grained token active in memory';
          if (setPill) { setPill.innerText = 'Token Active'; setPill.style.color = 'var(--badge-success)'; }
          if (setTier) setTier.innerText = '5,000 req/hr';
          if (setSub) setSub.innerText = 'Authenticated token in memory';
        } else {
          if (authText) authText.innerText = 'Unauthenticated (60 req/hr)';
          if (authDot) authDot.className = 'status-dot warning';
          if (rateText) rateText.innerText = 'Quota: 60 / hr (Unauthenticated)';
          if (dashRate) dashRate.innerText = '60 req/hr';
          if (dashDetail) dashDetail.innerText = 'IP-based rate limit active';
          if (setPill) { setPill.innerText = 'Unauthenticated'; setPill.style.color = 'var(--badge-warning)'; }
          if (setTier) setTier.innerText = '60 req/hr';
          if (setSub) setSub.innerText = 'Configure .env for 5k/hr';
        }
      } catch (e) {
        console.error('Failed to load system status:', e);
      }
    }

    // Load Client Configs
    async function loadClientConfigs() {
      try {
        const resp = await fetch('/api/client-configs');
        const data = await resp.json();
        state.clientConfigs = data;

        const claudeSnippet = document.getElementById('claude-desktop-snippet');
        const antigravitySnippet = document.getElementById('antigravity-snippet');
        const cursorSnippet = document.getElementById('cursor-snippet');
        const claudePath = document.getElementById('claude-config-path');

        if (claudeSnippet && data.claude_desktop) claudeSnippet.innerText = data.claude_desktop.snippet;
        if (antigravitySnippet && data.antigravity) antigravitySnippet.innerText = data.antigravity.snippet;
        if (cursorSnippet && data.cursor) cursorSnippet.innerText = data.cursor.command;
        if (claudePath && data.claude_desktop) claudePath.innerText = data.claude_desktop.file_location;
      } catch (e) {
        console.error('Failed to load client configs:', e);
      }
    }

    // Fetch Repositories
    async function fetchRepositories() {
      const usernameInput = document.getElementById('input-username');
      const username = usernameInput ? usernameInput.value.trim() : 'hamna-ali';
      state.username = username || 'hamna-ali';

      const container = document.getElementById('repo-list-container');
      const errBox = document.getElementById('explore-error-box');
      if (errBox) errBox.style.display = 'none';

      container.innerHTML = `
        <div class="blankslate">
          <div class="blankslate-icon" style="animation: spin 1s linear infinite;">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line></svg>
          </div>
          <h3 class="blankslate-heading">Querying GitHub REST API...</h3>
          <p class="blankslate-text">Fetching repositories for account <strong>${state.username}</strong></p>
        </div>
      `;

      try {
        const resp = await fetch(`/api/repos?username=${encodeURIComponent(state.username)}`);
        const data = await resp.json();

        if (data.rate_limit) updateRateLimit(data.rate_limit);

        if (data.error) {
          let errTitle = 'GitHub Request Notice';
          let errType = 'flash-error';
          let detailedMsg = data.message;

          if (data.error_type === 'ConnectTimeout') {
            errTitle = 'Connection Timeout (Network / Latency)';
            errType = 'flash-warn';
            detailedMsg = 'Unable to establish TCP handshake with api.github.com within 10s. This is caused by network latency, DNS resolution, or proxy filtering — NOT an API rate limit. Requests are automatically retried.';
          } else if (data.error_type === 'RateLimitExceeded') {
            errTitle = 'GitHub Rate Limit Exceeded (HTTP 403)';
            errType = 'flash-error';
            detailedMsg = `${data.message} Reset epoch: ${data.reset_time || 'N/A'}. Authenticate with GITHUB_PERSONAL_ACCESS_TOKEN in .env for 5,000 req/hr.`;
          } else if (data.error_type === 'PermissionDenied') {
            errTitle = 'GitHub Repository Access Denied (HTTP 403)';
            errType = 'flash-warn';
            detailedMsg = 'Token is authenticated, but does not have permission to access this repository. Verify repository access permissions for your fine-grained PAT.';
          } else if (data.error_type === 'AuthenticationFailed') {
            errTitle = 'GitHub Authentication Failed (HTTP 401)';
            errType = 'flash-error';
            detailedMsg = 'The provided GitHub Personal Access Token is invalid or expired. Check your .env file.';
          }

          if (errBox) {
            errBox.className = `flash ${errType}`;
            errBox.style.display = 'flex';
            document.getElementById('explore-error-title').innerText = errTitle;
            document.getElementById('explore-error-msg').innerText = detailedMsg;
          }
          container.innerHTML = `
            <div class="blankslate">
              <div class="blankslate-icon" style="color: var(--badge-danger);">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
              </div>
              <h3 class="blankslate-heading">${errTitle}</h3>
              <p class="blankslate-text">${detailedMsg}</p>
              <div class="blankslate-action">
                <button class="btn btn-secondary btn-sm" onclick="fetchRepositories()">Retry Request</button>
              </div>
            </div>
          `;
          recordActivity('List Repositories (Failed)', state.username, 'error');
          return;
        }

        state.repositories = data.repositories || [];
        state.filteredRepositories = [...state.repositories];
        recordActivity('List Repositories', `${state.username} (${state.repositories.length} found)`);
        renderRepositories();
      } catch (err) {
        container.innerHTML = `
          <div class="blankslate">
            <h3 class="blankslate-heading">Client Error</h3>
            <p class="blankslate-text">${err.message}</p>
          </div>
        `;
      }
    }

    function filterRepositoriesLocally() {
      const nameFilter = (document.getElementById('input-name-filter')?.value || '').toLowerCase().trim();
      const langFilter = (document.getElementById('select-language')?.value || '').toLowerCase().trim();

      state.filteredRepositories = state.repositories.filter(repo => {
        const nameMatch = !nameFilter || repo.name.toLowerCase().includes(nameFilter) || (repo.description || '').toLowerCase().includes(nameFilter);
        const langMatch = !langFilter || (repo.language || '').toLowerCase().includes(langFilter);
        return nameMatch && langMatch;
      });

      renderRepositories();
    }

    function renderRepositories() {
      const container = document.getElementById('repo-list-container');
      if (state.filteredRepositories.length === 0) {
        container.innerHTML = `
          <div class="state-box">
            <p style="font-weight: 600;">No matching repositories found</p>
            <p style="font-size: 0.85rem;">Try clearing your search query or language filter.</p>
          </div>
        `;
        return;
      }

      container.innerHTML = `
        <div class="repo-grid">
          ${state.filteredRepositories.map(repo => `
            <div class="repo-card ${state.selectedRepo?.name === repo.name ? 'active-repo' : ''}" onclick="selectAndInspectRepo('${repo.owner}', '${repo.name}')">
              <div class="repo-header">
                <span class="repo-name">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>
                  ${repo.name}
                </span>
                <span class="repo-visibility">${repo.is_private ? 'Private' : 'Public'}</span>
              </div>
              <p class="repo-description">${repo.description || 'No description provided.'}</p>
              <div class="repo-meta">
                <span class="repo-meta-item"><span class="lang-dot"></span> ${repo.language || 'Unknown'}</span>
                <span class="repo-meta-item">&star; ${repo.stargazers_count}</span>
                <span class="repo-meta-item">&#9874; ${repo.forks_count}</span>
              </div>
              <div class="repo-footer">
                <span style="font-size: 0.725rem; color: var(--text-subtle);">Branch: ${repo.default_branch}</span>
                <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation(); selectAndInspectRepo('${repo.owner}', '${repo.name}')">Inspect &rarr;</button>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Select and Inspect a Repository
    async function selectAndInspectRepo(owner, repoName) {
      state.selectedRepo = { owner, name: repoName };
      switchView('explore');

      const workspace = document.getElementById('selected-repo-workspace');
      workspace.style.display = 'flex';
      workspace.scrollIntoView({ behavior: 'smooth' });

      document.getElementById('active-repo-fullname').innerText = `${owner}/${repoName}`;
      document.getElementById('active-repo-description').innerText = 'Loading repository metadata...';
      document.getElementById('active-repo-github-link').href = `https://github.com/${owner}/${repoName}`;

      recordActivity('Inspect Repository', `${owner}/${repoName}`);

      try {
        const resp = await fetch(`/api/repos/${owner}/${repoName}`);
        const details = await resp.json();
        state.activeRepoDetails = details;
        if (details._rate_limit) updateRateLimit(details._rate_limit);

        document.getElementById('active-repo-description').innerText = details.description || 'No description provided.';
        document.getElementById('meta-stars').innerHTML = `&star; ${details.stargazers_count} stars`;
        document.getElementById('meta-forks').innerHTML = `&#9874; ${details.forks_count} forks`;
        document.getElementById('meta-branch').innerText = `Default: ${details.default_branch}`;
        document.getElementById('meta-license').innerText = details.license_name ? `License: ${details.license_name}` : 'No License';
        document.getElementById('meta-updated').innerText = details.updated_at ? `Updated: ${details.updated_at.split('T')[0]}` : '';

        const topicsBox = document.getElementById('active-repo-topics');
        if (details.topics && details.topics.length > 0) {
          topicsBox.innerHTML = details.topics.map(t => `<span class="topic-pill">${t}</span>`).join('');
        } else {
          topicsBox.innerHTML = '';
        }

        // Auto trigger ML analysis
        runMLAnalysisForActiveRepo();
      } catch (err) {
        console.error('Error fetching details:', err);
      }
    }

    function quickExplore(user) {
      const input = document.getElementById('input-username');
      if (input) input.value = user;
      switchView('explore');
      fetchRepositories();
    }

    // Run ML Repository Analysis
    async function runMLAnalysisForActiveRepo() {
      if (!state.selectedRepo) return;
      const { owner, name } = state.selectedRepo;

      switchSubTab('analysis');
      const loading = document.getElementById('analysis-loading-state');
      const results = document.getElementById('analysis-results-box');

      loading.style.display = 'flex';
      results.style.display = 'none';

      recordActivity('Run ML Analysis', `${owner}/${name}`);

      try {
        const resp = await fetch(`/api/repos/${owner}/${name}/analyze`, { method: 'POST' });
        const analysis = await resp.json();
        state.activeAnalysis = analysis;
        if (analysis._rate_limit) updateRateLimit(analysis._rate_limit);

        loading.style.display = 'none';
        results.style.display = 'block';

        // Developer details logging
        document.getElementById('developer-last-call').innerText = JSON.stringify({
          tool: 'analyze_ml_repository',
          parameters: { owner, repo: name, branch: null },
          timestamp: new Date().toISOString()
        }, null, 2);
        document.getElementById('developer-raw-response').innerText = JSON.stringify(analysis, null, 2);

        if (analysis.error) {
          document.getElementById('analysis-headline').innerText = 'Analysis Notice';
          document.getElementById('analysis-summary-notes').innerText = analysis.message;
          document.getElementById('analysis-score-val').innerText = '!';
          return;
        }

        // Populate Findings
        const scorePct = Math.round(analysis.ml_confidence_score * 100);
        document.getElementById('analysis-score-val').innerText = `${scorePct}%`;
        document.getElementById('analysis-headline').innerText = analysis.is_ml_project ? 'Verified Machine Learning Project' : 'General Software Repository';
        document.getElementById('analysis-summary-notes').innerText = analysis.summary_notes || 'Automated AST & documentation audit completed.';

        renderFinding('problem', analysis.problem_statement);
        renderFinding('model', analysis.model_architecture);
        renderFinding('datasets', analysis.datasets);
        renderFinding('training', analysis.training_pipeline);
        renderFinding('eval', analysis.evaluation_metrics);
        renderFinding('deployment', analysis.deployment_approach);

        // Frameworks Table
        const fwBody = document.getElementById('frameworks-table-body');
        const fwBadge = document.getElementById('frameworks-count-badge');
        if (analysis.frameworks && analysis.frameworks.length > 0) {
          fwBadge.innerText = `${analysis.frameworks.length} Detected`;
          fwBody.innerHTML = analysis.frameworks.map(f => `
            <tr>
              <td style="font-weight: 600; color: var(--text-main);">${f.name}</td>
              <td>${f.category}</td>
              <td>${f.verified_in_dependencies ? '<span class="status-tag documented">Verified</span>' : '<span style="color: var(--text-subtle);">No</span>'}</td>
              <td>${f.mentioned_in_readme ? '<span class="status-tag documented">Documented</span>' : '<span style="color: var(--text-subtle);">No</span>'}</td>
              <td style="font-family: var(--font-mono); font-size: 0.75rem;">${f.evidence || 'N/A'}</td>
            </tr>
          `).join('');
        } else {
          fwBadge.innerText = '0 Detected';
          fwBody.innerHTML = `<tr><td colspan="5" style="text-align: center; color: var(--text-subtle);">No standard ML frameworks detected in dependency manifests.</td></tr>`;
        }

        // Key Files
        const keyFilesBox = document.getElementById('key-files-list');
        if (analysis.key_files_found && analysis.key_files_found.length > 0) {
          keyFilesBox.innerHTML = analysis.key_files_found.map(kf => `
            <span class="topic-pill" style="cursor: pointer;" onclick="fetchAndDisplayFile('${kf}')">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="display: inline; vertical-align: middle;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg>
              ${kf}
            </span>
          `).join('');
        } else {
          keyFilesBox.innerHTML = '<span style="color: var(--text-subtle); font-size: 0.85rem;">No configuration files matched.</span>';
        }

      } catch (err) {
        loading.style.display = 'none';
        console.error('Error analyzing ML repository:', err);
      }
    }

    function renderFinding(idPrefix, field) {
      if (!field) return;
      const tag = document.getElementById(`tag-${idPrefix}-status`);
      const detail = document.getElementById(`detail-${idPrefix}`);
      const evidence = document.getElementById(`evidence-${idPrefix}`);

      if (tag) {
        tag.className = `status-tag ${field.status}`;
        tag.innerText = field.status;
      }
      if (detail) detail.innerText = field.details || 'Not documented.';
      if (evidence) {
        if (field.evidence && field.evidence.length > 0) {
          evidence.innerHTML = field.evidence.map(e => `<div>&bull; ${e}</div>`).join('');
        } else {
          evidence.innerText = 'No explicit evidence detected.';
        }
      }
    }

    // Load Repository Tree
    async function loadRepositoryTree(owner, repo) {
      const sidebar = document.getElementById('file-tree-sidebar-list');
      const fullTreeContainer = document.getElementById('full-tree-container');
      sidebar.innerHTML = '<div style="padding: 0.5rem; color: var(--text-subtle); font-size: 0.8rem;">Loading repository tree...</div>';

      recordActivity('Fetch Tree', `${owner}/${repo}`);

      try {
        const resp = await fetch(`/api/repos/${owner}/${repo}/tree`);
        const treeData = await resp.json();
        state.activeRepoTree = treeData;
        if (treeData._rate_limit) updateRateLimit(treeData._rate_limit);

        const totalItemsBadge = document.getElementById('tree-total-items-badge');
        if (totalItemsBadge) totalItemsBadge.innerText = `${treeData.total_items || 0} items`;

        if (!treeData.items || treeData.items.length === 0) {
          sidebar.innerHTML = '<div style="padding: 0.5rem; color: var(--text-subtle);">No tree items found.</div>';
          return;
        }

        // Render Sidebar files
        sidebar.innerHTML = treeData.items.filter(item => item.type === 'blob').map(item => `
          <div class="file-tree-item ${state.activeFilePath === item.path ? 'active' : ''}" onclick="fetchAndDisplayFile('${item.path}')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path></svg>
            <span style="overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">${item.path}</span>
          </div>
        `).join('');

        // Render full tree table
        if (fullTreeContainer) {
          fullTreeContainer.innerHTML = `
            <table class="frameworks-table">
              <thead>
                <tr>
                  <th>Path</th>
                  <th>Type</th>
                  <th>Size</th>
                  <th>Git SHA</th>
                </tr>
              </thead>
              <tbody>
                ${treeData.items.map(i => `
                  <tr>
                    <td style="font-family: var(--font-mono); color: var(--text-main);">${i.path}</td>
                    <td><span class="status-tag ${i.type === 'tree' ? 'inferred' : 'documented'}">${i.type}</span></td>
                    <td style="font-family: var(--font-mono);">${i.size ? Math.round(i.size/1024) + ' KB' : '-'}</td>
                    <td style="font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-subtle);">${(i.sha || '').substring(0, 8)}</td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          `;
        }

        // Auto load README.md or first file
        const readme = treeData.items.find(i => i.path.toLowerCase() === 'readme.md');
        if (readme) {
          fetchAndDisplayFile('README.md');
        } else if (treeData.items.length > 0) {
          fetchAndDisplayFile(treeData.items[0].path);
        }

      } catch (err) {
        console.error('Error loading tree:', err);
      }
    }

    // Fetch and Display File Contents
    async function fetchAndDisplayFile(path) {
      if (!state.selectedRepo) return;
      const { owner, name } = state.selectedRepo;

      state.activeFilePath = path;
      document.getElementById('active-file-path').innerText = path;
      document.getElementById('active-file-content').innerText = `Loading ${path}...`;

      // Update sidebar active highlights
      document.querySelectorAll('.file-tree-item').forEach(el => {
        if (el.innerText.trim() === path) {
          el.classList.add('active');
        } else {
          el.classList.remove('active');
        }
      });

      recordActivity('Read File', `${owner}/${name}/${path}`);

      try {
        const resp = await fetch(`/api/repos/${owner}/${name}/file?path=${encodeURIComponent(path)}`);
        const fileObj = await resp.json();
        if (fileObj._rate_limit) updateRateLimit(fileObj._rate_limit);

        if (fileObj.error) {
          document.getElementById('active-file-content').innerText = `Error: ${fileObj.message}`;
          return;
        }

        state.activeFileContent = fileObj.content || '';
        document.getElementById('active-file-content').innerText = state.activeFileContent;
        document.getElementById('active-file-size').innerText = `${Math.round(fileObj.size_bytes / 1024)} KB ${fileObj.is_truncated ? '(Truncated)' : ''}`;

      } catch (err) {
        document.getElementById('active-file-content').innerText = `Error loading file: ${err.message}`;
      }
    }

    // Initialize application on page load
    window.addEventListener('DOMContentLoaded', () => {
      loadSystemStatus();
      loadClientConfigs();
      renderActivityLog();
    });
  </script>
</body>
</html>
"""
