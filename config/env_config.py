from pydantic_settings import BaseSettings


class EnvFile(BaseSettings):
    MODEL_BASE: str
    MODEL_BASE_FILE: str
    MODEL_DETECT: str

    HFTOKEN: str

    MODE: str

    class Config:
        env_file = ".env"

env = EnvFile()
