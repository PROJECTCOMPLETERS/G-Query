from fastapi import Request
from fastapi.responses import JSONResponse


class SatQueryException(Exception):
    """Base exception for SatQuery backend errors."""

    def __init__(
        self,
        message: str,
        code: str = "SATQUERY_ERROR",
        status_code: int = 400,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


async def satquery_exception_handler(
    request: Request,
    exc: SatQueryException,
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
            },
        },
    )