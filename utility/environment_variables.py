import os

from dotenv import load_dotenv


def get_env_variable(key: str) -> str:
    """Get a variable from the enviroment.

    Args:
        key (str): The key of the environment variable to retrieve.

    Raises:
        ValueError: If the environment variable is not found. 

    Returns:
        str: The value of the environment variable. 
    """
    load_dotenv()  # Load environment variables from .env file
    value = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable '{key}' not found.")
    return value