"""
종목 데이터 로더 모듈
한국 주식 시장의 종목 정보를 로드하고 관리합니다.
"""

import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class Market(Enum):
    """시장 구분"""
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ" 
    KONEX = "KONEX"


@dataclass
class StockInfo:
    """종목 정보"""
    code: str
    name: str
    market: Market
    sector: Optional[str] = None
    industry: Optional[str] = None


class StockDataLoader:
    """종목 데이터 로더 클래스"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # 종목 데이터 저장
        self.stocks: Dict[str, StockInfo] = {}
        self.markets: Dict[Market, List[StockInfo]] = {
            Market.KOSPI: [],
            Market.KOSDAQ: [],
            Market.KONEX: []
        }
        
        self.is_loaded = False
        
    def load_all_data(self) -> bool:
        """모든 종목 데이터를 로드합니다."""
        try:
            logger.info("📊 종목 데이터 로드 시작...")
            
            # 1. 로컬 파일에서 로드 시도
            if self._load_from_local():
                logger.info("✅ 로컬 파일에서 종목 데이터 로드 완료")
                self.is_loaded = True
                return True
            
            # 2. 기본 종목 데이터 로드
            logger.info("📝 기본 종목 데이터를 로드합니다...")
            self._load_default_data()
            
            # 3. 로컬 파일로 저장
            self._save_to_local()
            
            self.is_loaded = True
            logger.info("✅ 종목 데이터 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 종목 데이터 로드 실패: {e}")
            return False
    
    def _load_from_local(self) -> bool:
        """로컬 파일에서 종목 데이터를 로드합니다."""
        try:
            stock_file = self.data_dir / "stocks.json"
            if not stock_file.exists():
                return False
            
            with open(stock_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 데이터 파싱
            for stock_data in data.get('stocks', []):
                stock_info = StockInfo(
                    code=stock_data['code'],
                    name=stock_data['name'],
                    market=Market(stock_data['market']),
                    sector=stock_data.get('sector'),
                    industry=stock_data.get('industry')
                )
                
                self.stocks[stock_info.code] = stock_info
                self.markets[stock_info.market].append(stock_info)
            
            logger.info(f"로컬 파일에서 {len(self.stocks)}개 종목 로드 완료")
            return True
            
        except Exception as e:
            logger.error(f"로컬 파일 로드 실패: {e}")
            return False
    
    def _load_default_data(self) -> None:
        """기본 종목 데이터를 로드합니다."""
        # 주요 KOSPI 종목들
        kospi_stocks = [
            {"code": "005930", "name": "삼성전자", "sector": "반도체", "industry": "반도체"},
            {"code": "000660", "name": "SK하이닉스", "sector": "반도체", "industry": "반도체"},
            {"code": "035420", "name": "NAVER", "sector": "인터넷", "industry": "포털검색"},
            {"code": "051910", "name": "LG화학", "sector": "화학", "industry": "종합화학"},
            {"code": "207940", "name": "삼성바이오로직스", "sector": "바이오", "industry": "바이오의약품"},
            {"code": "006400", "name": "삼성SDI", "sector": "전기전자", "industry": "2차전지"},
            {"code": "373220", "name": "LG에너지솔루션", "sector": "전기전자", "industry": "2차전지"},
            {"code": "035720", "name": "카카오", "sector": "인터넷", "industry": "모바일게임"},
            {"code": "068270", "name": "셀트리온", "sector": "바이오", "industry": "바이오의약품"},
            {"code": "028260", "name": "삼성물산", "sector": "건설", "industry": "종합건설"},
            {"code": "012330", "name": "현대모비스", "sector": "자동차", "industry": "자동차부품"},
            {"code": "066570", "name": "LG전자", "sector": "전기전자", "industry": "가전제품"},
            {"code": "003670", "name": "포스코홀딩스", "sector": "철강", "industry": "철강"},
            {"code": "096770", "name": "SK이노베이션", "sector": "화학", "industry": "정유"},
            {"code": "034020", "name": "두산에너빌리티", "sector": "기계", "industry": "발전설비"},
        ]
        
        # 주요 KOSDAQ 종목들
        kosdaq_stocks = [
            {"code": "247540", "name": "에코프로비엠", "sector": "전기전자", "industry": "2차전지소재"},
            {"code": "086520", "name": "에코프로", "sector": "전기전자", "industry": "2차전지소재"},
            {"code": "091990", "name": "셀트리온헬스케어", "sector": "바이오", "industry": "바이오의약품"},
            {"code": "196170", "name": "알테오젠", "sector": "바이오", "industry": "바이오의약품"},
            {"code": "039030", "name": "이오테크닉스", "sector": "반도체", "industry": "반도체장비"},
            {"code": "067310", "name": "하나마이크론", "sector": "반도체", "industry": "반도체"},
            {"code": "112040", "name": "위메이드", "sector": "게임", "industry": "게임소프트웨어"},
            {"code": "293490", "name": "카카오게임즈", "sector": "게임", "industry": "게임소프트웨어"},
            {"code": "058470", "name": "리노공업", "sector": "반도체", "industry": "반도체장비"},
            {"code": "277810", "name": "레인보우로보틱스", "sector": "기계", "industry": "로봇"},
        ]
        
        # KOSPI 종목 추가
        for stock_data in kospi_stocks:
            stock_info = StockInfo(
                code=stock_data["code"],
                name=stock_data["name"],
                market=Market.KOSPI,
                sector=stock_data.get("sector"),
                industry=stock_data.get("industry")
            )
            self.stocks[stock_info.code] = stock_info
            self.markets[Market.KOSPI].append(stock_info)
        
        # KOSDAQ 종목 추가
        for stock_data in kosdaq_stocks:
            stock_info = StockInfo(
                code=stock_data["code"],
                name=stock_data["name"],
                market=Market.KOSDAQ,
                sector=stock_data.get("sector"),
                industry=stock_data.get("industry")
            )
            self.stocks[stock_info.code] = stock_info
            self.markets[Market.KOSDAQ].append(stock_info)
        
        logger.info(f"기본 종목 데이터 로드 완료: KOSPI {len(kospi_stocks)}개, KOSDAQ {len(kosdaq_stocks)}개")
    
    def _save_to_local(self) -> None:
        """종목 데이터를 로컬 파일에 저장합니다."""
        try:
            stock_file = self.data_dir / "stocks.json"
            
            # 저장할 데이터 구성
            save_data = {
                "last_updated": "2024-01-01",
                "total_count": len(self.stocks),
                "stocks": []
            }
            
            for stock in self.stocks.values():
                save_data["stocks"].append({
                    "code": stock.code,
                    "name": stock.name,
                    "market": stock.market.value,
                    "sector": stock.sector,
                    "industry": stock.industry
                })
            
            with open(stock_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"종목 데이터를 로컬 파일에 저장: {stock_file}")
            
        except Exception as e:
            logger.error(f"로컬 파일 저장 실패: {e}")
    
    def get_data_stats(self) -> Dict[str, Any]:
        """종목 데이터 통계를 반환합니다."""
        return {
            "total_stocks": len(self.stocks),
            "kospi_stocks": len(self.markets[Market.KOSPI]),
            "kosdaq_stocks": len(self.markets[Market.KOSDAQ]),
            "konex_stocks": len(self.markets[Market.KONEX]),
            "is_loaded": self.is_loaded,
            "sectors": list(set(stock.sector for stock in self.stocks.values() if stock.sector)),
            "industries": list(set(stock.industry for stock in self.stocks.values() if stock.industry))
        }
    
    def search_stocks(self, query: str, market: Optional[Market] = None, limit: int = 20) -> List[StockInfo]:
        """종목을 검색합니다."""
        if not self.is_loaded:
            logger.warning("종목 데이터가 로드되지 않았습니다.")
            return []
        
        results = []
        query_lower = query.lower()
        
        search_stocks = list(self.stocks.values())
        if market:
            search_stocks = self.markets[market]
        
        for stock in search_stocks:
            if (query_lower in stock.name.lower() or 
                query_lower in stock.code.lower() or
                query in stock.name or
                query in stock.code):
                results.append(stock)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_stock_by_code(self, code: str) -> Optional[StockInfo]:
        """종목코드로 종목 정보를 조회합니다."""
        return self.stocks.get(code)
    
    def get_market_stocks(self, market: Market, limit: Optional[int] = None) -> List[StockInfo]:
        """특정 시장의 종목들을 조회합니다."""
        stocks = self.markets.get(market, [])
        if limit:
            return stocks[:limit]
        return stocks
    
    def reload_data(self) -> bool:
        """종목 데이터를 다시 로드합니다."""
        self.stocks.clear()
        for market_stocks in self.markets.values():
            market_stocks.clear()
        self.is_loaded = False
        
        return self.load_all_data()


# 글로벌 인스턴스 생성
stock_data_loader = StockDataLoader()