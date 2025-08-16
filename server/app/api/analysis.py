# ===========================================
# app/api/analysis.py - 분석 기능 관련
# ===========================================
from fastapi import APIRouter, Depends, HTTPException
from starlette.concurrency import run_in_threadpool
import logging

from app.schemas import (
    PerformanceAnalysisRequest, PerformanceAnalysisResponse,
    StockComparisonRequest, StockComparisonResponse,
    FluctuationAnalysisRequest, FluctuationAnalysisResponse,
    NewsSearchRequest, NewsSearchResponse
)
from app.core.dependencies import (
    get_performance_service, get_fluctuation_service, get_news_scalping_service
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/performance/analysis", response_model=PerformanceAnalysisResponse)
async def analyze_performance(
    request: PerformanceAnalysisRequest,
    performance_service = Depends(get_performance_service)
):
    """시장 성과 분석을 요청합니다."""
    try:
        result = await run_in_threadpool(
            performance_service.analyze_performance,
            request.country,
            request.market,
            request.start_date,
            request.end_date,
            request.top_n
        )
        if not result:
            raise HTTPException(status_code=404, detail="분석할 데이터를 찾을 수 없습니다.")
        return result
    except Exception as e:
        logger.error(f"성과 분석 오류: {e}")
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail="성과 분석 중 오류가 발생했습니다.")
        raise

@router.post("/stock/compare", response_model=StockComparisonResponse)
async def compare_stocks(
    request: StockComparisonRequest,
    performance_service = Depends(get_performance_service)
):
    """여러 주식의 수익률을 비교 분석합니다."""
    try:
        result = await run_in_threadpool(
            performance_service.compare_stocks,
            request.tickers,
            request.start_date,
            request.end_date
        )
        if not result:
            raise HTTPException(status_code=404, detail="비교할 데이터를 찾을 수 없습니다.")
        return result
    except Exception as e:
        logger.error(f"주식 비교 분석 오류: {e}")
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail="주식 비교 분석 중 오류가 발생했습니다.")
        raise

@router.post("/fluctuation/analysis", response_model=FluctuationAnalysisResponse)
async def analyze_fluctuation(
    request: FluctuationAnalysisRequest,
    fluctuation_service = Depends(get_fluctuation_service)
):
    """변동성 종목 분석을 요청합니다."""
    try:
        result = await run_in_threadpool(
            fluctuation_service.analyze_fluctuation,
            request.country,
            request.market,
            request.start_date,
            request.end_date,
            request.top_n,
            request.min_volume
        )
        if not result:
            raise HTTPException(status_code=404, detail="분석할 데이터를 찾을 수 없습니다.")
        return result
    except Exception as e:
        logger.error(f"변동성 분석 오류: {e}")
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail="변동성 분석 중 오류가 발생했습니다.")
        raise

@router.post("/news/search", response_model=NewsSearchResponse)
async def search_news(
    request: NewsSearchRequest,
    news_service = Depends(get_news_scalping_service)
):
    """뉴스 검색을 수행합니다."""
    try:
        results = await news_service.search_news(
            query=request.query,
            start_date=request.start_date,
            end_date=request.end_date,
            limit=request.limit
        )
        return {"results": results}
    except Exception as e:
        logger.error(f"뉴스 검색 오류: {e}")
        raise HTTPException(status_code=500, detail="뉴스 검색 중 오류가 발생했습니다.")