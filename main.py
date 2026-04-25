from http.client import HTTPException
from typing import NoReturn

import uvicorn
from fastapi import FastAPI

from api.v1.utils.exceptions import http_exception_handler, exception_handler
from api.v1.v1_router import router

"""
Entry point for the OCR Engine FastAPI application.

This module initializes the FastAPI app, attaches global exception handlers,
and includes versioned API routers.
"""

app: FastAPI = FastAPI(title="Cognexus OCR Engine")

app.include_router(router)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, exception_handler)


def start() -> NoReturn:
    """
    Runs the FastAPI application using the Uvicorn server.

    This function starts the web server on host 0.0.0.0 and port 8011,
    with auto-reload enabled for development.
    """
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8011,
        reload=True,
    )


if __name__ == "__main__":
    start()
