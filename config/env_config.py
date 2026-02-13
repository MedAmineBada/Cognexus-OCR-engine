from pydantic_settings import BaseSettings


class EnvFile(BaseSettings):
    MODEL_BASE: str
    MODEL_BASE_FILE: str
    MODEL_BASE_MMPROJ: str

    MODEL_DETECT: str
    MODEL_DETECT_FILE: str

    HFTOKEN: str

    MAX_SIZE:int
    MODE: str
    CORES: int
    class Config:
        env_file = ".env"

env = EnvFile()
