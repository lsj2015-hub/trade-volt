# ===========================================
# server/app/main.py - 서버 시작시 캐시 상태 로깅 추가
# ===========================================
import logging
import pandas as pd
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.concurrency import run_in_threadpool

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
    get_fluctuation_service, get_news_scalping_service
)
from app.services.yahoo_finance import YahooFinanceService
from app.services.krx_service import PyKRXService
from app.services.news import NewsService
from app.services.translation import TranslationService
from app.services.llm import LLMService
from app.services.fluctuation_service import FluctuationService
from app.services.news_scalping_service import NewsScalpingService

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 앱 라이프사이클 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 애플리케이션 시작")
    # 서비스 초기화
    services = get_services()
    logger.info("✅ 모든 서비스 초기화 완료")
    yield
    logger.info("🛑 애플리케이션 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Trade Volt API",
    description="한국투자증권 & 키움 REST API 기반 주식 매매 전략 시스템",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 기본 라우트
@app.get("/")
async def root():
    return {"message": "Trade Volt API Server", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# === 번역 API ===
@app.post("/api/translate", response_model=TranslationResponse, tags=["Translation"])
async def translate_text(
    request: TranslationRequest,
    ts: TranslationService = Depends(get_translation_service)
):
    try:
        translated_text = ts.translate(request.text)
        return {"translated_text": translated_text}
    except Exception as e:
        logger.error(f"번역 API 오류: {e}")
        raise HTTPException(status_code=500, detail="번역 중 오류가 발생했습니다.")

# === 주식 정보 API ===
@app.get("/api/stock/{symbol}/overview", response_model=StockOverviewResponse, tags=["Stock Info"])
async def get_stock_overview(
    symbol: str,
    yfs: YahooFinanceService = Depends(get_yahoo_finance_service)
):
    try:
        overview = await run_in_threadpool(yfs.get_stock_overview, symbol)
        if not overview:
            raise HTTPException(status_code=404, detail=f"'{symbol}' 종목을 찾을 수 없습니다.")
        return overview
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"주식 개요 API 오류: symbol={symbol}, error={e}")
        raise HTTPException(status_code=500, detail="주식 정보 조회 중 오류가 발생했습니다.")

@app.get("/api/stock/{symbol}/financials", response_model=FinancialStatementResponse, tags=["Stock Info"])
async def get_financial_statements(
    symbol: str,
    yfs: YahooFinanceService = Depends(get_yahoo_finance_service)
):
    try:
        financials = await run_in_threadpool(yfs.get_financial_statements, symbol)
        if not financials or not financials.get("data"):
            raise HTTPException(status_code=404, detail=f"'{symbol}'의 재무제표를 찾을 수 없습니다.")
        return financials
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"재무제표 API 오류: symbol={symbol}, error={e}")
        raise HTTPException(status_code=500, detail="재무제표 조회 중 오류가 발생했습니다.")

@app.get("/api/stock/{symbol}/history", response_model=PriceHistoryResponse, tags=["Stock Info"])
async def get_price_history(
    symbol: str,
    start_date: str,
    end_date: str,
    yfs: YahooFinanceService = Depends(get_yahoo_finance_service)
):
    try:
        history = await run_in_threadpool(yfs.get_price_history, symbol, start_date, end_date)
        if not history or not history.get("data"):
            raise HTTPException(status_code=404, detail=f"'{symbol}'의 주가 데이터를 찾을 수 없습니다.")
        return history
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"주가 이력 API 오류: symbol={symbol}, error={e}")
        raise HTTPException(status_code=500, detail="주가 이력 조회 중 오류가 발생했습니다.")

@app.get("/api/stock/{symbol}/news", response_model=NewsResponse, tags=["Stock Info"])
async def get_stock_news(
    symbol: str,
    ns: NewsService = Depends(get_news_service)
):
    try:
        news = await run_in_threadpool(ns.get_stock_news, symbol)
        return {"news": news}
    except Exception as e:
        logger.error(f"뉴스 API 오류: symbol={symbol}, error={e}")
        raise HTTPException(status_code=500, detail="뉴스 조회 중 오류가 발생했습니다.")

@app.post("/api/ai/chat", response_model=AIChatResponse, tags=["AI Chat"])
async def ai_chat(
    request: AIChatRequest,
    llm: LLMService = Depends(get_llm_service)
):
    try:
        response = await llm.get_ai_response(
            request.symbol,
            request.question,
            request.financial_data,
            request.history_data,
            request.news_data
        )
        return {"response": response}
    except Exception as e:
        logger.error(f"AI 채팅 API 오류: {e}")
        raise HTTPException(status_code=500, detail="AI 응답 생성 중 오류가 발생했습니다.")

# === 섹터 분석 API ===
@app.get("/api/sectors/groups", tags=["Sector Analysis"])
async def get_sector_groups():
    # 섹터 그룹 정보는 정적 데이터로 제공
    return {
        "KOSPI": ["건설", "금융", "기계", "서비스", "유통", "음식료", "전기가스", "철강", "화학"],
        "KOSDAQ": ["IT", "바이오", "게임", "엔터테인먼트", "신재생에너지"]
    }

@app.get("/api/sectors/tickers", tags=["Sector Analysis"])
async def get_sector_tickers(market: str, group: str):
    # 실제 구현 시 KRX에서 섹터별 종목 조회
    # 현재는 샘플 데이터 반환
    return {
        "tickers": [
            {"ticker": "005930", "name": "삼성전자"},
            {"ticker": "000660", "name": "SK하이닉스"},
            {"ticker": "035420", "name": "NAVER"}
        ]
    }

@app.post("/api/sectors/analysis", response_model=SectorAnalysisResponse, tags=["Sector Analysis"])
async def analyze_sectors(request: SectorAnalysisRequest):
    try:
        # 실제 구현은 별도로 진행
        # 현재는 기본 응답만 반환
        return {"data": []}
    except Exception as e:
        logger.error(f"섹터 분석 API 오류: request={request.model_dump()}, error={e}")
        raise HTTPException(status_code=500, detail="서버 내부에서 섹터 분석 중 오류가 발생했습니다.")

# === 주가 비교 분석 API ===
@app.post("/api/stock/compare", response_model=StockComparisonResponse, tags=["Stock Analysis"])
async def compare_stocks(
    request: StockComparisonRequest,
    yfs: YahooFinanceService = Depends(get_yahoo_finance_service)
):
    try:
        df_normalized = await run_in_threadpool(
            yfs.get_comparison_data,
            request.tickers,
            request.start_date,
            request.end_date
        )

        if df_normalized is None or df_normalized.empty:
            raise HTTPException(status_code=404, detail="분석할 유효한 주가 데이터를 찾을 수 없습니다.")

        # 결과를 JSON 직렬화 가능한 형태로 포맷팅
        df_normalized.index = df_normalized.index.strftime('%Y-%m-%d')
        df_normalized = df_normalized.where(pd.notnull(df_normalized), None)
        
        # recharts에 맞는 데이터 형태로 변환
        result_list = df_normalized.reset_index().to_dict(orient='records')
        formatted_data = [{'date': item['Date'], **{k: v for k, v in item.items() if k != 'Date'}} for item in result_list]

        # 차트의 각 라인 정보 생성
        valid_tickers = df_normalized.columns.tolist()
        series = [{"dataKey": ticker, "name": ticker} for ticker in valid_tickers]

        return {"data": formatted_data, "series": series}

    except Exception as e:
        logger.error(f"주가 비교 분석 API 오류: request={request.model_dump()}, error={e}")
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail="서버 내부에서 분석 중 오류가 발생했습니다.")
        raise e

# === 투자자별 매매동향 API ===
@app.post("/api/krx/trading-volume", response_model=TradingVolumeResponse, tags=["Krx Analysis"])
async def get_trading_volume(
    request: TradingVolumeRequest,
    krx: PyKRXService = Depends(get_krx_service)
):
    try:
        df = await run_in_threadpool(
            krx.get_trading_performance_by_investor,
            request.start_date,
            request.end_date,
            request.ticker,
            request.detail,
            request.institution_only
        )
        if df.empty:
            raise HTTPException(status_code=404, detail="해당 조건의 데이터를 찾을 수 없습니다.")

        response_data = {
            "index_name": df.columns[0],
            "data": df.to_dict(orient='records')
        }
        return response_data
    except Exception as e:
        logger.error(f"투자자별 매매현황 조회 API 오류: request={request.model_dump()}, error={e}")
        raise HTTPException(status_code=500, detail="서버 내부에서 조회 중 오류가 발생했습니다.")

@app.post("/api/krx/net-purchases", response_model=NetPurchaseResponse, tags=["Krx Analysis"])
async def get_top_net_purchases(
    request: NetPurchaseRequest,
    krx: PyKRXService = Depends(get_krx_service)
):
    """선택된 투자자의 순매수 상위 종목을 조회합니다."""
    try:
        df = await run_in_threadpool(
            krx.get_net_purchase_ranking_by_investor,
            request.start_date,
            request.end_date,
            request.market,
            request.investor
        )
        if df.empty:
            raise HTTPException(status_code=404, detail="해당 조건의 데이터를 찾을 수 없습니다.")

        return {"data": df.to_dict(orient='records')}
    except Exception as e:
        logger.error(f"투자자별 순매수 상위종목 조회 API 오류: request={request.model_dump()}, error={e}")
        raise HTTPException(status_code=500, detail="서버 내부에서 조회 중 오류가 발생했습니다.")

# === 변동성 분석 API ===
@app.post("/api/stocks/fluctuation-analysis", response_model=FluctuationAnalysisResponse, tags=["Stock Analysis"])
async def analyze_fluctuation(
    request: FluctuationAnalysisRequest,
    fs: FluctuationService = Depends(get_fluctuation_service)
):
    try:
        found_stocks = await run_in_threadpool(
            fs.find_fluctuation_stocks,
            country=request.country, market=request.market,
            start_date=request.start_date, end_date=request.end_date,
            decline_period=request.decline_period, decline_rate=request.decline_rate,
            rebound_period=request.rebound_period, rebound_rate=request.rebound_rate,
        )
        return {"found_stocks": found_stocks}
    except Exception as e:
        logger.error(f"변동성 분석 API 오류: request={request.model_dump()}, error={e}")
        raise HTTPException(status_code=500, detail="서버 내부에서 변동성 분석 중 오류가 발생했습니다.")

# === 뉴스 스캘핑 API ===
@app.post("/api/strategy/news-feed-search", response_model=NewsSearchResponse, tags=["Strategy API"])
async def search_news_feed_candidates(req: NewsSearchRequest):
    """뉴스 필터링 후 DART 공시를 검증하고, 각 단계별 결과를 모두 반환합니다."""
    news_scalping_service = get_news_scalping_service()
    result = await news_scalping_service.get_news_candidates(
        time_limit_seconds=req.time_limit_seconds,
        display_count=req.display_count
    )
    return result

# === 한국투자증권 API 연동 ===
from app.api.search import router as search_router
app.include_router(search_router, prefix="/api", tags=["KIS Search"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)