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
    
    # 서비스 초기화
    services = get_services()
    
    # 필요한 데이터 미리 로드
    await services.news_scalping_service.load_corp_data()
    
    logger.info("✅ 서버 시작 준비 완료")
    yield
    logger.info("🔄 서버를 종료합니다.")

# FastAPI 앱 생성
app = FastAPI(
    title="Trade Volt API",
    version="1.0.0",
    description="API 기반 주식 매매 전략 플랫폼",
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

# 기본 헬스체크
@app.get("/", tags=["Health"])
async def health_check():
    """서버 상태 확인"""
    return {
        "status": "ok", 
        "message": "Trade Volt API is running",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )