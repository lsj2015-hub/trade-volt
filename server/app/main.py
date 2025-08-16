# ===========================================
# server/app/main.py - 서버 시작시 캐시 상태 로깅 추가
# ===========================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import Settings
from app.core.dependencies import get_services
from app.api import (
    stock_router,
    search_router,
    analysis_router,
    utils_router,
    sectors_router,
    krx_router
)

# 로거 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 설정
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """서버 시작/종료 시 실행되는 로직"""
    logger.info("🚀 Trade Volt API 서버 시작...")
    
    # ✅ 설정 정보 로깅
    logger.info(f"📊 성능 설정: MAX_TICKERS={settings.PERFORMANCE_MAX_TICKERS}, "
               f"CHUNK_SIZE={settings.PERFORMANCE_CHUNK_SIZE}, "
               f"TIMEOUT={settings.PERFORMANCE_TIMEOUT}s")
    logger.info(f"💾 Redis 설정: {settings.REDIS_HOST}:{settings.REDIS_PORT}, "
               f"DB={settings.REDIS_DB}, TTL={settings.PERFORMANCE_CACHE_TTL}s")
    
    # 서비스 초기화
    services = get_services()
    
    # ✅ 캐시 서비스 상태 확인
    try:
        cache_stats = services.performance.get_cache_stats()
        logger.info(f"💾 캐시 서비스 초기화 완료: "
                   f"Redis={cache_stats['redis_enabled']}, "
                   f"Host={cache_stats.get('redis_host', 'N/A')}")
        
        if cache_stats['redis_enabled']:
            logger.info("✅ Redis 캐시 활성화 - 고성능 캐싱 사용")
        else:
            logger.info("⚠️ 메모리 캐시 사용 - Redis 연결 실패 또는 미설치")
            
    except Exception as e:
        logger.warning(f"캐시 서비스 초기화 실패: {e}")
    
    # 필요한 데이터 미리 로드
    await services.news_scalping_service.load_corp_data()
    
    logger.info("✅ 서버 시작 준비 완료")
    yield
    
    # ✅ 서버 종료시 캐시 정리
    try:
        logger.info("💾 서버 종료: 캐시 정리 시작...")
        cache_clear_result = services.performance.clear_cache()
        if cache_clear_result:
            logger.info("✅ 캐시 정리 완료")
        else:
            logger.warning("⚠️ 캐시 정리 실패")
    except Exception as e:
        logger.warning(f"캐시 정리 중 오류: {e}")
    
    logger.info("🔄 서버를 종료합니다.")

# FastAPI 앱 생성
app = FastAPI(
    title="Trade Volt API",
    version="1.0.0",
    description="API 기반 주식 매매 전략 플랫폼 (캐싱 최적화)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 미들웨어
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(search_router, prefix="/api", tags=["Stock Search"])
app.include_router(stock_router, prefix="/api", tags=["Stock Info"])
app.include_router(analysis_router, prefix="/api", tags=["Analysis"])
app.include_router(sectors_router, prefix="/api", tags=["Sectors"])
app.include_router(krx_router, prefix="/api", tags=["KRX"])
app.include_router(utils_router, prefix="/api", tags=["Utilities"])

# ✅ 개선된 헬스체크 (캐시 상태 포함)
@app.get("/", tags=["Health"])
async def health_check():
    """서버 상태 확인 (캐시 정보 포함)"""
    try:
        services = get_services()
        cache_stats = services.performance.get_cache_stats()
        
        return {
            "status": "ok", 
            "message": "Trade Volt API is running",
            "version": "1.0.0",
            "cache": {
                "redis_enabled": cache_stats["redis_enabled"],
                "memory_cache_size": cache_stats["memory_cache_size"],
                "redis_keys": cache_stats["redis_keys"]
            },
            "performance_config": {
                "max_tickers": settings.PERFORMANCE_MAX_TICKERS,
                "chunk_size": settings.PERFORMANCE_CHUNK_SIZE,
                "timeout": settings.PERFORMANCE_TIMEOUT,
                "cache_ttl": settings.PERFORMANCE_CACHE_TTL
            }
        }
    except Exception as e:
        logger.error(f"헬스체크 중 오류: {e}")
        return {
            "status": "ok", 
            "message": "Trade Volt API is running",
            "version": "1.0.0",
            "cache": "unavailable"
        }

@app.get("/health/cache", tags=["Health"])
async def cache_health_check():
    """캐시 상태 전용 확인"""
    try:
        services = get_services()
        return services.performance.get_cache_stats()
    except Exception as e:
        logger.error(f"캐시 헬스체크 오류: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )