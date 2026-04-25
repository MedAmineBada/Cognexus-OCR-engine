from http.client import HTTPException
from typing import Any

from starlette import status
from starlette.responses import JSONResponse
from starlette.requests import Request

"""
Custom exception classes and global handlers for the API.

This module defines standard error responses and handlers to maintain
consistent error reporting across the service.
"""


class CustomException(HTTPException):
    """
    Base class for custom API exceptions.

    Attributes:
        status_code (int): The HTTP status code for the error.
        message (str): A descriptive error message.
    """

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: str = "Something went wrong.",
    ) -> None:
        self.status_code: int = status_code
        self.message: str = message
        super().__init__(self.message)


class UnprocessableContent(CustomException):
    """
    Exception raised when content cannot be processed by the engine.
    """

    def __init__(self, message: str = "Resource not found.") -> None:
        super().__init__(status.HTTP_422_UNPROCESSABLE_CONTENT, message)


async def exception_handler(req: Request, exc: Exception) -> JSONResponse:
    """
    Global handler for generic, unhandled exceptions.

    Args:
        req: The incoming request object.
        exc: The caught exception.

    Returns:
        A JSON response with a 500 status code.
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Something went wrong."},
    )


async def http_exception_handler(req: Request, exc: Any) -> JSONResponse:
    """
    Global handler for HTTP-specific exceptions.

    Args:
        req: The incoming request object.
        exc: The caught HTTP exception containing status and message.

    Returns:
        A JSON response with the exception's status code and message.
    """
    return JSONResponse(
        status_code=exc.status_code, content={"error": exc.message}
    )
