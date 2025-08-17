import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from app.config import settings
from app.schemas import StockItem, TokenData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KoreaInvestmentService:
    """
    한국투자증권 Open API 서비스 클래스
    토큰 관리, 주식 정보 조회 등의 기능을 제공합니다.
    """
    
    def __init__(self):
        # 환경변수에서 API 키 정보 로드
        self.APP_KEY = settings.KIS_APP_KEY
        self.APP_SECRET = settings.KIS_APP_SECRET
        self.BASE_URL = settings.KIS_BASE_URL
        
        # 토큰 파일 경로를 절대경로로 설정
        self._token_data_path = Path(__file__).parent.parent / "data" / "kis_token.json"
        self._token_data_path.parent.mkdir(exist_ok=True)
        
        # API 키 검증
        if not all([self.APP_KEY, self.APP_SECRET, self.BASE_URL]):
            logger.error("❌ KIS API 설정이 누락되었습니다. .env 파일을 확인해주세요.")
            raise ValueError("KIS API 설정이 누락되었습니다.")
        
        logger.info(f"✅ KIS Service 초기화 완료 - Server: {self.BASE_URL}")
        
        # 종목 데이터 로드
        self._initialize_stock_data()
        
        # 초기화 시 토큰 유효성 검사
        self._validate_token_on_startup()

    def _initialize_stock_data(self) -> None:
        """종목 데이터를 초기화합니다."""
        try:
            logger.info("📊 종목 데이터 로드 시작...")
            # stock_data_loader가 없는 경우 기본 처리
            try:
                from app.core.stock_data_loader import stock_data_loader
                success = stock_data_loader.load_all_data()
                if success:
                    stats = stock_data_loader.get_data_stats()
                    logger.info(f"✅ 종목 데이터 로드 완료: {stats}")
                else:
                    logger.warning("⚠️ 종목 데이터 로드에 일부 실패했습니다.")
            except ImportError:
                logger.warning("⚠️ stock_data_loader 모듈이 없습니다. 기본 종목 데이터를 사용합니다.")
                self._load_default_stock_data()
        except Exception as e:
            logger.error(f"❌ 종목 데이터 초기화 실패: {e}")
            self._load_default_stock_data()

    def _load_default_stock_data(self) -> None:
        """기본 종목 데이터를 로드합니다."""
        try:
            # 기본 한국 주요 종목들
            self.default_stocks = [
                {"code": "005930", "name": "삼성전자", "market": "KOSPI"},
                {"code": "000660", "name": "SK하이닉스", "market": "KOSPI"},
                {"code": "035420", "name": "NAVER", "market": "KOSPI"},
                {"code": "051910", "name": "LG화학", "market": "KOSPI"},
                {"code": "207940", "name": "삼성바이오로직스", "market": "KOSPI"},
            ]
            logger.info("✅ 기본 종목 데이터 로드 완료")
        except Exception as e:
            logger.error(f"❌ 기본 종목 데이터 로드 실패: {e}")
            self.default_stocks = []

    def _validate_token_on_startup(self) -> None:
        """서비스 시작 시 토큰 유효성을 검사합니다."""
        try:
            token = self.get_access_token()
            if token:
                logger.info("✅ 기존 토큰이 유효하거나 새 토큰 발급 완료")
                # 토큰 유효성 테스트
                if self.test_connection():
                    logger.info("✅ KIS API 연결 테스트 성공")
                else:
                    logger.warning("⚠️ KIS API 연결 테스트 실패")
            else:
                logger.warning("⚠️ 토큰 발급에 실패했습니다.")
        except Exception as e:
            logger.error(f"❌ 토큰 검증 중 오류 발생: {e}")

    def get_access_token(self) -> Optional[str]:
        """
        유효한 액세스 토큰을 반환합니다.
        기존 토큰이 유효하면 재사용하고, 만료되었으면 새로 발급받습니다.
        
        Returns:
            str: 유효한 액세스 토큰
            None: 토큰 발급 실패 시
        """
        # 기존 토큰 파일이 있는지 확인
        if self._token_data_path.exists():
            try:
                with open(self._token_data_path, "r", encoding="utf-8") as f:
                    token_data = TokenData(**json.load(f))
                
                # 토큰 만료 시간 확인 (10분 여유 시간 추가)
                expires_at = datetime.strptime(token_data.expires_at, "%Y-%m-%d %H:%M:%S")
                if expires_at > datetime.now() + timedelta(minutes=10):
                    logger.debug("🔄 기존 토큰 재사용")
                    return token_data.access_token
                else:
                    logger.info("⏰ 기존 토큰이 만료되었습니다. 새 토큰을 발급받습니다.")
            
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                logger.warning(f"⚠️ 토큰 파일 읽기 실패: {e}. 새 토큰을 발급받습니다.")
        
        # 새 토큰 발급
        return self._issue_new_token()

    def _issue_new_token(self) -> Optional[str]:
        """
        KIS Open API에서 새로운 액세스 토큰을 발급받습니다.
        
        Returns:
            str: 새로 발급받은 액세스 토큰
            None: 토큰 발급 실패 시
        """
        try:
            # API 요청 설정
            path = "/oauth2/tokenP"
            url = f"{self.BASE_URL}{path}"
            headers = {
                "content-type": "application/json"
            }
            body = {
                "grant_type": "client_credentials",
                "appkey": self.APP_KEY,
                "appsecret": self.APP_SECRET
            }
            
            logger.info("🔑 새 액세스 토큰 발급 요청...")
            
            # API 호출
            response = requests.post(url, headers=headers, data=json.dumps(body), timeout=30)
            response.raise_for_status()
            
            token_info = response.json()
            
            # 응답 검증
            if "access_token" not in token_info:
                logger.error(f"❌ 토큰 발급 실패 - 응답: {token_info}")
                return None
            
            # 토큰 만료 시간 계산 (24시간 - 여유시간)
            expires_at = datetime.now() + timedelta(seconds=token_info.get("expires_in", 86400))
            
            # 토큰 데이터 객체 생성
            token_data = TokenData(
                access_token=token_info["access_token"],
                expires_at=expires_at.strftime("%Y-%m-%d %H:%M:%S")
            )
            
            # 토큰 파일에 저장
            with open(self._token_data_path, "w", encoding="utf-8") as f:
                json.dump(token_data.model_dump(), f, ensure_ascii=False, indent=2)
            
            logger.info("✅ 새 액세스 토큰 발급 및 저장 완료")
            return token_data.access_token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ API 요청 실패: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 토큰 발급 중 예상치 못한 오류: {e}")
            return None

    def _get_auth_headers(self, tr_id: str) -> Dict[str, str]:
        """
        KIS API 요청에 필요한 인증 헤더를 생성합니다.
        
        Args:
            tr_id: 거래 ID (API마다 다름)
            
        Returns:
            dict: 인증 헤더 딕셔너리
        """
        token = self.get_access_token()
        if not token:
            raise ValueError("액세스 토큰을 가져올 수 없습니다.")
        
        return {
            "authorization": f"Bearer {token}",
            "appkey": self.APP_KEY,
            "appsecret": self.APP_SECRET,
            "tr_id": tr_id,
            "content-type": "application/json"
        }

    def test_connection(self) -> bool:
        """
        KIS API 연결 테스트를 수행합니다.
        
        Returns:
            bool: 연결 성공 여부
        """
        try:
            # 간단한 API 호출로 연결 테스트 (주식 기본정보 조회)
            headers = self._get_auth_headers("FHKST01010100")
            
            # 삼성전자 기본정보 조회로 테스트
            url = f"{self.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": "005930"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            return result.get("rt_cd") == "0"  # 성공 코드
            
        except Exception as e:
            logger.error(f"❌ 연결 테스트 실패: {e}")
            return False

    def search_stocks_by_market(self, query: str, market: str = "KOR", limit: int = 20) -> List[StockItem]:
        """
        시장별로 주식을 검색합니다.
        
        Args:
            query: 검색어 (종목명 또는 종목코드)
            market: 시장 구분 (KOR, USA, KOSPI, KOSDAQ 등)
            limit: 최대 반환 개수
            
        Returns:
            List[StockItem]: 검색된 종목 리스트
        """
        try:
            # 현재는 기본 종목 데이터에서 검색
            results = []
            query_lower = query.lower()
            
            for stock in getattr(self, 'default_stocks', []):
                if (query_lower in stock['name'].lower() or 
                    query_lower in stock['code'] or
                    query in stock['name']):
                    results.append(StockItem(
                        symbol=stock['code'],
                        name=stock['name'],
                        market=stock['market']
                    ))
                    
                if len(results) >= limit:
                    break
            
            logger.info(f"검색어 '{query}'로 {len(results)}개 종목 검색됨")
            return results
            
        except Exception as e:
            logger.error(f"주식 검색 오류: {e}")
            return []

    def search_korean_stocks(self, query: str, limit: int = 20) -> List[StockItem]:
        """한국 주식만 검색합니다."""
        return self.search_stocks_by_market(query, "KOR", limit)

    def search_overseas_stocks(self, query: str, market_list: Optional[List[str]] = None, limit: int = 20) -> List[StockItem]:
        """해외 주식만 검색합니다."""
        # 현재는 한국 주식만 지원
        logger.warning("해외 주식 검색은 아직 지원되지 않습니다.")
        return []

    def get_stock_info_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        종목코드로 주식 정보를 조회합니다.
        
        Args:
            code: 종목코드
            
        Returns:
            dict: 주식 정보 또는 None
        """
        try:
            headers = self._get_auth_headers("FHKST01010100")
            
            url = f"{self.BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
            params = {
                "fid_cond_mrkt_div_code": "J",
                "fid_input_iscd": code
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("rt_cd") == "0":
                output = result.get("output", {})
                return {
                    "symbol": code,
                    "name": output.get("hts_kor_isnm", ""),
                    "current_price": int(output.get("stck_prpr", 0)),
                    "change_rate": float(output.get("prdy_ctrt", 0)),
                    "volume": int(output.get("acml_vol", 0)),
                    "market_cap": int(output.get("hts_avls", 0)) if output.get("hts_avls") else None
                }
            else:
                logger.error(f"주식 정보 조회 실패: {result.get('msg1', '')}")
                return None
                
        except Exception as e:
            logger.error(f"주식 정보 조회 오류: {e}")
            return None

    def get_market_stocks(self, market: str) -> List[StockItem]:
        """특정 시장의 모든 종목을 조회합니다."""
        try:
            # 현재는 기본 종목 데이터 반환
            results = []
            for stock in getattr(self, 'default_stocks', []):
                if market.upper() in stock['market'].upper():
                    results.append(StockItem(
                        symbol=stock['code'],
                        name=stock['name'],
                        market=stock['market']
                    ))
            
            return results
            
        except Exception as e:
            logger.error(f"시장 종목 조회 오류: {e}")
            return []

    def get_stock_data_stats(self) -> Dict[str, Any]:
        """로드된 종목 데이터의 통계를 반환합니다."""
        return {
            "total_stocks": len(getattr(self, 'default_stocks', [])),
            "markets": ["KOSPI", "KOSDAQ"],
            "last_updated": datetime.now().isoformat(),
            "status": "loaded"
        }

    def reload_stock_data(self) -> bool:
        """종목 데이터를 다시 로드합니다."""
        try:
            self._initialize_stock_data()
            return True
        except Exception as e:
            logger.error(f"종목 데이터 재로드 실패: {e}")
            return False


# 전역 서비스 인스턴스 생성
kis_service = KoreaInvestmentService()