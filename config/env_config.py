from pydantic_settings import BaseSettings

"""
Environment-based configuration management.

This module leverages Pydantic to load and validate application
settings from environment variables or a .env file.
"""


class EnvFile(BaseSettings):
    """
    Schema for environment variables and application settings.

    This class defines the expected configuration parameters, their types,
    and sources from the environment.
    """

    MODEL_BASE: str
    MODEL_BASE_FILE: str
    MODEL_BASE_MMPROJ: str

    HFTOKEN: str

    MAX_SIDE: int

    MODE: str
    CORES: int

    class Config:
        env_file: str = ".env"


env: EnvFile = EnvFile()
