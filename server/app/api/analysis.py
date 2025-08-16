# ===========================================
# app/api/analysis.py - 분석 기능 관련
# ===========================================
import asyncio
from datetime import datetime
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
    get_performance_service, get_fluctuation_service, get_news_scalping_service,
    get_yahoo_finance_service
)

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/performance/analysis", response_model=PerformanceAnalysisResponse)
async def analyze_performance(
    request: PerformanceAnalysisRequest,
    performance_service = Depends(get_performance_service)
):
    """시장 성과 분석 - 캐싱 및 최적화 적용"""
    
    # ✅ 입력 검증 및 제한
    if request.top_n > 50:
        raise HTTPException(
            status_code=400, 
            detail="분석 개수는 최대 50개까지 지원됩니다."
        )
    
    # ✅ 기간 제한 검증
    try:
        start_dt = datetime.strptime(request.start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(request.end_date, '%Y-%m-%d')
        
        if (end_dt - start_dt).days > 365:
            raise HTTPException(
                status_code=400, 
                detail="분석 기간은 최대 1년까지 지원됩니다."
            )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식을 사용해주세요."
        )
    
    try:
        logger.info(f"성과 분석 요청: {request.market}, {request.start_date}~{request.end_date}, Top {request.top_n}")
        
        # ✅ 수정된 메서드 호출 (올바른 메서드명과 파라미터)
        result = await asyncio.wait_for(
            run_in_threadpool(
                performance_service.get_market_performance,  # 올바른 메서드명
                request.market,                              # country 제거
                request.start_date,
                request.end_date,
                min(request.top_n, 50)  # 강제 제한
            ),
            timeout=60.0  # 60초 제한
        )
        
        if not result or (not result.get("top_performers") and not result.get("bottom_performers")):
            raise HTTPException(
                status_code=404, 
                detail="해당 조건의 분석 데이터를 생성할 수 없습니다."
            )
        
        logger.info(f"성과 분석 완료: 상위 {len(result.get('top_performers', []))}개, 하위 {len(result.get('bottom_performers', []))}개")
        return result
        
    except asyncio.TimeoutError:
        logger.error(f"성과 분석 타임아웃: {request.market}")
        raise HTTPException(
            status_code=408, 
            detail="요청 처리 시간이 초과되었습니다. 더 작은 기간이나 개수로 다시 시도해주세요."
        )
    except Exception as e:
        logger.error(f"성과 분석 오류: {e}")
        if not isinstance(e, HTTPException):
            raise HTTPException(
                status_code=500, 
                detail="성과 분석 중 오류가 발생했습니다."
            )
        raise

@router.post("/performance/analysis/fast", response_model=PerformanceAnalysisResponse)
async def analyze_performance_fast(
    request: PerformanceAnalysisRequest,
    performance_service = Depends(get_performance_service)
):
    """빠른 성과 분석 (제한된 데이터셋)"""
    # 빠른 분석용 제한
    if request.top_n > 20:
        request.top_n = 20
        
    try:
        result = await asyncio.wait_for(
            run_in_threadpool(
                performance_service.get_market_performance_fast,
                request.market,
                request.start_date,
                request.end_date,
                request.top_n
            ),
            timeout=30.0  # 30초 제한
        )
        
        return result
    except Exception as e:
        logger.error(f"빠른 성과 분석 오류: {e}")
        raise HTTPException(status_code=500, detail="빠른 분석 중 오류가 발생했습니다.")

@router.post("/stock/compare", response_model=StockComparisonResponse)
async def compare_stocks(
    request: StockComparisonRequest,
    yfs = Depends(get_yahoo_finance_service)  # ✅ Yahoo Finance 서비스 사용
):
    """여러 주식의 수익률을 비교 분석합니다."""
    try:
        # ✅ 백업 버전의 올바른 로직 사용
        df_normalized = await run_in_threadpool(
            yfs.get_comparison_data,
            request.tickers,
            request.start_date,
            request.end_date
        )

        if df_normalized is None or df_normalized.empty:
            raise HTTPException(status_code=404, detail="분석할 유효한 주가 데이터를 찾을 수 없습니다.")

        # JSON 직렬화 가능한 형태로 포맷팅
        import pandas as pd
        df_normalized.index = df_normalized.index.strftime('%Y-%m-%d')
        df_normalized = df_normalized.where(pd.notnull(df_normalized), None)
        
        # recharts에 맞는 데이터 형태로 변환
        result_list = df_normalized.reset_index().to_dict(orient='records')
        formatted_data = [{'date': item['Date'], **{k: v for k, v in item.items() if k != 'Date'}} for item in result_list]

        # 차트의 각 라인(series) 정보 생성
        valid_tickers = df_normalized.columns.tolist()
        series = [{"dataKey": ticker, "name": ticker} for ticker in valid_tickers]

        return {"data": formatted_data, "series": series}
        
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
        # ✅ 백업 버전 기준 올바른 메서드 호출
        found_stocks = await run_in_threadpool(
            fluctuation_service.find_fluctuation_stocks,  # 올바른 메서드명
            country=request.country, 
            market=request.market,
            start_date=request.start_date, 
            end_date=request.end_date,
            decline_period=request.decline_period, 
            decline_rate=request.decline_rate,
            rebound_period=request.rebound_period, 
            rebound_rate=request.rebound_rate,
        )
        return {"found_stocks": found_stocks}
    except Exception as e:
        logger.error(f"변동성 분석 오류: {e}")
        if not isinstance(e, HTTPException):
            raise HTTPException(status_code=500, detail="변동성 분석 중 오류가 발생했습니다.")
        raise

@router.post("/strategy/news-feed-search", response_model=NewsSearchResponse)
async def search_news_feed_candidates(
    req: NewsSearchRequest,
    news_scalping_service = Depends(get_news_scalping_service)
):
    """뉴스 필터링 후 DART 공시를 검증하고, 각 단계별 결과를 모두 반환합니다."""
    try:
        result = await news_scalping_service.get_news_candidates(
            time_limit_seconds=req.time_limit_seconds,
            display_count=req.display_count
        )
        return result
    except Exception as e:
        logger.error(f"뉴스 검색 오류: {e}")
        raise HTTPException(status_code=500, detail="뉴스 검색 중 오류가 발생했습니다.")

# ✅ 캐시 관리 API 추가
@router.post("/performance/cache/clear")
async def clear_performance_cache(
    market: str = None,
    performance_service = Depends(get_performance_service)
):
    """성과 분석 캐시를 클리어합니다."""
    try:
        success = performance_service.clear_cache(market)
        return {
            "success": success,
            "message": f"캐시 클리어 완료: {market or '전체'}"
        }
    except Exception as e:
        logger.error(f"캐시 클리어 오류: {e}")
        raise HTTPException(status_code=500, detail="캐시 클리어 중 오류가 발생했습니다.")

@router.get("/performance/cache/stats")
async def get_cache_stats(
    performance_service = Depends(get_performance_service)
):
    """캐시 통계 정보를 조회합니다."""
    try:
        stats = performance_service.get_cache_stats()
        return stats
    except Exception as e:
        logger.error(f"캐시 통계 조회 오류: {e}")
        raise HTTPException(status_code=500, detail="캐시 통계 조회 중 오류가 발생했습니다.")