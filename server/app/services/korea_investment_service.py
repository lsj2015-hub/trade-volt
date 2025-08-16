import requests
import json
import os
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

from app.config import settings
from app.schemas import StockItem, TokenData
from app.core.stock_data_loader import stock_data_loader, Market

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
        self._token_data_path = "kis_token.json"
        
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
            success = stock_data_loader.load_all_data()
            if success:
                stats = stock_data_loader.get_data_stats()
                logger.info(f"✅ 종목 데이터 로드 완료: {stats}")
            else:
                logger.warning("⚠️ 종목 데이터 로드에 일부 실패했습니다.")
        except Exception as e:
            logger.error(f"❌ 종목 데이터 초기화 실패: {e}")

    def _validate_token_on_startup(self) -> None:
        """서비스 시작 시 토큰 유효성을 검사합니다."""
        try:
            token = self.get_access_token()
            if token:
                logger.info("✅ 기존 토큰이 유효하거나 새 토큰 발급 완료")
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
        if os.path.exists(self._token_data_path):
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
            token = self.get_access_token()
            if token:
                logger.info("✅ KIS API 연결 테스트 성공")
                return True
            else:
                logger.error("❌ KIS API 연결 테스트 실패 - 토큰 없음")
                return False
        except Exception as e:
            logger.error(f"❌ KIS API 연결 테스트 실패: {e}")
            return False

    def get_token_info(self) -> Optional[Dict[str, Any]]:
        """
        현재 토큰 정보를 반환합니다. (디버그용)
        
        Returns:
            dict: 토큰 정보 (토큰값 제외)
            None: 토큰 파일이 없거나 읽기 실패 시
        """
        try:
            if os.path.exists(self._token_data_path):
                with open(self._token_data_path, "r", encoding="utf-8") as f:
                    token_data = json.load(f)
                
                expires_at = datetime.strptime(token_data["expires_at"], "%Y-%m-%d %H:%M:%S")
                time_left = expires_at - datetime.now()
                
                return {
                    "expires_at": token_data["expires_at"],
                    "is_valid": time_left > timedelta(minutes=10),
                    "time_left_minutes": int(time_left.total_seconds() / 60),
                    "token_length": len(token_data.get("access_token", ""))
                }
            else:
                return {"status": "토큰 파일 없음"}
                
        except Exception as e:
            logger.error(f"토큰 정보 조회 실패: {e}")
            return None

    def refresh_token(self) -> bool:
        """
        강제로 새 토큰을 발급받습니다.
        
        Returns:
            bool: 토큰 갱신 성공 여부
        """
        try:
            # 기존 토큰 파일 삭제
            if os.path.exists(self._token_data_path):
                os.remove(self._token_data_path)
                logger.info("기존 토큰 파일 삭제")
            
            # 새 토큰 발급
            new_token = self._issue_new_token()
            if new_token:
                logger.info("✅ 토큰 강제 갱신 완료")
                return True
            else:
                logger.error("❌ 토큰 강제 갱신 실패")
                return False
                
        except Exception as e:
            logger.error(f"토큰 갱신 중 오류: {e}")
            return False


            return False


    # =========================
    # 종목 검색 및 조회 기능
    # =========================
    
    def search_korean_stocks(self, query: str, limit: int = 20) -> List[StockItem]:
        """
        한국 주식을 검색합니다.
        
        Args:
            query: 검색어 (종목명 또는 종목코드)
            limit: 최대 반환 개수
            
        Returns:
            List[StockItem]: 검색된 종목 목록
        """
        try:
            return stock_data_loader.search_korean_stocks(query, limit)
        except Exception as e:
            logger.error(f"한국 주식 검색 오류: {e}")
            return []

    def search_overseas_stocks(self, query: str, markets: Optional[List[str]] = None, limit: int = 20) -> List[StockItem]:
        """
        해외 주식을 검색합니다.
        
        Args:
            query: 검색어 (Symbol 또는 종목명)
            markets: 검색할 시장 목록 (NASDAQ, NYSE, AMEX 등)
            limit: 최대 반환 개수
            
        Returns:
            List[StockItem]: 검색된 종목 목록
        """
        try:
            # 기본적으로 주요 미국 시장에서 검색
            if markets is None:
                markets = ["NASDAQ", "NYSE", "AMEX"]
            
            return stock_data_loader.search_overseas_stocks(query, markets, limit)
        except Exception as e:
            logger.error(f"해외 주식 검색 오류: {e}")
            return []

    def search_stocks_by_market(self, query: str, market: str, limit: int = 20) -> List[StockItem]:
        """
        특정 시장에서 주식을 검색합니다.
        
        Args:
            query: 검색어
            market: 시장 (KOR, KOSPI, KOSDAQ, NASDAQ, NYSE, AMEX 등)
            limit: 최대 반환 개수
            
        Returns:
            List[StockItem]: 검색된 종목 목록
        """
        market_upper = market.upper()
        
        if market_upper in ["KOR", "KOREA", "KOSPI", "KOSDAQ"]:
            return self.search_korean_stocks(query, limit)
        elif market_upper in ["USA", "US", "NASDAQ", "NYSE", "AMEX"]:
            if market_upper in ["USA", "US"]:
                return self.search_overseas_stocks(query, None, limit)
            else:
                return self.search_overseas_stocks(query, [market_upper], limit)
        else:
            logger.warning(f"알 수 없는 시장: {market}")
            return []

    def get_stock_info_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        종목코드로 주식 정보를 조회합니다.
        
        Args:
            code: 종목코드 또는 Symbol
            
        Returns:
            dict: 종목 정보 또는 None
        """
        try:
            stock_data = stock_data_loader.get_stock_by_code(code)
            if stock_data:
                return {
                    "code": stock_data.code,
                    "name": stock_data.name,
                    "market": stock_data.market.value,
                    "sector": stock_data.sector,
                    "industry": stock_data.industry
                }
            return None
        except Exception as e:
            logger.error(f"종목 정보 조회 오류: {e}")
            return None

    def get_market_stocks(self, market: str) -> List[StockItem]:
        """
        특정 시장의 모든 종목을 반환합니다.
        
        Args:
            market: 시장명 (KOSPI, KOSDAQ, NASDAQ, NYSE, AMEX)
            
        Returns:
            List[StockItem]: 시장 내 모든 종목
        """
        try:
            stock_data_list = stock_data_loader.get_market_stocks(market)
            return [
                StockItem(code=stock.code, name=stock.name) 
                for stock in stock_data_list
            ]
        except Exception as e:
            logger.error(f"시장 종목 조회 오류: {e}")
            return []

    def get_stock_data_stats(self) -> Dict[str, Any]:
        """
        로드된 종목 데이터의 통계를 반환합니다.
        
        Returns:
            dict: 종목 데이터 통계
        """
        try:
            return stock_data_loader.get_data_stats()
        except Exception as e:
            logger.error(f"종목 데이터 통계 조회 오류: {e}")
            return {"error": str(e)}

    def reload_stock_data(self) -> bool:
        """
        종목 데이터를 다시 로드합니다.
        
        Returns:
            bool: 재로드 성공 여부
        """
        try:
            logger.info("🔄 종목 데이터 재로드 요청...")
            return stock_data_loader.reload_data()
        except Exception as e:
            logger.error(f"종목 데이터 재로드 오류: {e}")
            return False


# 전역 서비스 인스턴스 생성
kis_service = KoreaInvestmentService()