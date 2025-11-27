from GitHubMCPClient import GitHubMCPClient
from GeminiGitHubAgent import GeminiGitHubAgent


async def add_pr_comment(GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, TARGET_PR_NUMBER, GEN_API_KEY, MODEL_ID):
    """Adds a comment to PR if secrets are detected in the changes."""
    mcp = GitHubMCPClient(GITHUB_TOKEN)
    await mcp.start()
    
    try:
        agent = GeminiGitHubAgent(mcp, GEN_API_KEY=GEN_API_KEY, MODEL_ID=MODEL_ID)
        await agent.initialize()
        
        task = f"""
        Analyze pull request #{TARGET_PR_NUMBER} in repository {GITHUB_OWNER}/{GITHUB_REPO} 
        and detect if any secrets, credentials, or sensitive information have been committed.
        
        Follow these steps:
        1. First, use the appropriate tool to get all files and their changes in the PR
        2. Carefully examine each file's content and changes (patches/diffs) for:
           - API keys (patterns like 'api_key', 'apiKey', 'API_KEY')
           - Passwords (patterns like 'password', 'passwd', 'pwd')
           - Secret keys (patterns like 'secret', 'SECRET_KEY', 'private_key')
           - Tokens (patterns like 'token', 'access_token', 'auth_token')
           - Database credentials
           - OAuth secrets
           - Private keys or certificates
           - Any hardcoded sensitive values (long alphanumeric strings that look like credentials)
        
        3. If you find ANY secrets or suspicious credentials:
           - Identify the exact file name and line number where the secret was found
           - Add a general PR comment summarizing the findings
           - Make sure to post the comment on the PR
           - The comment should be professional, clear, and include:
             * What type of secret was detected
             * Why this is a security risk
             * Recommendation to remove it and use environment variables instead
             * Suggestion to rotate/invalidate the exposed credential if already committed
        
        4. If you add comments, summarize what secrets were found and where
        5. If no secrets are found, confirm that the PR looks secure
        6. Post the comment using this endpoint:
            url = "https://api.github.com/repos/OWNER/REPO/issues/PR_NUMBER/comments"
            data = {{"body": "Insert what you found here"}}
            response = requests.post(url, json=data, headers=headers)
        
        Be thorough and check all added or modified lines carefully. Security is critical.
        """
        
        result = await agent.execute_task(task)
        # print("\n" + "="*60)
        # print("SECRET DETECTION RESULT:")
        # print(result)
        # print("="*60)
        return result

    finally:
        await mcp.stop()


async def list_pr_files(GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, TARGET_PR_NUMBER, GEN_API_KEY, MODEL_ID):
    """Lists all files modified in a pull request."""
    mcp = GitHubMCPClient(GITHUB_TOKEN)
    await mcp.start()
    
    try:
        agent = GeminiGitHubAgent(mcp, GEN_API_KEY=GEN_API_KEY, MODEL_ID=MODEL_ID)
        await agent.initialize()
        
        task = f"""
        Use the appropriate tool to list all modified files in pull request #{TARGET_PR_NUMBER} 
        from repository {GITHUB_OWNER}/{GITHUB_REPO}.
        
        Look for a tool named something like "list_pull_request_files" or "get_pull_request_files" 
        and use it with the correct parameters.
        
        Provide a complete list of all files found with their modification status.
        """
        
        result = await agent.execute_task(task)
        # print("="*60)
        # print("FILES IN PR:")
        # print(result)
        # print("="*60)
        return result
        
    finally:
        await mcp.stop()


async def analyze_pr(GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, TARGET_PR_NUMBER, GEN_API_KEY, MODEL_ID):
    """Performs a comprehensive analysis of a pull request."""
    mcp = GitHubMCPClient(GITHUB_TOKEN)
    await mcp.start()
    
    try:
        agent = GeminiGitHubAgent(mcp, GEN_API_KEY=GEN_API_KEY, MODEL_ID=MODEL_ID)
        await agent.initialize()
        
        task = f"""
        Analyze pull request #{TARGET_PR_NUMBER} from repository {GITHUB_OWNER}/{GITHUB_REPO}.
        
        Perform the following analysis:
        1. List all modified files
        2. Check for obvious security issues
        3. Suggest improvements if applicable
        4. Provide a summary of the changes
        
        Be thorough and provide actionable insights.
        """
        
        result = await agent.execute_task(task)
        # print("\n" + "="*60)
        # print("PR ANALYSIS:")
        # print(result)
        # print("="*60)
        return result

    finally:
        await mcp.stop()