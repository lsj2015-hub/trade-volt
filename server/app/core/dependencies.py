from fastapi import HTTPException, Depends
from cachetools import TTLCache
import httpx
import logging
from typing import Dict, Any
from dataclasses import dataclass

from app.config import Settings, settings
from app.services.yahoo_finance import YahooFinanceService
from app.services.krx_service import PyKRXService
from app.services.news import NewsService
from app.services.translation import TranslationService
from app.services.llm import LLMService
from app.services.performance_service import PerformanceService
from app.services.fluctuation_service import FluctuationService
from app.services.news_scalping_service import NewsScalpingService
from app.services.korea_investment_service import KoreaInvestmentService

logger = logging.getLogger(__name__)

# 전역 캐시
exchange_rate_cache = TTLCache(maxsize=1, ttl=settings.CACHE_TTL_SECONDS)

@dataclass
class Services:
    """모든 서비스 인스턴스를 담는 컨테이너"""
    yahoo_finance: YahooFinanceService
    krx: PyKRXService
    news: NewsService
    translation: TranslationService
    llm: LLMService
    performance: PerformanceService
    fluctuation: FluctuationService
    news_scalping_service: NewsScalpingService
    korea_investment: KoreaInvestmentService

# 전역 서비스 인스턴스 (싱글톤)
_services: Services = None

def get_services() -> Services:
    """서비스 인스턴스를 반환합니다 (싱글톤 패턴)"""
    global _services
    if _services is None:
        logger.info("🔧 서비스 인스턴스 초기화...")
        _services = Services(
            yahoo_finance=YahooFinanceService(),
            krx=PyKRXService(),
            news=NewsService(),
            translation=TranslationService(),
            llm=LLMService(settings),
            performance=PerformanceService(),
            fluctuation=FluctuationService(),
            news_scalping_service=NewsScalpingService(),
            korea_investment=KoreaInvestmentService()
        )
        logger.info("✅ 모든 서비스 인스턴스 초기화 완료")
    return _services

# FastAPI 의존성 함수들
def get_yahoo_finance_service() -> YahooFinanceService:
    return get_services().yahoo_finance

def get_krx_service() -> PyKRXService:
    return get_services().krx

def get_news_service() -> NewsService:
    return get_services().news

def get_translation_service() -> TranslationService:
    return get_services().translation

def get_llm_service() -> LLMService:
    return get_services().llm

def get_performance_service() -> PerformanceService:
    return get_services().performance

def get_fluctuation_service() -> FluctuationService:
    return get_services().fluctuation

def get_news_scalping_service() -> NewsScalpingService:
    return get_services().news_scalping_service

def get_korea_investment_service() -> KoreaInvestmentService:
    return get_services().korea_investment

async def get_exchange_rate() -> float:
    """USD to KRW 환율을 가져옵니다 (캐시 활용)"""
    if "usd_to_krw" in exchange_rate_cache:
        return exchange_rate_cache["usd_to_krw"]
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.exchangerate-api.com/v4/latest/USD",
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            rate = data["rates"]["KRW"]
            exchange_rate_cache["usd_to_krw"] = rate
            logger.debug(f"환율 업데이트: 1 USD = {rate} KRW")
            return rate
    except Exception as e:
        logger.warning(f"환율 조회 실패, 기본값 사용: {e}")
        default_rate = 1300.0
        exchange_rate_cache["usd_to_krw"] = default_rate
        return default_rate

async def get_yfinance_info(symbol: str) -> Dict[str, Any]:
    """Yahoo Finance에서 주식 정보를 가져옵니다"""
    yfs = get_yahoo_finance_service()
    
    try:
        from starlette.concurrency import run_in_threadpool
        info = await run_in_threadpool(yfs.get_stock_info, symbol.upper())
        
        if not info:
            raise HTTPException(
                status_code=404, 
                detail=f"'{symbol.upper()}'에 대한 기업 정보를 찾을 수 없습니다."
            )
        return info
    except Exception as e:
        logger.error(f"주식 정보 조회 실패: {symbol} - {e}")
        raise HTTPException(
            status_code=500,
            detail=f"주식 정보 조회 중 오류가 발생했습니다: {str(e)}"
        )