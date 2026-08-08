from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.environ["ANTHROPIC_API_KEY"]
BASE_URL = os.environ["ANTHROPIC_BASE_URL"]
MODEL = "claude-sonnet-4-6"
