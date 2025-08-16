# app/core/exceptions.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    HTTPException 외의 처리되지 않은 모든 예외를 처리합니다.
    서버가 죽는 것을 방지하고 일관된 오류 응답을 반환합니다.
    """
    logger.error(f"처리되지 않은 예외 발생: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "서버 내부에서 예상치 못한 오류가 발생했습니다.",
            "error_type": type(exc).__name__
        },
    )

async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """
    HTTPException이 발생했을 때 로그를 남깁니다.
    """
    logger.warning(f"HTTP 예외 발생: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )