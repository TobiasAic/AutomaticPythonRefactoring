import os
from dotenv import load_dotenv

def get_env_variable(key: str) -> str:
    load_dotenv()  # Load environment variables from .env file
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable '{key}' not found.")
    return value