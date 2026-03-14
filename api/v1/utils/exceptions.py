"""
Custom exception classes and handlers for the API.
"""
from http.client import HTTPException

from starlette import status
from starlette.responses import JSONResponse


class CustomException(HTTPException):
    """
    Base class for custom API exceptions.
    """
    def __init__(self, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR, message: str = "Something went wrong."):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

class UnprocessableContent(CustomException):
    """
    Exception raised when content cannot be processed (HTTP 422).
    """
    def __init__(self,message: str = "Resource not found."):
        super().__init__(status.HTTP_422_UNPROCESSABLE_CONTENT, message)


async def exception_handler(req, exc):
    """
    Global handler for generic exceptions.
    """
    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": "Something went wrong."})

async def http_exception_handler(req, exc):
    """
    Global handler for HTTP exceptions.
    """
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})
