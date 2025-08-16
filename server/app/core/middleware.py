# ===========================================
# server/app/core/middleware.py - 성능 모니터링 미들웨어
# ===========================================

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
import time
import logging
from typing import Callable

logger = logging.getLogger(__name__)

class PerformanceCacheMiddleware(BaseHTTPMiddleware):
    """성능 분석 API 캐시 미들웨어"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # 성과 분석 API 감지
        is_performance_api = "/api/performance/" in str(request.url)
        
        if is_performance_api:
            logger.info(f"📊 성능 분석 API 요청: {request.method} {request.url}")
            
            # 요청 파라미터 로깅
            if request.method == "POST":
                try:
                    # POST 요청의 경우 body 정보 로깅 (민감하지 않은 정보만)
                    pass  # 실제로는 body를 읽으면 소비되므로 주의
                except:
                    pass
        
        # 응답 처리
        response = await call_next(request)
        
        if is_performance_api:
            process_time = time.time() - start_time
            
            # 응답 시간에 따른 로그 레벨 조정
            if process_time > 60:  # 1분 이상
                logger.warning(f"🐌 느린 성능 분석 API: {process_time:.2f}초")
            elif process_time > 10:  # 10초 이상
                logger.info(f"📊 성능 분석 API 완료: {process_time:.2f}초")
            else:
                logger.info(f"⚡ 빠른 성능 분석 API: {process_time:.2f}초 (캐시 히트 가능성)")
            
            # 응답 헤더에 처리 시간과 캐시 정보 추가
            response.headers["X-Process-Time"] = f"{process_time:.3f}"
            response.headers["X-Cache-Info"] = "enabled"
            
            # 캐시 히트 여부 추정 (매우 빠른 응답은 캐시일 가능성 높음)
            if process_time < 2:
                response.headers["X-Cache-Hit"] = "likely"
            else:
                response.headers["X-Cache-Hit"] = "miss"
        
        return response
    
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """보안 헤더 추가 미들웨어"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # 보안 헤더 추가
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        return response