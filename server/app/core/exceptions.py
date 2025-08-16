# app/core/exceptions.py
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import asyncio


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

async def performance_timeout_handler(request: Request, exc: asyncio.TimeoutError) -> JSONResponse:
    """성능 분석 타임아웃 전용 예외 처리"""
    logger.error(f"성능 분석 타임아웃: {request.url}")
    
    return JSONResponse(
        status_code=408,
        content={
            "detail": "요청 처리 시간이 초과되었습니다.",
            "suggestion": "더 작은 기간이나 개수로 다시 시도해주세요.",
            "error_type": "PerformanceTimeout",
            "url": str(request.url)
        }
    )

async def cache_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """캐시 관련 예외 처리"""
    logger.warning(f"캐시 오류 (서비스 계속 제공): {exc}")
    
    # 캐시 오류는 서비스에 영향을 주지 않도록 처리
    return JSONResponse(
        status_code=200,
        content={
            "detail": "캐시 서비스에 일시적 문제가 있지만 요청은 정상 처리됩니다.",
            "cache_status": "degraded",
            "performance_impact": "응답 시간이 평소보다 길 수 있습니다."
        }
    )