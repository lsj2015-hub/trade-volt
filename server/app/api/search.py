# ===========================================
# app/api/search.py - 종목 검색 관련
# ===========================================
from fastapi import APIRouter, Query, Depends, HTTPException
from typing import List, Optional
import logging

from app.schemas import StockItem
from app.core.dependencies import get_korea_investment_service
from app.services.korea_investment_service import KoreaInvestmentService

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/search-stocks", response_model=List[StockItem])
async def search_stocks(
    query: str, 
    market: str = Query("KOR", description="시장 구분 (KOR, USA, KOSPI, KOSDAQ, NASDAQ, NYSE, AMEX)"),
    limit: int = Query(20, description="최대 반환 개수"),
    kis: KoreaInvestmentService = Depends(get_korea_investment_service)
):
    """주식 종목을 검색합니다."""
    if not query.strip():
        return []

    try:
        return kis.search_stocks_by_market(query, market, limit)
    except Exception as e:
        logger.error(f"종목 검색 오류: {e}")
        raise HTTPException(status_code=500, detail="종목 검색 중 오류가 발생했습니다.")

@router.get("/stocks/korean", response_model=List[StockItem])
async def search_korean_stocks(
    query: str,
    limit: int = Query(20, description="최대 반환 개수"),
    kis: KoreaInvestmentService = Depends(get_korea_investment_service)
):
    """한국 주식만 검색합니다."""
    if not query.strip():
        return []
    return kis.search_korean_stocks(query, limit)

@router.get("/stocks/overseas", response_model=List[StockItem])
async def search_overseas_stocks(
    query: str,
    markets: Optional[str] = Query(None, description="검색할 시장 (콤마로 구분: NASDAQ,NYSE,AMEX)"),
    limit: int = Query(20, description="최대 반환 개수"),
    kis: KoreaInvestmentService = Depends(get_korea_investment_service)
):
    """해외 주식만 검색합니다."""
    if not query.strip():
        return []
    
    market_list = None
    if markets:
        market_list = [m.strip().upper() for m in markets.split(",")]
    
    return kis.search_overseas_stocks(query, market_list, limit)

@router.get("/stocks/info/{code}")
async def get_stock_info(
    code: str,
    kis: KoreaInvestmentService = Depends(get_korea_investment_service)
):
    """종목코드로 주식 정보를 조회합니다."""
    stock_info = kis.get_stock_info_by_code(code)
    if not stock_info:
        raise HTTPException(status_code=404, detail=f"종목코드 '{code}'를 찾을 수 없습니다.")
    return stock_info

@router.get("/stocks/market/{market}", response_model=List[StockItem])
async def get_market_stocks(
    market: str,
    limit: int = Query(100, description="최대 반환 개수"),
    kis: KoreaInvestmentService = Depends(get_korea_investment_service)
):
    """특정 시장의 모든 종목을 조회합니다."""
    try:
        stocks = kis.get_market_stocks(market.upper())
        return stocks[:limit]
    except Exception as e:
        logger.error(f"시장 종목 조회 오류: {e}")
        raise HTTPException(status_code=500, detail=f"'{market}' 시장 종목 조회 중 오류가 발생했습니다.")

@router.get("/stocks/stats")
async def get_stock_data_stats(
    kis: KoreaInvestmentService = Depends(get_korea_investment_service)
):
    """로드된 종목 데이터의 통계를 반환합니다."""
    return kis.get_stock_data_stats()

@router.post("/stocks/reload")
async def reload_stock_data(
    kis: KoreaInvestmentService = Depends(get_korea_investment_service)
):
    """종목 데이터를 다시 로드합니다."""
    try:
        success = kis.reload_stock_data()
        if success:
            return {"message": "종목 데이터 재로드 완료", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="종목 데이터 재로드 실패")
    except Exception as e:
        logger.error(f"종목 데이터 재로드 오류: {e}")
        raise HTTPException(status_code=500, detail="종목 데이터 재로드 중 오류가 발생했습니다.")