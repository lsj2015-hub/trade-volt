# ===========================================
# server/app/main.py - 메인 애플리케이션 파일
# ===========================================
import logging
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from app.config import settings
from app.schemas import (
    TranslationRequest, TranslationResponse,
    StockOverviewResponse, FinancialStatementResponse, PriceHistoryResponse,
    NewsResponse, AIChatRequest, AIChatResponse,
    SectorAnalysisRequest, SectorAnalysisResponse,
    StockComparisonRequest, StockComparisonResponse,
    TradingVolumeRequest, TradingVolumeResponse,
    NetPurchaseRequest, NetPurchaseResponse,
    FluctuationAnalysisRequest, FluctuationAnalysisResponse,
    NewsSearchRequest, NewsSearchResponse
)
from app.core.dependencies import (
    get_services, get_yahoo_finance_service, get_krx_service,
    get_news_service, get_translation_service, get_llm_service,
    get_fluctuation_service, get_news_scalping_service,
    get_korea_investment_service
)
from app.services.yahoo_finance import YahooFinanceService
from app.services.krx_service import PyKRXService
from app.services.news import NewsService
from app.services.translation import TranslationService
from app.services.llm import LLMService
from app.services.fluctuation_service import FluctuationService
from app.services.news_scalping_service import NewsScalpingService
from app.services.korea_investment_service import KoreaInvestmentService

# API 라우터 임포트
from app.api import search

# 로깅 설정
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger(__name__)

# 앱 라이프사이클 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Trade Volt API 서버 시작")
    
    try:
        # 서비스 초기화
        services = get_services()
        logger.info("✅ 기본 서비스 초기화 완료")
        
        # KIS 서비스 초기화
        kis_service = get_korea_investment_service()
        logger.info("✅ 한국투자증권 API 서비스 초기화 완료")
        
        # 뉴스 스크래핑 서비스 초기화 (백그라운드에서 기업 데이터 로드)
        news_scalping_service = get_news_scalping_service()
        await news_scalping_service.load_corp_data()
        logger.info("✅ 뉴스 스크래핑 서비스 초기화 완료")
        
        logger.info("🎉 모든 서비스 초기화 완료")
        
    except Exception as e:
        logger.error(f"❌ 서비스 초기화 중 오류 발생: {e}")
        # 오류가 발생해도 서버는 시작되도록 함
    
    yield
    
    logger.info("🛑 Trade Volt API 서버 종료")

# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    description="한국투자증권 & 키움 REST API 기반 주식 매매 전략 시스템",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    debug=settings.DEBUG
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 글로벌 예외 핸들러
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"글로벌 예외 발생: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "서버 내부 오류가 발생했습니다."}
    )

# API 라우터 등록
app.include_router(search.router, prefix="/api", tags=["Stock Search"])

# 기본 라우트
@app.get("/")
async def root():
    return {
        "message": f"{settings.APP_NAME} v{settings.APP_VERSION}",
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # 기본 서비스들의 상태 확인
        services = get_services()
        
        # KIS 서비스 상태 확인
        kis_service = get_korea_investment_service()
        kis_status = kis_service.test_connection()
        
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "services": {
                "yahoo_finance": "available",
                "krx": "available", 
                "news": "available",
                "translation": "available",
                "llm": "available",
                "korea_investment": "connected" if kis_status else "disconnected",
                "fluctuation": "available",
                "news_scalping": "available"
            },
            "environment": "production" if settings.is_production else "development"
        }
    except Exception as e:
        logger.error(f"헬스 체크 실패: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )

# === 번역 API ===
@app.post("/api/translate", response_model=TranslationResponse, tags=["Translation"])
async def translate_text(
    request: TranslationRequest,
    ts: TranslationService = Depends(get_translation_service)
):
    """텍스트를 번역합니다."""
    try:
        translated_text = ts.translate(request.text)
        return {"translated_text": translated_text}
    except Exception as e:
        logger.error(f"번역 API 오류: {e}")
        raise HTTPException(status_code=500, detail="번역 중 오류가 발생했습니다.")

# === 주식 정보 API ===
@app.get("/api/stock/{ticker}/overview", response_model=StockOverviewResponse, tags=["Stock Info"])
async def get_stock_overview(
    ticker: str,
    yf: YahooFinanceService = Depends(get_yahoo_finance_service)
):
    """주식 개요 정보를 조회합니다."""
    try:
        overview = await run_in_threadpool(yf.get_stock_overview, ticker)
        if overview is None:
            raise HTTPException(status_code=404, detail=f"'{ticker}' 종목을 찾을 수 없습니다.")
        return overview
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"주식 개요 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="주식 개요 조회 중 오류가 발생했습니다.")

@app.get("/api/stock/{ticker}/financials", response_model=FinancialStatementResponse, tags=["Stock Info"])
async def get_financial_statements(
    ticker: str,
    yf: YahooFinanceService = Depends(get_yahoo_finance_service)
):
    """재무제표를 조회합니다."""
    try:
        financials = await run_in_threadpool(yf.get_financial_statements, ticker)
        if financials is None:
            raise HTTPException(status_code=404, detail=f"'{ticker}' 재무제표를 찾을 수 없습니다.")
        return financials
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"재무제표 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="재무제표 조회 중 오류가 발생했습니다.")

@app.get("/api/stock/{ticker}/history", response_model=PriceHistoryResponse, tags=["Stock Info"])
async def get_price_history(
    ticker: str,
    period: str = "1y",
    yf: YahooFinanceService = Depends(get_yahoo_finance_service)
):
    """주가 이력을 조회합니다."""
    try:
        history = await run_in_threadpool(yf.get_price_history, ticker, period)
        if history is None or history.empty:
            raise HTTPException(status_code=404, detail=f"'{ticker}' 주가 이력을 찾을 수 없습니다.")
        
        # DataFrame을 딕셔너리로 변환
        history_data = history.reset_index().to_dict(orient='records')
        return {"data": history_data}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"주가 이력 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="주가 이력 조회 중 오류가 발생했습니다.")

# === 뉴스 API ===
@app.get("/api/news/{ticker}", response_model=NewsResponse, tags=["News"])
async def get_stock_news(
    ticker: str,
    count: int = 10,
    news_service: NewsService = Depends(get_news_service)
):
    """주식 관련 뉴스를 조회합니다."""
    try:
        news_data = await run_in_threadpool(news_service.get_stock_news, ticker, count)
        return {"news": news_data}
    except Exception as e:
        logger.error(f"뉴스 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="뉴스 조회 중 오류가 발생했습니다.")

@app.post("/api/news/search", response_model=NewsSearchResponse, tags=["News"])
async def search_news(
    request: NewsSearchRequest,
    news_scalping_service: NewsScalpingService = Depends(get_news_scalping_service)
):
    """뉴스를 검색합니다."""
    try:
        results = await news_scalping_service.search_news(
            query=request.query,
            start_date=request.start_date,
            end_date=request.end_date,
            source=request.source,
            limit=request.limit
        )
        return {"results": results, "total": len(results)}
    except Exception as e:
        logger.error(f"뉴스 검색 오류: {e}")
        raise HTTPException(status_code=500, detail="뉴스 검색 중 오류가 발생했습니다.")

# === AI 채팅 API ===
@app.post("/api/chat", response_model=AIChatResponse, tags=["AI"])
async def ai_chat(
    request: AIChatRequest,
    llm: LLMService = Depends(get_llm_service)
):
    """AI와 채팅합니다."""
    try:
        response = await llm.chat(request.message, request.context)
        return {"response": response}
    except Exception as e:
        logger.error(f"AI 채팅 오류: {e}")
        raise HTTPException(status_code=500, detail="AI 채팅 중 오류가 발생했습니다.")

# === 분석 API ===
@app.post("/api/analysis/sectors", response_model=SectorAnalysisResponse, tags=["Analysis"])
async def analyze_sectors(
    request: SectorAnalysisRequest,
    krx: PyKRXService = Depends(get_krx_service)
):
    """섹터 분석을 수행합니다."""
    try:
        result = await run_in_threadpool(
            krx.analyze_sector_performance, 
            request.tickers, 
            request.start_date, 
            request.end_date
        )
        return result
    except Exception as e:
        logger.error(f"섹터 분석 오류: {e}")
        raise HTTPException(status_code=500, detail="섹터 분석 중 오류가 발생했습니다.")

@app.post("/api/analysis/comparison", response_model=StockComparisonResponse, tags=["Analysis"])
async def compare_stocks(
    request: StockComparisonRequest,
    yf: YahooFinanceService = Depends(get_yahoo_finance_service)
):
    """주식 비교 분석을 수행합니다."""
    try:
        result = await run_in_threadpool(
            yf.compare_stocks,
            request.tickers,
            request.start_date,
            request.end_date
        )
        return result
    except Exception as e:
        logger.error(f"주식 비교 분석 오류: {e}")
        raise HTTPException(status_code=500, detail="주식 비교 분석 중 오류가 발생했습니다.")

@app.post("/api/analysis/volume", response_model=TradingVolumeResponse, tags=["Analysis"])
async def analyze_trading_volume(
    request: TradingVolumeRequest,
    krx: PyKRXService = Depends(get_krx_service)
):
    """거래량 분석을 수행합니다."""
    try:
        result = await run_in_threadpool(
            krx.analyze_trading_volume,
            request.market,
            request.date,
            request.top_n
        )
        return result
    except Exception as e:
        logger.error(f"거래량 분석 오류: {e}")
        raise HTTPException(status_code=500, detail="거래량 분석 중 오류가 발생했습니다.")

@app.post("/api/analysis/net-purchase", response_model=NetPurchaseResponse, tags=["Analysis"])
async def analyze_net_purchase(
    request: NetPurchaseRequest,
    krx: PyKRXService = Depends(get_krx_service)
):
    """순매수 분석을 수행합니다."""
    try:
        result = await run_in_threadpool(
            krx.analyze_net_purchase,
            request.market,
            request.start_date,
            request.end_date,
            request.investor_type
        )
        return result
    except Exception as e:
        logger.error(f"순매수 분석 오류: {e}")
        raise HTTPException(status_code=500, detail="순매수 분석 중 오류가 발생했습니다.")

@app.post("/api/analysis/fluctuation", response_model=FluctuationAnalysisResponse, tags=["Analysis"])
async def analyze_fluctuation(
    request: FluctuationAnalysisRequest,
    fluctuation_service: FluctuationService = Depends(get_fluctuation_service)
):
    """등락률 분석을 수행합니다."""
    try:
        result = await run_in_threadpool(
            fluctuation_service.analyze_fluctuation,
            request.market,
            request.date,
            request.sort_by,
            request.limit
        )
        return result
    except Exception as e:
        logger.error(f"등락률 분석 오류: {e}")
        raise HTTPException(status_code=500, detail="등락률 분석 중 오류가 발생했습니다.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )