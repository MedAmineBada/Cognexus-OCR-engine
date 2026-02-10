from pathlib import Path

from fastapi import FastAPI
from api.main_router import router

app = FastAPI()

app.include_router(router)
project_root = Path(__file__)
print(project_root)