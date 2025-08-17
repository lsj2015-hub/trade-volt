# ===========================================
# server/app/core/dependencies.py
# ===========================================
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

def get_fluctuation_service() -> FluctuationService:
    return get_services().fluctuation

def get_news_scalping_service() -> NewsScalpingService:
    return get_services().news_scalping_service

def get_korea_investment_service() -> KoreaInvestmentService:
    """한국투자증권 서비스 인스턴스를 반환합니다."""
    return get_services().korea_investment

async def get_exchange_rate() -> float:
    """환율 정보를 조회합니다 (USD/KRW)"""
    cache_key = "exchange_rate"
    
    # 캐시 확인
    if cache_key in exchange_rate_cache:
        cached_rate = exchange_rate_cache[cache_key]
        logger.debug(f"환율 캐시 적중: {cached_rate}")
        return cached_rate
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(settings.EXCHANGE_RATE_API_URL)
            response.raise_for_status()
            data = response.json()
            
            # EUR 기준이므로 USD -> KRW 계산
            krw_rate = data.get("rates", {}).get("KRW", settings.DEFAULT_KRW_RATE)
            usd_rate = data.get("rates", {}).get("USD", 1.0)
            
            # USD/KRW 환율 계산
            usd_krw_rate = krw_rate / usd_rate
            
            # 캐시에 저장
            exchange_rate_cache[cache_key] = usd_krw_rate
            
            logger.info(f"환율 조회 성공: 1 USD = {usd_krw_rate:.2f} KRW")
            return usd_krw_rate
            
    except Exception as e:
        logger.warning(f"환율 조회 실패: {e}, 기본값 사용: {settings.DEFAULT_KRW_RATE}")
        
        # 기본값을 캐시에 저장 (짧은 TTL)
        exchange_rate_cache[cache_key] = settings.DEFAULT_KRW_RATE
        return settings.DEFAULT_KRW_RATE