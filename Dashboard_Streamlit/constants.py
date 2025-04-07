import os


# Constants
MODEL_OPTIONS = [
    "openai/gpt-3.5-turbo",
    "openai/gpt-4o-mini",
    "google/gemini-pro",
    "anthropic/claude-3-haiku",
    "deepseek/deepseek-chat:free",
    "meta-llama/llama-3-8b-instruct"
]

TEST_SCRIPTS_DIR = "TestScripts"
os.makedirs(TEST_SCRIPTS_DIR, exist_ok=True)  # Ensure directory exists
