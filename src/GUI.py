import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import asyncio
from tkinter import simpledialog
from Functions import add_pr_comment, list_pr_files, analyze_pr
import os
from dotenv import load_dotenv, set_key


ENV_FILE = ".env"
REQUIRED_VARS = [
    "GITHUB_PAT_TOKEN",
    "GITHUB_OWNER",
    "GITHUB_REPO",
    "TARGET_PR_NUMBER",
    "GOOGLE_API_KEY",
    "MODEL_ID"
]

root = tk.Tk()
root.withdraw()
root.title("repo-checker")
root.geometry("800x400")

if not os.path.exists(ENV_FILE):
    open(ENV_FILE, "w").close()

load_dotenv(ENV_FILE)

for var in REQUIRED_VARS:
    value = os.getenv(var)
    if not value:
        user_value = simpledialog.askstring(var, f"Input {var}:")
        if user_value:
            set_key(ENV_FILE, var, user_value)

load_dotenv(ENV_FILE)

GITHUB_TOKEN = os.getenv("GITHUB_PAT_TOKEN")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
TARGET_PR_NUMBER = os.getenv("TARGET_PR_NUMBER")
GEN_API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_ID = os.getenv("MODEL_ID")

root.deiconify()

def set_repo_info(username: str, repository: str):
    if not username.strip() or not repository.strip():
        messagebox.showwarning("Input error", "GitHub username and repository must be filled!")
        return
    
    global GITHUB_OWNER, GITHUB_REPO
    GITHUB_OWNER = username
    GITHUB_REPO = repository



frame_buttons = tk.Frame(root)
frame_buttons.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

frame_results = tk.Frame(root)
frame_results.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

text_results = scrolledtext.ScrolledText(frame_results, wrap=tk.WORD)
text_results.pack(fill=tk.BOTH, expand=True)


def run_async_in_thread(async_func):
    def worker():
        result = asyncio.run(async_func(GITHUB_OWNER, GITHUB_REPO, GITHUB_TOKEN, TARGET_PR_NUMBER))
        text_results.after(0, lambda: text_results.insert(tk.END, str(result) + "\n"))
    
    threading.Thread(target=worker).start()


tk.Button(frame_buttons, text="1. Add PR comment", width=20,
          command=lambda: run_async_in_thread(add_pr_comment)).pack(pady=5)
tk.Button(frame_buttons, text="2. List all files in PR", width=20,
          command=lambda: run_async_in_thread(list_pr_files)).pack(pady=5)
tk.Button(frame_buttons, text="3. Analyze full PR", width=20,
          command=lambda: run_async_in_thread(analyze_pr)).pack(pady=5)

tk.Label(frame_buttons, text="GitHub username:").pack(pady=5)
username_entry = tk.Entry(frame_buttons, width=30)
username_entry.pack(pady=5)
username_entry.insert(0, GITHUB_OWNER)

tk.Label(frame_buttons, text="Repository:").pack(pady=5)
repository_entry = tk.Entry(frame_buttons, width=30)
repository_entry.pack(pady=5)
repository_entry.insert(0, GITHUB_REPO)

tk.Button(frame_buttons, text="Submit", width=20,
          command=lambda: set_repo_info(username_entry.get(), repository_entry.get())).pack(pady=5)


root.mainloop()