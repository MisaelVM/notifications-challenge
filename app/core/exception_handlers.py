from collections.abc import Mapping
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse


class CustomException(HTTPException):
    def __init__(
        self,
        error_code: str,
        status_code: int,
        detail: Any,  # noqa: ANN401
        headers: Mapping[str, str] | None = None,
    ) -> None:
        self.error_code: str = error_code
        super().__init__(status_code, detail, headers)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(CustomException)
    async def custom_exception_handler(
        _request: Request, exception: CustomException
    ) -> JSONResponse:
        headers = getattr(exception, "headers", None)
        return JSONResponse(
            {"error_code": exception.error_code, "detail": exception.detail},
            status_code=exception.status_code,
            headers=headers,
        )
