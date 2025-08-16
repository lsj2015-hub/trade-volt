import pandas as pd
import os
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum

from app.schemas import StockItem

logger = logging.getLogger(__name__)


class Market(Enum):
    """시장 구분"""
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    NASDAQ = "NASDAQ"
    NYSE = "NYSE"
    AMEX = "AMEX"


@dataclass
class StockData:
    """종목 데이터 클래스"""
    code: str
    name: str
    market: Market
    sector: Optional[str] = None
    industry: Optional[str] = None


class StockDataLoader:
    """
    Excel 파일에서 종목 데이터를 로드하고 검색하는 서비스
    """
    
    def __init__(self, data_dir: str = "server/data"):
        self.data_dir = Path(data_dir)
        self._korean_stocks: List[StockData] = []
        self._overseas_stocks: Dict[Market, List[StockData]] = {}
        self._loaded = False
        
        # 파일 경로 설정
        self.korean_files = {
            Market.KOSPI: self.data_dir / "kospi_code.xlsx",
            Market.KOSDAQ: self.data_dir / "kosdaq_code.xlsx"
        }
        self.overseas_file = self.data_dir / "overseas_stock_code.xlsx"
        
        logger.info(f"✅ StockDataLoader 초기화 완료 - 데이터 디렉토리: {self.data_dir}")

    def load_all_data(self) -> bool:
        """모든 종목 데이터를 로드합니다."""
        try:
            success = True
            
            # 한국 주식 로드
            korean_success = self._load_korean_stocks()
            if not korean_success:
                logger.error("❌ 한국 주식 데이터 로드 실패")
                success = False
            
            # 해외 주식 로드
            overseas_success = self._load_overseas_stocks()
            if not overseas_success:
                logger.error("❌ 해외 주식 데이터 로드 실패")
                success = False
            
            if success:
                self._loaded = True
                total_korean = len(self._korean_stocks)
                total_overseas = sum(len(stocks) for stocks in self._overseas_stocks.values())
                logger.info(f"✅ 모든 종목 데이터 로드 완료 - 한국: {total_korean}개, 해외: {total_overseas}개")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 종목 데이터 로드 중 오류: {e}")
            return False

    def _load_korean_stocks(self) -> bool:
        """한국 주식 데이터를 로드합니다."""
        try:
            korean_stocks = []
            
            for market, file_path in self.korean_files.items():
                if not file_path.exists():
                    logger.warning(f"⚠️ 파일을 찾을 수 없습니다: {file_path}")
                    continue
                
                try:
                    # Excel 파일 읽기
                    df = pd.read_excel(file_path)
                    
                    # 필수 컬럼 확인
                    required_columns = ['종목코드', '종목명']
                    missing_columns = [col for col in required_columns if col not in df.columns]
                    
                    if missing_columns:
                        logger.error(f"❌ {file_path}: 필수 컬럼 누락 - {missing_columns}")
                        continue
                    
                    # 데이터 처리
                    for _, row in df.iterrows():
                        code = str(row['종목코드']).strip()
                        name = str(row['종목명']).strip()
                        
                        # 유효성 검사
                        if not code or not name or code == 'nan' or name == 'nan':
                            continue
                        
                        # 종목코드 포맷팅 (6자리 + .KS/.KQ)
                        if len(code) == 6 and code.isdigit():
                            if market == Market.KOSPI:
                                formatted_code = f"{code}.KS"
                            else:  # KOSDAQ
                                formatted_code = f"{code}.KQ"
                        else:
                            formatted_code = code
                        
                        stock_data = StockData(
                            code=formatted_code,
                            name=name,
                            market=market,
                            sector=row.get('업종', None),
                            industry=row.get('산업', None)
                        )
                        korean_stocks.append(stock_data)
                    
                    logger.info(f"✅ {market.value} 데이터 로드 완료: {len(df)}개 종목")
                    
                except Exception as e:
                    logger.error(f"❌ {file_path} 파일 처리 중 오류: {e}")
                    continue
            
            self._korean_stocks = korean_stocks
            logger.info(f"✅ 한국 주식 데이터 로드 완료: 총 {len(korean_stocks)}개 종목")
            return True
            
        except Exception as e:
            logger.error(f"❌ 한국 주식 데이터 로드 실패: {e}")
            return False

    def _load_overseas_stocks(self) -> bool:
        """해외 주식 데이터를 로드합니다."""
        try:
            if not self.overseas_file.exists():
                logger.warning(f"⚠️ 해외 주식 파일을 찾을 수 없습니다: {self.overseas_file}")
                return False
            
            # Excel 파일 읽기
            df = pd.read_excel(self.overseas_file)
            
            # 필수 컬럼 확인
            required_columns = ['Symbol', '종목명', '시장']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                logger.error(f"❌ 해외 주식 파일: 필수 컬럼 누락 - {missing_columns}")
                return False
            
            # 시장별로 분류
            overseas_stocks = {market: [] for market in [Market.NASDAQ, Market.NYSE, Market.AMEX]}
            
            for _, row in df.iterrows():
                symbol = str(row['Symbol']).strip().upper()
                name = str(row['종목명']).strip()
                market_str = str(row['시장']).strip().upper()
                
                # 유효성 검사
                if not symbol or not name or symbol == 'NAN' or name == 'NAN':
                    continue
                
                # 시장 매핑
                market_mapping = {
                    'NASDAQ': Market.NASDAQ,
                    'NASD': Market.NASDAQ,
                    'NYSE': Market.NYSE,
                    'AMEX': Market.AMEX,
                    'NYQ': Market.NYSE,  # Yahoo Finance 형식
                    'NMS': Market.NASDAQ  # NASDAQ Global Market
                }
                
                market = market_mapping.get(market_str)
                if not market:
                    logger.debug(f"알 수 없는 시장: {market_str} (종목: {symbol})")
                    continue
                
                stock_data = StockData(
                    code=symbol,
                    name=name,
                    market=market,
                    sector=row.get('섹터', None),
                    industry=row.get('산업', None)
                )
                overseas_stocks[market].append(stock_data)
            
            self._overseas_stocks = overseas_stocks
            
            # 로딩 결과 로그
            for market, stocks in overseas_stocks.items():
                logger.info(f"✅ {market.value} 데이터 로드 완료: {len(stocks)}개 종목")
            
            total_overseas = sum(len(stocks) for stocks in overseas_stocks.values())
            logger.info(f"✅ 해외 주식 데이터 로드 완료: 총 {total_overseas}개 종목")
            return True
            
        except Exception as e:
            logger.error(f"❌ 해외 주식 데이터 로드 실패: {e}")
            return False

    def search_korean_stocks(self, query: str, limit: int = 20) -> List[StockItem]:
        """한국 주식을 검색합니다."""
        if not self._loaded:
            logger.warning("⚠️ 데이터가 로드되지 않았습니다. load_all_data()를 먼저 실행해주세요.")
            return []
        
        if not query.strip():
            return []
        
        query = query.strip().upper()
        results = []
        
        for stock in self._korean_stocks:
            # 종목코드 또는 종목명에서 검색
            if (query in stock.code.upper() or 
                query in stock.name.upper() or
                query.replace('.', '') in stock.code.replace('.', '').upper()):
                
                results.append(StockItem(
                    code=stock.code,
                    name=stock.name
                ))
                
                if len(results) >= limit:
                    break
        
        logger.debug(f"한국 주식 검색 결과: '{query}' -> {len(results)}개")
        return results

    def search_overseas_stocks(self, query: str, markets: Optional[List[str]] = None, limit: int = 20) -> List[StockItem]:
        """해외 주식을 검색합니다."""
        if not self._loaded:
            logger.warning("⚠️ 데이터가 로드되지 않았습니다. load_all_data()를 먼저 실행해주세요.")
            return []
        
        if not query.strip():
            return []
        
        query = query.strip().upper()
        
        # 검색할 시장 결정
        if markets:
            search_markets = []
            for market_str in markets:
                try:
                    market = Market(market_str.upper())
                    if market in self._overseas_stocks:
                        search_markets.append(market)
                except ValueError:
                    logger.warning(f"알 수 없는 시장: {market_str}")
        else:
            # 기본적으로 모든 해외 시장 검색
            search_markets = [Market.NASDAQ, Market.NYSE, Market.AMEX]
        
        results = []
        
        for market in search_markets:
            if market not in self._overseas_stocks:
                continue
                
            for stock in self._overseas_stocks[market]:
                # Symbol 또는 종목명에서 검색
                if (query in stock.code.upper() or 
                    query in stock.name.upper()):
                    
                    results.append(StockItem(
                        code=stock.code,
                        name=stock.name
                    ))
                    
                    if len(results) >= limit:
                        break
            
            if len(results) >= limit:
                break
        
        logger.debug(f"해외 주식 검색 결과: '{query}' -> {len(results)}개")
        return results

    def get_stock_by_code(self, code: str) -> Optional[StockData]:
        """종목코드로 특정 종목을 조회합니다."""
        if not self._loaded:
            return None
        
        code = code.strip().upper()
        
        # 한국 주식에서 검색
        for stock in self._korean_stocks:
            if stock.code.upper() == code:
                return stock
        
        # 해외 주식에서 검색
        for stocks in self._overseas_stocks.values():
            for stock in stocks:
                if stock.code.upper() == code:
                    return stock
        
        return None

    def get_market_stocks(self, market: str) -> List[StockData]:
        """특정 시장의 모든 종목을 반환합니다."""
        if not self._loaded:
            return []
        
        try:
            market_enum = Market(market.upper())
        except ValueError:
            logger.warning(f"알 수 없는 시장: {market}")
            return []
        
        if market_enum in [Market.KOSPI, Market.KOSDAQ]:
            return [stock for stock in self._korean_stocks if stock.market == market_enum]
        else:
            return self._overseas_stocks.get(market_enum, [])

    def get_data_stats(self) -> Dict[str, int]:
        """로드된 데이터의 통계를 반환합니다."""
        if not self._loaded:
            return {"error": "데이터가 로드되지 않음"}
        
        stats = {
            "total_korean": len(self._korean_stocks),
            "kospi": len([s for s in self._korean_stocks if s.market == Market.KOSPI]),
            "kosdaq": len([s for s in self._korean_stocks if s.market == Market.KOSDAQ]),
        }
        
        for market in [Market.NASDAQ, Market.NYSE, Market.AMEX]:
            stats[market.value.lower()] = len(self._overseas_stocks.get(market, []))
        
        stats["total_overseas"] = sum(len(stocks) for stocks in self._overseas_stocks.values())
        stats["total"] = stats["total_korean"] + stats["total_overseas"]
        
        return stats

    def reload_data(self) -> bool:
        """데이터를 다시 로드합니다."""
        logger.info("🔄 종목 데이터 재로드 시작...")
        self._loaded = False
        self._korean_stocks.clear()
        self._overseas_stocks.clear()
        return self.load_all_data()


# 전역 인스턴스 생성
stock_data_loader = StockDataLoader()