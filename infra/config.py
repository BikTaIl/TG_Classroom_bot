import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
GITHUB_TOKEN = os.getenv("GITHUB_CLASSROOM_TOKEN")
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")