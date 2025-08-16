# ===========================================
# server/app/services/performance_service.py
# Config 설정을 활용한 완전한 캐싱 버전
# ===========================================

import pandas as pd
import yfinance as yf
from pykrx import stock
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import time
import json
import hashlib
from functools import lru_cache

# ✅ Config 설정 import 추가
from app.config import settings, get_redis_url

# Redis 캐싱 (선택사항)
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)

class CacheService:
    """Config 기반 Redis 캐싱 서비스"""
    
    def __init__(self):
        self.enabled = False
        self.redis_client = None
        self.memory_cache = {}
        self.cache_timestamps = {}
        
        # ✅ Config 기반 Redis 초기화
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                    decode_responses=True,
                    socket_timeout=1,
                    socket_connect_timeout=1
                )
                
                # 연결 테스트
                self.redis_client.ping()
                self.enabled = True
                logger.info(f"✅ Redis 캐시 연결 성공: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
                
            except Exception as e:
                logger.warning(f"⚠️ Redis 연결 실패 ({settings.REDIS_HOST}:{settings.REDIS_PORT}), 메모리 캐싱 사용: {e}")
                self.redis_client = None
                self.enabled = False
        else:
            logger.info("⚠️ Redis 미설치, 메모리 캐싱 사용")
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """캐시 키 생성"""
        key_data = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
        return f"{prefix}:{key_hash}"
    
    def get(self, prefix: str, **kwargs) -> Optional[Any]:
        """캐시에서 데이터 조회"""
        key = self._generate_key(prefix, **kwargs)
        
        # Redis 우선 시도
        if self.enabled:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    return json.loads(cached_data)
            except Exception as e:
                logger.warning(f"Redis 조회 실패: {e}")
        
        # 메모리 캐시 확인
        if key in self.memory_cache:
            timestamp = self.cache_timestamps.get(key, 0)
            if time.time() - timestamp < settings.PERFORMANCE_CACHE_TTL:
                return self.memory_cache[key]
            else:
                # 만료된 캐시 삭제
                del self.memory_cache[key]
                del self.cache_timestamps[key]
        
        return None
    
    def set(self, prefix: str, data: Any, ttl: int = None, **kwargs) -> bool:
        """캐시에 데이터 저장"""
        if ttl is None:
            ttl = settings.PERFORMANCE_CACHE_TTL
            
        key = self._generate_key(prefix, **kwargs)
        
        # Redis에 저장 시도
        if self.enabled:
            try:
                self.redis_client.setex(key, ttl, json.dumps(data))
                return True
            except Exception as e:
                logger.warning(f"Redis 저장 실패: {e}")
        
        # 메모리 캐시에 저장
        self.memory_cache[key] = data
        self.cache_timestamps[key] = time.time()
        
        # 메모리 캐시 크기 제한 (최대 100개)
        if len(self.memory_cache) > 100:
            oldest_key = min(self.cache_timestamps.keys(), 
                           key=lambda k: self.cache_timestamps[k])
            del self.memory_cache[oldest_key]
            del self.cache_timestamps[oldest_key]
        
        return True

    def clear(self, pattern: str = None) -> bool:
        """캐시 클리어"""
        try:
            if self.enabled and self.redis_client:
                if pattern:
                    keys = self.redis_client.keys(pattern)
                    if keys:
                        self.redis_client.delete(*keys)
                        logger.info(f"Redis 패턴 캐시 클리어: {pattern} ({len(keys)}개 키)")
                else:
                    keys = self.redis_client.keys("market_performance:*")
                    if keys:
                        self.redis_client.delete(*keys)
                        logger.info(f"Redis 전체 캐시 클리어: {len(keys)}개 키")
            
            # 메모리 캐시도 클리어
            if pattern:
                # 패턴 매칭으로 선택적 삭제
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
                for k in keys_to_delete:
                    del self.memory_cache[k]
                    del self.cache_timestamps[k]
            else:
                self.memory_cache.clear()
                self.cache_timestamps.clear()
            
            return True
        except Exception as e:
            logger.error(f"캐시 클리어 실패: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        stats = {
            "redis_enabled": self.enabled,
            "redis_host": f"{settings.REDIS_HOST}:{settings.REDIS_PORT}",
            "memory_cache_size": len(self.memory_cache),
            "redis_keys": 0,
            "cache_ttl": settings.PERFORMANCE_CACHE_TTL
        }
        
        try:
            if self.enabled and self.redis_client:
                keys = self.redis_client.keys("market_performance:*")
                stats["redis_keys"] = len(keys)
        except Exception as e:
            logger.warning(f"Redis 통계 조회 실패: {e}")
        
        return stats

# 전역 캐시 인스턴스
cache_service = CacheService()

class PerformanceService:
    """Config 기반 성과 분석 서비스"""
    
    def __init__(self):
        # ✅ Config에서 설정값 로드
        self.max_workers = 4
        self.chunk_size = settings.PERFORMANCE_CHUNK_SIZE
        self.timeout = settings.PERFORMANCE_TIMEOUT
        self.max_tickers = settings.PERFORMANCE_MAX_TICKERS
        self.max_chunks = settings.PERFORMANCE_MAX_CHUNKS
        self.cache_ttl = settings.PERFORMANCE_CACHE_TTL
        
        logger.info(f"🔧 PerformanceService 초기화: "
                   f"chunk_size={self.chunk_size}, timeout={self.timeout}s, "
                   f"max_tickers={self.max_tickers}, cache_ttl={self.cache_ttl}s")
        
    @lru_cache(maxsize=100)
    def _get_tickers_by_market_cached(self, market: str) -> pd.DataFrame:
        """캐싱된 티커 목록 조회"""
        return self._get_tickers_by_market(market)
    
    def _get_tickers_by_market(self, market: str) -> pd.DataFrame:
        """시장의 티커와 이름 목록을 가져옵니다."""
        try:
            if market in ["KOSPI", "KOSDAQ"]:
                today_str = datetime.now().strftime('%Y%m%d')
                tickers = stock.get_market_ticker_list(market=market, date=today_str)
                valid_tickers = [t for t in tickers if len(t) == 6 and t.isdigit()]
                names = [stock.get_market_ticker_name(t) for t in valid_tickers]
                df = pd.DataFrame({'ticker': valid_tickers, 'name': names})
            elif market in ['NASDAQ', 'NYSE', 'S&P500']:
                try:
                    import FinanceDataReader as fdr
                    df = fdr.StockListing(market)
                    df = df[['Symbol', 'Name']].rename(columns={'Symbol': 'ticker', 'Name': 'name'})
                except ImportError:
                    logger.error("FinanceDataReader가 설치되지 않았습니다.")
                    df = pd.DataFrame()
            else:
                df = pd.DataFrame()
            return df
        except Exception as e:
            logger.error(f"'{market}' 티커 목록 조회 실패: {e}")
            return pd.DataFrame()

    def _get_performance_kr(self, tickers: List[str], name_map: Dict[str, str], 
                           start_date: str, end_date: str) -> pd.DataFrame:
        """한국 주식의 수익률을 계산합니다."""
        performance_data = []
        
        # Config 기반 종목 수 제한
        limited_tickers = tickers[:min(500, self.max_tickers // 2)]
        
        logger.info(f"한국 주식 분석 시작: {len(limited_tickers)}개 종목")
        
        for i, ticker in enumerate(limited_tickers):
            try:
                # 진행률 로깅
                if i % (len(limited_tickers) // 10 + 1) == 0:
                    progress = (i / len(limited_tickers)) * 100
                    logger.info(f"한국 주식 진행률: {progress:.1f}% ({i}/{len(limited_tickers)})")
                
                df = stock.get_market_ohlcv(
                    start_date.replace('-', ''), 
                    end_date.replace('-', ''), 
                    ticker
                )
                
                if not df.empty and len(df) > 1:
                    start_price = df['종가'].iloc[0]
                    end_price = df['종가'].iloc[-1]
                    
                    if start_price > 0:
                        performance = ((end_price - start_price) / start_price) * 100
                        
                        # 이상치 필터링
                        if -90 <= performance <= 900:
                            performance_data.append({
                                "ticker": ticker,
                                "name": name_map.get(ticker, ticker),
                                "performance": performance
                            })
                
                # API 호출 간격 조절
                if i % 10 == 0:
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.warning(f"한국 주식 {ticker} 처리 실패: {e}")
                continue
        
        logger.info(f"한국 주식 분석 완료: {len(performance_data)}개 데이터 수집")
        return pd.DataFrame(performance_data)

    def _get_performance_us_optimized(self, tickers: List[str], name_map: Dict[str, str], 
                                    start_date: str, end_date: str) -> pd.DataFrame:
        """Config 기반 최적화된 미국 주식 성능 분석"""
        all_performance_data = []
        
        # Config 기반 티커 수 제한
        limited_tickers = tickers[:self.max_tickers]
        
        logger.info(f"미국 주식 분석 시작: {len(limited_tickers)}개 종목 (원본: {len(tickers)}개)")
        
        processed_chunks = 0
        
        for i in range(0, len(limited_tickers), self.chunk_size):
            if processed_chunks >= self.max_chunks:
                logger.warning(f"청크 제한 도달 ({self.max_chunks}개), 분석 중단")
                break
                
            chunk = limited_tickers[i:i + self.chunk_size]
            
            try:
                # Config 기반 재시도 로직
                data = None
                for attempt in range(2):
                    try:
                        data = yf.download(
                            chunk, 
                            start=start_date, 
                            end=end_date, 
                            progress=False, 
                            auto_adjust=True,
                            timeout=self.timeout
                        )
                        break
                    except Exception as e:
                        if attempt == 1:
                            logger.warning(f"청크 {i}-{i+self.chunk_size} 최종 실패: {e}")
                            break
                        else:
                            time.sleep(1)
                
                if data is None or data.empty or 'Close' not in data.columns:
                    continue

                close_prices = data['Close'].dropna(axis=1, how='all')
                if close_prices.empty or len(close_prices) < 2:
                    continue

                start_prices = close_prices.bfill().iloc[0]
                end_prices = close_prices.ffill().iloc[-1]
                
                perf_series = ((end_prices - start_prices) / start_prices) * 100
                
                for ticker, performance in perf_series.items():
                    if pd.notna(performance) and -90 <= performance <= 900:
                        all_performance_data.append({
                            "ticker": ticker,
                            "name": name_map.get(ticker, ticker),
                            "performance": performance
                        })

                processed_chunks += 1
                
                # 진행률 로깅
                progress = (processed_chunks / min(self.max_chunks, len(limited_tickers) // self.chunk_size + 1)) * 100
                logger.info(f"미국 주식 진행률: {progress:.1f}% ({processed_chunks} 청크 완료)")
                
                # API 호출 간격 조절
                time.sleep(0.2)
                
            except Exception as e:
                logger.warning(f"청크 {i}-{i+self.chunk_size} 처리 중 오류: {e}")
                continue
        
        logger.info(f"미국 주식 분석 완료: {len(all_performance_data)}개 데이터 수집")
        return pd.DataFrame(all_performance_data)

    def _get_performance_us(self, tickers: List[str], name_map: Dict[str, str], 
                           start_date: str, end_date: str) -> pd.DataFrame:
        """호환성을 위한 별칭"""
        return self._get_performance_us_optimized(tickers, name_map, start_date, end_date)

    def get_market_performance(self, market: str, start_date: str, end_date: str, top_n: int) -> Dict[str, Any]:
        """Config 기반 시장 성과 분석 - 캐싱 적용"""
        logger.info(f"성능 분석 시작: Market={market}, Period={start_date}~{end_date}, Top={top_n}")
        
        # 캐시 확인
        cached_result = cache_service.get(
            "market_performance",
            market=market,
            start_date=start_date,
            end_date=end_date,
            top_n=top_n
        )
        
        if cached_result:
            logger.info(f"✅ 캐시에서 데이터 반환: {market}")
            return cached_result
        
        # 캐시 미스 - 실제 계산 수행
        listing = self._get_tickers_by_market_cached(market)
        if listing.empty:
            logger.warning(f"'{market}'에 대한 티커 목록을 찾을 수 없습니다.")
            return {"top_performers": [], "bottom_performers": []}

        tickers = listing['ticker'].tolist()
        name_map = listing.set_index('ticker')['name'].to_dict()

        # 시장별 성능 분석
        if market in ["KOSPI", "KOSDAQ"]:
            performance_df = self._get_performance_kr(tickers, name_map, start_date, end_date)
        else:
            performance_df = self._get_performance_us_optimized(tickers, name_map, start_date, end_date)
        
        if performance_df.empty:
            result = {"top_performers": [], "bottom_performers": []}
        else:
            # 정렬 및 결과 생성
            performance_df = performance_df.sort_values(by='performance', ascending=False)
            
            top_performers = performance_df.head(top_n).to_dict('records')
            bottom_performers = performance_df.tail(top_n).sort_values(
                by='performance', ascending=True
            ).to_dict('records')
            
            result = {
                "top_performers": top_performers, 
                "bottom_performers": bottom_performers,
                "total_analyzed": len(performance_df),
                "analysis_period": f"{start_date} ~ {end_date}",
                "market": market
            }
        
        # 결과를 캐시에 저장
        cache_service.set(
            "market_performance",
            result,
            ttl=self.cache_ttl,
            market=market,
            start_date=start_date,
            end_date=end_date,
            top_n=top_n
        )
        
        logger.info(f"성능 분석 완료: 상위 {len(result.get('top_performers', []))}개, "
                   f"하위 {len(result.get('bottom_performers', []))}개")
        
        return result

    def get_market_performance_fast(self, market: str, start_date: str, end_date: str, top_n: int = 20) -> Dict[str, Any]:
        """빠른 성과 분석 (더 제한적)"""
        original_max_tickers = self.max_tickers
        original_chunk_size = self.chunk_size
        original_max_chunks = self.max_chunks
        
        try:
            # 빠른 분석용 제한 설정
            self.max_tickers = 500
            self.chunk_size = 25
            self.max_chunks = 10
            
            return self.get_market_performance(market, start_date, end_date, min(top_n, 20))
        finally:
            # 원래 설정 복원
            self.max_tickers = original_max_tickers
            self.chunk_size = original_chunk_size
            self.max_chunks = original_max_chunks

    def clear_cache(self, market: str = None) -> bool:
        """캐시 클리어"""
        if market:
            pattern = f"market_performance:*{market}*"
            return cache_service.clear(pattern)
        else:
            return cache_service.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보"""
        stats = cache_service.get_stats()
        stats.update({
            "config": {
                "chunk_size": self.chunk_size,
                "timeout": self.timeout,
                "max_tickers": self.max_tickers,
                "max_chunks": self.max_chunks,
                "cache_ttl": self.cache_ttl
            }
        })
        return stats

# 호환성을 위한 별칭
PerformanceService.get_market_performance_cached = PerformanceService.get_market_performance