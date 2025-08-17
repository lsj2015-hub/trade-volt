# ===========================================
# app/core/dependencies.py - 의존성 주입 관리
# ===========================================
"""
FastAPI 의존성 주입을 위한 모듈
모든 서비스 인스턴스를 싱글톤으로 관리합니다.
"""

import logging
from functools import lru_cache
from typing import Dict, Any

from app.config import settings
from app.services.yahoo_finance import YahooFinanceService
from app.services.krx_service import PyKRXService
from app.services.news import NewsService
from app.services.translation import TranslationService
from app.services.llm import LLMService
from app.services.fluctuation_service import FluctuationService
from app.services.news_scalping_service import NewsScalpingService
from app.services.korea_investment_service import KoreaInvestmentService

logger = logging.getLogger(__name__)

# 서비스 인스턴스 캐시
_service_cache = {}

@lru_cache()
def get_yahoo_finance_service() -> YahooFinanceService:
    """Yahoo Finance 서비스 인스턴스를 반환합니다."""
    if 'yahoo_finance' not in _service_cache:
        logger.info("🔄 Yahoo Finance 서비스 생성")
        _service_cache['yahoo_finance'] = YahooFinanceService()
    return _service_cache['yahoo_finance']

@lru_cache()
def get_krx_service() -> PyKRXService:
    """KRX 서비스 인스턴스를 반환합니다."""
    if 'krx' not in _service_cache:
        logger.info("🔄 KRX 서비스 생성")
        _service_cache['krx'] = PyKRXService()
    return _service_cache['krx']

@lru_cache()
def get_news_service() -> NewsService:
    """뉴스 서비스 인스턴스를 반환합니다."""
    if 'news' not in _service_cache:
        logger.info("🔄 뉴스 서비스 생성")
        _service_cache['news'] = NewsService()
    return _service_cache['news']

@lru_cache()
def get_translation_service() -> TranslationService:
    """번역 서비스 인스턴스를 반환합니다."""
    if 'translation' not in _service_cache:
        logger.info("🔄 번역 서비스 생성")
        _service_cache['translation'] = TranslationService()
    return _service_cache['translation']

@lru_cache()
def get_llm_service() -> LLMService:
    """LLM 서비스 인스턴스를 반환합니다."""
    if 'llm' not in _service_cache:
        logger.info("🔄 LLM 서비스 생성")
        _service_cache['llm'] = LLMService()
    return _service_cache['llm']

@lru_cache()
def get_fluctuation_service() -> FluctuationService:
    """등락률 분석 서비스 인스턴스를 반환합니다."""
    if 'fluctuation' not in _service_cache:
        logger.info("🔄 등락률 분석 서비스 생성")
        _service_cache['fluctuation'] = FluctuationService()
    return _service_cache['fluctuation']

@lru_cache()
def get_news_scalping_service() -> NewsScalpingService:
    """뉴스 스크래핑 서비스 인스턴스를 반환합니다."""
    if 'news_scalping' not in _service_cache:
        logger.info("🔄 뉴스 스크래핑 서비스 생성")
        _service_cache['news_scalping'] = NewsScalpingService()
    return _service_cache['news_scalping']

@lru_cache()
def get_korea_investment_service() -> KoreaInvestmentService:
    """한국투자증권 API 서비스 인스턴스를 반환합니다."""
    if 'korea_investment' not in _service_cache:
        logger.info("🔄 한국투자증권 API 서비스 생성")
        _service_cache['korea_investment'] = KoreaInvestmentService()
    return _service_cache['korea_investment']

def get_services() -> Dict[str, Any]:
    """모든 서비스의 상태를 반환합니다."""
    try:
        services = {
            'yahoo_finance': get_yahoo_finance_service(),
            'krx': get_krx_service(),
            'news': get_news_service(),
            'translation': get_translation_service(),
            'llm': get_llm_service(),
            'fluctuation': get_fluctuation_service(),
            'news_scalping': get_news_scalping_service(),
            'korea_investment': get_korea_investment_service()
        }
        
        logger.info("✅ 모든 서비스 인스턴스 생성 완료")
        return services
        
    except Exception as e:
        logger.error(f"❌ 서비스 초기화 중 오류 발생: {e}")
        raise

def clear_service_cache():
    """서비스 캐시를 초기화합니다."""
    global _service_cache
    _service_cache.clear()
    
    # lru_cache도 초기화
    get_yahoo_finance_service.cache_clear()
    get_krx_service.cache_clear()
    get_news_service.cache_clear()
    get_translation_service.cache_clear()
    get_llm_service.cache_clear()
    get_fluctuation_service.cache_clear()
    get_news_scalping_service.cache_clear()
    get_korea_investment_service.cache_clear()
    
    logger.info("🔄 서비스 캐시 초기화 완료")

def get_service_status() -> Dict[str, str]:
    """각 서비스의 상태를 확인하여 반환합니다."""
    status = {}
    
    try:
        # Yahoo Finance 서비스 상태
        yf = get_yahoo_finance_service()
        status['yahoo_finance'] = 'healthy'
    except Exception as e:
        status['yahoo_finance'] = f'error: {str(e)}'
    
    try:
        # KRX 서비스 상태
        krx = get_krx_service()
        status['krx'] = 'healthy'
    except Exception as e:
        status['krx'] = f'error: {str(e)}'
    
    try:
        # 뉴스 서비스 상태
        news = get_news_service()
        status['news'] = 'healthy'
    except Exception as e:
        status['news'] = f'error: {str(e)}'
    
    try:
        # 번역 서비스 상태
        translation = get_translation_service()
        status['translation'] = 'healthy'
    except Exception as e:
        status['translation'] = f'error: {str(e)}'
    
    try:
        # LLM 서비스 상태
        llm = get_llm_service()
        status['llm'] = 'healthy'
    except Exception as e:
        status['llm'] = f'error: {str(e)}'
    
    try:
        # 등락률 분석 서비스 상태
        fluctuation = get_fluctuation_service()
        status['fluctuation'] = 'healthy'
    except Exception as e:
        status['fluctuation'] = f'error: {str(e)}'
    
    try:
        # 뉴스 스크래핑 서비스 상태
        news_scalping = get_news_scalping_service()
        status['news_scalping'] = 'healthy'
    except Exception as e:
        status['news_scalping'] = f'error: {str(e)}'
    
    try:
        # 한국투자증권 API 서비스 상태
        kis = get_korea_investment_service()
        if kis.test_connection():
            status['korea_investment'] = 'connected'
        else:
            status['korea_investment'] = 'disconnected'
    except Exception as e:
        status['korea_investment'] = f'error: {str(e)}'
    
    return status