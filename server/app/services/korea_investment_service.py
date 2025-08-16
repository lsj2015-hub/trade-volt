import pandas as pd
import logging
import os
import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.config import settings
from app.schemas import StockItem, TokenData

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KoreaInvestmentService:
    def __init__(self, data_path: str = "data"):
        self.APP_KEY = settings.KIS_APP_KEY
        self.APP_SECRET = settings.KIS_APP_SECRET
        self.BASE_URL = settings.KIS_BASE_URL
        self._token_data_path = "kis_token.json"
        self.data_path = data_path
        self.korean_df = pd.DataFrame()
        self.overseas_df = pd.DataFrame()
        
        self._load_all_stocks_from_files()
        
        logger.info(f"✅ KIS Service initializing for REAL server: {self.BASE_URL}")

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

    def _load_all_stocks_from_files(self):
        logger.info("--- 로컬 엑셀 파일에서 주식 정보 로드를 시작합니다. ---")
        
        kospi_df = self._load_file_to_df_by_position('kospi_code.xlsx')
        kosdaq_df = self._load_file_to_df_by_position('kosdaq_code.xlsx')
        self.korean_df = pd.concat([kospi_df, kosdaq_df], ignore_index=True)
        logger.info(f"✅ 총 {len(self.korean_df)}개의 국내 주식 정보 통합 완료.")
        
        self.overseas_df = self._load_file_to_df_by_position('overseas_stock_code.xlsx')
        logger.info(f"✅ 총 {len(self.overseas_df)}개의 해외 주식 정보 로드 완료.")

    def _load_file_to_df_by_position(self, file_name: str) -> pd.DataFrame:
        file_path = os.path.join(self.data_path, file_name)
        if not os.path.exists(file_path):
            logger.error(f"❌ '{file_name}' 파일이 존재하지 않습니다. `server/data` 폴더를 확인해주세요.")
            return pd.DataFrame()
        
        try:
            df = pd.read_excel(file_path, dtype=str, header=0)
            if len(df.columns) >= 2:
                df = df.iloc[:, [0, 1]]
                df.columns = ['code', 'name']
                df.dropna(inplace=True)
                logger.info(f"✅ '{file_name}' 파일에서 첫 두 컬럼을 사용하여 {len(df)}개 종목 로드 완료.")
                return df
            else:
                logger.error(f"❌ '{file_name}' 파일에 최소 2개 이상의 컬럼이 필요합니다.")
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"❌ '{file_name}' 파일 로드 중 에러 발생: {e}", exc_info=True)
        return pd.DataFrame()

    def search_korean_stocks(self, query: str) -> List[StockItem]:
        if not query or self.korean_df.empty: return []
        mask = (self.korean_df['name'].str.contains(query, case=False, na=False)) | \
               (self.korean_df['code'].str.contains(query, case=False, na=False))
        results_df = self.korean_df[mask].head(20)
        return [StockItem(**row) for row in results_df.to_dict(orient='records')]

    def search_overseas_stocks(self, query: str) -> List[StockItem]:
        if not query or self.overseas_df.empty: return []
        mask = (self.overseas_df['name'].str.contains(query, case=False, na=False)) | \
               (self.overseas_df['code'].str.contains(query, case=False, na=False))
        results_df = self.overseas_df[mask].head(20)
        return [StockItem(**row) for row in results_df.to_dict(orient='records')]
        
    def get_latest_close_price(self, market: str, stock_code: str, base_date: datetime) -> Optional[str]:
        """
        주어진 기준일(base_date)부터 과거로 최대 10일간 탐색하여
        가장 최근의 유효한 종가를 찾아 반환합니다. (휴일/주말 처리)
        """
        for i in range(10): # 최대 10일 전까지 조회
            query_date = (base_date - timedelta(days=i)).strftime('%Y%m%d')
            
            path, tr_id, params = "", "", {}
            
            if market == 'KOR':
                path = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
                tr_id = "FHKST03010100"
                numeric_code = stock_code[1:] if stock_code.startswith('A') else stock_code
                params = {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": numeric_code, "FID_INPUT_DATE_1": query_date, "FID_INPUT_DATE_2": query_date, "FID_PERIOD_DIV_CODE": "D", "FID_ORG_ADJ_PRC": "1"}
            elif market == 'OVERSEAS':
                path = "/uapi/overseas-price/v1/quotations/dailyprice"
                tr_id = "HHDFS76240000"
                # 해외주식은 모든 주요 거래소를 순회하며 조회
                for excd in ["NASD", "NYSE", "AMEX"]:
                    params = {"AUTH": "", "EXCD": excd, "SYMB": stock_code, "GUBN": "0", "BYMD": query_date, "MODP": "1"}
                    price = self._request_price(path, tr_id, params, market)
                    if price: return price
                continue # 다음 날짜로
            else:
                return None

            price = self._request_price(path, tr_id, params, market)
            if price: return price
            
            time.sleep(0.11) # Rate Limit 방지를 위해 다음 날짜 조회 전 잠시 대기

        logger.warning(f"10일간의 조회 시도 후에도 {stock_code}의 가격 정보를 찾지 못했습니다.")
        return None

    def _request_price(self, path: str, tr_id: str, params: dict, market: str) -> Optional[str]:
        """KIS API에 가격을 요청하고 결과를 파싱하는 내부 헬퍼 함수"""
        url = f"{self.BASE_URL}{path}"
        headers = self._get_auth_headers(tr_id)
        try:
            res = requests.get(url, headers=headers, params=params)
            res.raise_for_status()
            data = res.json()
            
            output_key = 'output2' if market == 'KOR' else 'output1'
            price_key = 'stck_clpr' if market == 'KOR' else 'clos'

            if data.get('rt_cd') == '0' and output_key in data and len(data[output_key]) > 0:
                price = data[output_key][0].get(price_key)
                if price and float(price.strip()) > 0:
                    return price.strip()
        except Exception:
            return None
        return None

    def get_current_price(self, market: str, stock_code: str) -> Optional[str]:
        # '현재가'는 오늘을 기준으로 가장 최근 영업일의 종가를 가져옵니다.
        return self.get_latest_close_price(market, stock_code, datetime.now())

    def get_previous_day_price(self, market: str, stock_code: str) -> Optional[str]:
        # '전일가'는 어제를 기준으로 가장 최근 영업일의 종가를 가져옵니다.
        return self.get_latest_close_price(market, stock_code, datetime.now() - timedelta(days=1))