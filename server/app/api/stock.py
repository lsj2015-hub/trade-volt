# ===========================================
# app/api/stock.py - 개별 주식 정보 관련
# ===========================================
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette.concurrency import run_in_threadpool
from typing import List
import logging

from app.schemas import (
    StockOverviewResponse, StockProfile, FinancialSummary,
    InvestmentMetrics, MarketData, AnalystRecommendations,
    OfficersResponse, Officer, FinancialStatementResponse,
    PriceHistoryResponse, NewsResponse
)
from app.core.dependencies import (
    get_yfinance_info, get_exchange_rate, get_translation_service,
    get_yahoo_finance_service, get_krx_service, get_news_service
)
from app.core import formatting

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/stock/{symbol}/overview", response_model=StockOverviewResponse)
async def get_stock_overview(
    symbol: str,
    info: dict = Depends(get_yfinance_info),
    ts = Depends(get_translation_service),
    rate: float = Depends(get_exchange_rate)
):
    """한 번의 요청으로 기업 프로필, 재무 요약, 지표 등 모든 주요 정보를 조회합니다."""
    summary_kr = await run_in_threadpool(ts.translate_to_korean, info.get('longBusinessSummary', ''))
    profile_data = formatting.format_stock_profile(info, summary_kr)
    summary_data = formatting.format_financial_summary(info, symbol, rate)
    metrics_data = formatting.format_investment_metrics(info)
    market_data = formatting.format_market_data(info, symbol, rate)
    recommendations_data = formatting.format_analyst_recommendations(info)

    officers_raw = info.get("companyOfficers", [])
    formatted_officers = []
    if officers_raw:
        top_officers = sorted(officers_raw, key=lambda x: x.get('totalPay', 0), reverse=True)[:5]
        formatted_officers = [
            {
                "name": o.get("name", ""),
                "title": o.get("title", ""), 
                "totalPay": formatting.format_currency(o.get("totalPay"), symbol, rate)
            }
            for o in top_officers
        ]

    return {
        "profile": profile_data,
        "summary": summary_data,
        "metrics": metrics_data,
        "marketData": market_data,
        "recommendations": recommendations_data,
        "officers": formatted_officers
    }

@router.get("/stock/{symbol}/profile", response_model=StockProfile)
async def get_stock_profile(
    info: dict = Depends(get_yfinance_info),
    ts = Depends(get_translation_service)
):
    """회사 기본 정보 조회"""
    summary = info.get('longBusinessSummary', '')
    summary_kr = await run_in_threadpool(ts.translate_to_korean, summary)
    return formatting.format_stock_profile(info, summary_kr)

@router.get("/stock/{symbol}/financial-summary", response_model=FinancialSummary)
async def get_financial_summary(
    symbol: str,
    info: dict = Depends(get_yfinance_info),
    rate: float = Depends(get_exchange_rate)
):
    """재무 요약 정보 조회"""
    return formatting.format_financial_summary(info, symbol, rate)

@router.get("/stock/{symbol}/metrics", response_model=InvestmentMetrics)
async def get_investment_metrics(info: dict = Depends(get_yfinance_info)):
    """투자 지표 조회"""
    return formatting.format_investment_metrics(info)

@router.get("/stock/{symbol}/market-data", response_model=MarketData)
async def get_market_data(
    symbol: str,
    info: dict = Depends(get_yfinance_info),
    rate: float = Depends(get_exchange_rate)
):
    """주가/시장 정보 조회"""
    return formatting.format_market_data(info, symbol, rate)

@router.get("/stock/{symbol}/recommendations", response_model=AnalystRecommendations)
async def get_analyst_recommendations(info: dict = Depends(get_yfinance_info)):
    """분석가 의견 조회"""
    return formatting.format_analyst_recommendations(info)

@router.get("/stock/{symbol}/officers", response_model=OfficersResponse)
async def get_stock_officers(
    symbol: str,
    yfs = Depends(get_yahoo_finance_service),
    rate: float = Depends(get_exchange_rate)
):
    """임원 정보 조회"""
    officers_raw = await run_in_threadpool(yfs.get_officers, symbol.upper())
    
    if officers_raw is None:
        return {"officers": []}
    if not officers_raw:
        logger.info(f"'{symbol.upper()}'에 대한 임원 정보가 비어있습니다.")
        return {"officers": []}

    top_officers = sorted(officers_raw, key=lambda x: x.get('totalPay', 0), reverse=True)[:5]
    
    formatted_officers = [
        Officer(
            name=o.get("name", ""),
            title=o.get("title", ""),
            totalPay=formatting.format_currency(o.get("totalPay"), symbol, rate)
        )
        for o in top_officers
    ]
    return {"officers": formatted_officers}

@router.get("/stock/{symbol}/financials/{statement_type}", response_model=FinancialStatementResponse)
async def get_financial_statement(
    symbol: str, 
    statement_type: str,
    yfs = Depends(get_yahoo_finance_service)
):
    """재무제표 조회 (income, balance, cashflow)"""
    if statement_type not in ["income", "balance", "cashflow"]:
        raise HTTPException(status_code=400, detail="statement_type은 'income', 'balance', 'cashflow' 중 하나여야 합니다.")

    fin_data = await run_in_threadpool(yfs.get_financials, symbol.upper())
    if not fin_data:
        raise HTTPException(status_code=404, detail=f"'{symbol.upper()}'에 대한 재무 데이터를 가져오지 못했습니다.")
    
    df_raw = fin_data.get(statement_type)

    if df_raw is None or df_raw.empty:
        raise HTTPException(status_code=404, detail=f"'{symbol.upper()}'에 대한 {statement_type} 데이터를 찾을 수 없습니다.")
        
    return formatting.format_financial_statement_response(df_raw, statement_type, symbol)

@router.get("/stock/{symbol}/history", response_model=PriceHistoryResponse)
async def get_stock_history(
    symbol: str,
    start_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    end_date: str = Query(..., pattern=r"^\d{4}-\d{2}-\d{2}$"),
    yfs = Depends(get_yahoo_finance_service),
    krx = Depends(get_krx_service)
):
    """기간별 주가 히스토리 조회"""
    symbol_upper = symbol.upper()
    df_raw, adjusted_end = None, None
    
    if len(symbol_upper) == 6 and symbol_upper.isdigit():
        df_raw, adjusted_end = await run_in_threadpool(krx.get_price_history_kr, symbol_upper, start_date, end_date)
    else:
        df_raw, adjusted_end = await run_in_threadpool(yfs.get_price_history, symbol_upper, start_date, end_date)
    
    if df_raw is None or df_raw.empty:
        raise HTTPException(status_code=404, detail=f"해당 기간의 주가 데이터를 찾을 수 없습니다.")
    
    display_df = formatting.process_price_dataframe(df_raw)
    return {
        "symbol": symbol_upper,
        "startDate": start_date,
        "endDate": adjusted_end if adjusted_end else end_date,
        "data": display_df.to_dict("records")
    }

@router.get("/stock/{symbol}/news", response_model=NewsResponse)
async def get_yahoo_rss_news(
    symbol: str, 
    limit: int = Query(10, ge=1, le=50),
    ns = Depends(get_news_service)
):
    """Yahoo Finance RSS 뉴스 조회"""
    news_list = await ns.get_yahoo_rss_news(symbol.upper(), limit)
    if not news_list:
        logger.warning(f"'{symbol.upper()}'에 대한 뉴스를 가져오지 못했습니다.")
    return {"news": news_list}