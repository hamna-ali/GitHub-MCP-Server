"""Live GitHub API integration verification script.

Demonstrates end-to-end execution of all 5 tools against real GitHub endpoints,
specifically verifying hamna-ali/Customer-Churn-Prediction as required for demo verification.
"""

import asyncio

from github_mcp.server import create_server


async def main():
    print("=" * 65)
    print("LIVE GITHUB MCP SERVER INTEGRATION VERIFICATION")
    print("=" * 65)

    server = create_server()
    tools = server._tool_manager._tools

    target_owner = "hamna-ali"
    target_repo = "Customer-Churn-Prediction"

    # 1. Test list_repositories tool
    print("\n[1/5] Testing tool: list_repositories")
    list_tool = tools["list_repositories"].fn
    list_result = await list_tool(username=target_owner)
    print(
        f"Status: Success! Found {list_result.get('count', 0)} repositories for '{target_owner}'."
    )
    for r in list_result.get("repositories", [])[:3]:
        print(
            f"  - {r['full_name']} | Language: {r.get('language')} | Stars: {r.get('stargazers_count')}"
        )

    # 2. Test get_repository_details tool
    print(f"\n[2/5] Testing tool: get_repository_details on '{target_owner}/{target_repo}'")
    details_tool = tools["get_repository_details"].fn
    details_result = await details_tool(owner=target_owner, repo=target_repo)
    if details_result.get("error"):
        print(f"FAILED: {details_result.get('message')}")
        return
    print("Status: Success!")
    print(f"  - Full Name: {details_result.get('full_name')}")
    print(f"  - Default Branch: {details_result.get('default_branch')}")
    print(f"  - Clone URL: {details_result.get('clone_url')}")
    print(f"  - Primary Language: {details_result.get('language')}")

    # 3. Test get_repository_tree tool
    print(f"\n[3/5] Testing tool: get_repository_tree on '{target_owner}/{target_repo}'")
    tree_tool = tools["get_repository_tree"].fn
    tree_result = await tree_tool(owner=target_owner, repo=target_repo)
    if tree_result.get("error"):
        print(f"FAILED: {tree_result.get('message')}")
        return
    print(f"Status: Success! Retrieved {tree_result.get('total_items', 0)} tree objects.")
    items_preview = [item["path"] for item in tree_result.get("items", [])[:8]]
    print(f"  - Tree items preview: {items_preview}")

    # 4. Test get_file_contents tool
    print(
        f"\n[4/5] Testing tool: get_file_contents for 'README.md' in '{target_owner}/{target_repo}'"
    )
    file_tool = tools["get_file_contents"].fn
    file_result = await file_tool(owner=target_owner, repo=target_repo, path="README.md")
    if file_result.get("error"):
        print(f"FAILED: {file_result.get('message')}")
        return
    print(f"Status: Success! Read {file_result.get('size_bytes')} bytes.")
    content_lines = file_result.get("content", "").splitlines()
    print(f"  - First line: {content_lines[0] if content_lines else ''}")
    print(f"  - Truncated: {file_result.get('is_truncated')}")

    # 5. Test analyze_ml_repository tool on Customer-Churn-Prediction
    print(f"\n[5/5] Testing tool: analyze_ml_repository on '{target_owner}/{target_repo}'")
    ml_tool = tools["analyze_ml_repository"].fn
    ml_result = await ml_tool(owner=target_owner, repo=target_repo)
    if ml_result.get("error"):
        print(f"FAILED: {ml_result.get('message')}")
        return
    print("Status: Success! ML Analysis completed:")
    print(f"  - Repository: {ml_result.get('repository')}")
    print(f"  - Is ML Project: {ml_result.get('is_ml_project')}")
    print(f"  - ML Confidence Score: {ml_result.get('ml_confidence_score')}")
    print(
        f"  - Problem Statement: [{ml_result.get('problem_statement', {}).get('status')}] {ml_result.get('problem_statement', {}).get('details')[:100]}..."
    )
    fws = [f["name"] for f in ml_result.get("frameworks", [])]
    print(f"  - Detected Frameworks ({len(fws)}): {', '.join(fws)}")
    print(
        f"  - Architecture: [{ml_result.get('model_architecture', {}).get('status')}] {ml_result.get('model_architecture', {}).get('details')[:100]}..."
    )
    print(
        f"  - Datasets: [{ml_result.get('datasets', {}).get('status')}] {ml_result.get('datasets', {}).get('details')[:100]}..."
    )
    print(
        f"  - Training Pipeline: [{ml_result.get('training_pipeline', {}).get('status')}] {ml_result.get('training_pipeline', {}).get('details')[:100]}..."
    )
    print(
        f"  - Evaluation: [{ml_result.get('evaluation_metrics', {}).get('status')}] {ml_result.get('evaluation_metrics', {}).get('details')[:100]}..."
    )
    print(
        f"  - Deployment: [{ml_result.get('deployment_approach', {}).get('status')}] {ml_result.get('deployment_approach', {}).get('details')[:100]}..."
    )
    print(
        f"  - Key Files Found ({len(ml_result.get('key_files_found', []))}): {ml_result.get('key_files_found', [])[:5]}"
    )
    print("\n" + "=" * 65)
    print("ALL 5 LIVE TOOLS VERIFIED SUCCESSFULLY AGAINST GITHUB REST API")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
