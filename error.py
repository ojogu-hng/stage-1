from fastapi import FastAPI, Request, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
import logging


# Set up logger
exception_logger = logging.getLogger('exception_handler')
exception_logger.setLevel(logging.ERROR)

# Create handlers
console_handler = logging.StreamHandler()
file_handler = logging.FileHandler('error.log')

# Create formatters and add it to handlers
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(log_format)
file_handler.setFormatter(log_format)

# Add handlers to the logger
exception_logger.addHandler(console_handler)
exception_logger.addHandler(file_handler)


# Custom Exception Classes

class BaseExceptionClass(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class NotFoundError(BaseExceptionClass):
    pass


def register_error_handler(app:FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        exception_logger.error(f"HTTP {exc.status_code}: {exc.detail}")
        return JSONResponse(
            content={
                "status": "error",
                "message": exc.detail,
                "error_code": "http_error",
                "data": None,
            },
            status_code=exc.status_code
        )

    @app.exception_handler(ValidationError)
    async def pydantic_validation_error_handler(request: Request, exc: ValidationError):
        exception_logger.error(f"Pydantic validation error: {str(exc)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": "Validation error",
                "error_code": "pydantic_validation_error",
                "data": exc.json(),
                "model": exc.model.__name__ 
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    @app.exception_handler(RequestValidationError)
    async def bad_request_error_handler(request: Request, exc: RequestValidationError):
        exception_logger.error(f"Bad request error: {str(exc)}")
        return JSONResponse(
            content={
                "status": "error", 
                "message": "Invalid request parameters",
                "error_code": "bad_request_error",
                "data": str(exc.errors()),
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):
        exception_logger.error(f"Not found error: {str(exc)}")
        return JSONResponse(
            content={
                "status": "error",
                "message": str(exc.message) or "Not found",
                "error_code": "not_found_error",
                "data": None,
            },
            status_code=status.HTTP_404_NOT_FOUND
        )
