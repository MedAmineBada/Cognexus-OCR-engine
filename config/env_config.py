"""
This module defines the environment variables used by the application
and loads them using Pydantic's BaseSettings.
"""
from pydantic_settings import BaseSettings


class EnvFile(BaseSettings):
    """
    Represents the environment variables loaded from the .env file.
    """
    MODEL_BASE: str
    """The base model name for the VLM."""
    MODEL_BASE_FILE: str
    """The file path for the base model."""
    MODEL_BASE_MMPROJ: str
    """The mmproj file path for the base model."""

    MODEL_DETECT: str
    """The detection model name."""
    MODEL_DETECT_FILE: str
    """The file path for the detection model."""

    HFTOKEN: str
    """Hugging Face authentication token."""

    MAX_SIDE:int
    """Maximum side length for image preprocessing."""

    MODE: str
    """The application's running mode (e.g., development, production)."""
    CORES: int
    """The number of CPU cores to utilize."""
    class Config:
        env_file = ".env"

env = EnvFile()
"""An instance of EnvFile containing the loaded environment variables."""
