import requests
import json
import os
import io
import zipfile
from datetime import datetime, timedelta
from typing import List
import logging

from app.config import settings
from app.schemas import StockItem, OverseasStockSearchResponse, TokenData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KoreaInvestmentService:
    def __init__(self):
        self.APP_KEY = settings.KIS_APP_KEY
        self.APP_SECRET = settings.KIS_APP_SECRET
        self.BASE_URL = settings.KIS_BASE_URL
        self._token_data_path = "kis_token.json"
        
        logger.info(f"✅ KIS Service initializing for REAL server: {self.BASE_URL}")
        self.korean_stock_list: List[StockItem] = self._get_korean_stock_master_list()

    def get_access_token(self) -> str:
        if os.path.exists(self._token_data_path):
            with open(self._token_data_path, "r") as f:
                try:
                    token_data = TokenData(**json.load(f))
                    if datetime.strptime(token_data.expires_at, "%Y-%m-%d %H:%M:%S") > datetime.now() + timedelta(minutes=10):
                        return token_data.access_token
                except Exception:
                    pass
        
        path = "/oauth2/tokenP"
        url = f"{self.BASE_URL}{path}"
        headers = {"content-type": "application/json"}
        body = {"grant_type": "client_credentials", "appkey": self.APP_KEY, "appsecret": self.APP_SECRET}
        res = requests.post(url, headers=headers, data=json.dumps(body))
        res.raise_for_status()
        token_info = res.json()
        expires_at = datetime.now() + timedelta(seconds=token_info["expires_in"])
        token_data = TokenData(access_token=token_info["access_token"], expires_at=expires_at.strftime("%Y-%m-%d %H:%M:%S"))
        with open(self._token_data_path, "w") as f:
            json.dump(token_data.model_dump(), f)
        return token_data.access_token

    def _get_auth_headers(self, tr_id: str) -> dict:
        return {"authorization": f"Bearer {self.get_access_token()}", "appkey": self.APP_KEY, "appsecret": self.APP_SECRET, "tr_id": tr_id}

    # --- 🌟 여기가 핵심: KIS 공식 GitHub의 .mst 파일 파싱 방식으로 최종 수정 ---
    def _get_korean_stock_master_list(self) -> List[StockItem]:
        logger.info("--- 국내 주식 마스터 파일 다운로드 시작 (공식 방식) ---")
        urls = {
            'kospi': 'https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip',
            'kosdaq': 'https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip',
        }
        stock_list = []

        for market, url in urls.items():
            try:
                logger.info(f"{market.upper()} 마스터 파일 다운로드 시도 -> URL: {url}")
                res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
                res.raise_for_status()
                
                with zipfile.ZipFile(io.BytesIO(res.content)) as zf:
                    mst_filename = zf.namelist()[0]
                    with zf.open(mst_filename) as mst_file:
                        mst_data = mst_file.read()
                
                logger.info(f"성공: {market.upper()} 마스터 파일 크기: {len(mst_data)} bytes")

                for line in mst_data.splitlines():
                    if not line: continue
                    
                    decoded_line = line.decode('cp949')
                    
                    # 이제 안전하게 문자열을 자를 수 있습니다.
                    stock_code = decoded_line[0:20].strip()
                    stock_name = decoded_line[48:92].strip()
                    
                    if stock_code.startswith('A'):
                        stock_list.append(StockItem(code=stock_code, name=stock_name))

            except Exception as e:
                logger.error(f"❌ {market.upper()} 마스터 파일 처리 중 에러: {e}", exc_info=True)
        
        logger.info(f"✅ 최종 파싱 완료. 총 {len(stock_list)}개 국내 종목 로드.")
        return stock_list

    def search_korean_stocks(self, query: str) -> List[StockItem]:
        if not query or not self.korean_stock_list: return []
        query_lower = query.lower()
        results = [
            stock for stock in self.korean_stock_list
            if query_lower in stock.name.lower() or query.upper() in stock.code.upper()
        ][:20]
        return results

    def search_overseas_stocks(self, query: str) -> List[StockItem]:
        if not query.isascii(): return []
        path = "/uapi/overseas-price/v1/quotations/inquire-search"
        url = f"{self.BASE_URL}{path}"
        markets = ["NASD", "NYSE", "AMEX"]
        all_results: List[StockItem] = []
        for market in markets:
            headers = self._get_auth_headers("HHDFS76410000")
            params = {"P_NP_ETC_INFO": query.upper(), "OVRS_EXCG_CD": market}
            try:
                res = requests.get(url, headers=headers, params=params)
                if res.status_code != 200: continue
                response_data = OverseasStockSearchResponse(**res.json())
                if response_data.rt_cd == '0':
                    existing_tickers = {item.code for item in all_results}
                    for item in response_data.output:
                        if item.ticker not in existing_tickers:
                            all_results.append(StockItem(code=item.ticker, name=item.name))
            except Exception:
                continue
        return all_results
