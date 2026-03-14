"""
This is the main application file for the Cognexus-OCR service.
It initializes the FastAPI application and includes the API router.
"""
from http.client import HTTPException

from fastapi import FastAPI

from api.v1.utils.exceptions import http_exception_handler, exception_handler
from api.v1_router import router

app = FastAPI()
app.include_router(router)
app.exception_handler(HTTPException)(http_exception_handler)
app.exception_handler(Exception)(exception_handler)