import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_env_variable(name, default=None, required=True):
    val = os.getenv(name, default)
    if required and not val:
        print(f"Error: Environment variable {name} is not set.")
        sys.exit(1)
    return val.strip() if val else val

# API Credentials
try:
    API_ID = int(get_env_variable("API_ID"))
except ValueError:
    print("Error: API_ID must be an integer.")
    sys.exit(1)
API_HASH = get_env_variable("API_HASH")
BOT_TOKEN = get_env_variable("BOT_TOKEN")

# Channel IDs
try:
    SOURCE_CHANNEL_ID = int(get_env_variable("SOURCE_CHANNEL_ID"))
    TARGET_CHANNEL_ID = int(get_env_variable("TARGET_CHANNEL_ID"))
except ValueError:
    print("Error: Channel IDs must be integers.")
    sys.exit(1)

# Helper for initial session generation
PHONE_NUMBER = os.getenv("phone_number")

# Session strings for Koyeb deployment (no file-based sessions)
USER_SESSION_STRING = os.getenv("USER_SESSION_STRING", "")
BOT_SESSION_STRING = os.getenv("BOT_SESSION_STRING", "")
