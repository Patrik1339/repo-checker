import os
import asyncio
from dotenv import load_dotenv
from Functions import *


load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_PAT_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
TARGET_PR_NUMBER = os.getenv("TARGET_PR_NUMBER")
GEN_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")


async def main():
    while(True):
        print("=" * 20)
        print("Options:")
        print("0. Exit")
        print("1. Add PR comment")
        print("2. List all files in PR")
        print("3. Analyze full PR")
        print("=" * 20)
        
        choice = input("Choose option (1-3): ")
        
        match choice:
            case "0":
                return
            case "1":
                await add_pr_comment(GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, TARGET_PR_NUMBER)
            case "2":
                await list_pr_files(GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, TARGET_PR_NUMBER)
            case "3":
                await analyze_pr(GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, TARGET_PR_NUMBER)
            case _:
                print("Invalid option")

if __name__ == "__main__":
    asyncio.run(main())