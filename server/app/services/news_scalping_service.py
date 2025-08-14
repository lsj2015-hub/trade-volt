import logging
import re
from typing import List, Dict, Any
from starlette.concurrency import run_in_threadpool
import requests
from datetime import datetime, timedelta, timezone
import zipfile
import pandas as pd
import io
import xml.etree.ElementTree as ET
import asyncio
import pytz
import openai
import html

from ..config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}

class NewsScalpingService:
    def __init__(self):
        self.naver_client_id = settings.NAVER_CLIENT_ID
        self.naver_client_secret = settings.NAVER_CLIENT_SECRET
        self.dart_api_key = settings.DART_API_KEY
        self.unified_stock_map: Dict[str, Dict[str, str]] = {}
        self.openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logging.getLogger("requests").setLevel(logging.WARNING)
        logger.info("✅ NewsScalpingService 초기화 (키워드/시간 필터링 모드).")

    # ✅ --- 기업 목록 로드 로직 복원 ---
    async def load_corp_data(self):
        if self.unified_stock_map: return
        try:
            logger.info("--- [단계 1: 기업 목록 생성] ---")
            krx_df = await run_in_threadpool(self._get_krx_stock_list)
            dart_df = await run_in_threadpool(self._get_dart_corp_list_from_file)
            self.unified_stock_map = self._create_unified_stock_map(krx_df, dart_df)
            logger.info(f"✅ KRX({len(krx_df)})/DART({len(dart_df)}) 통합 -> 최종 {len(self.unified_stock_map)}개 기업 맵 생성 완료.")
        except Exception as e:
            logger.error(f"❌ 기업 목록 데이터 로드 중 오류: {e}", exc_info=True)

    def _get_krx_stock_list(self) -> pd.DataFrame:
        response = requests.get('http://kind.krx.co.kr/corpgeneral/corpList.do?method=download', headers=HEADERS, timeout=30.0)
        response.raise_for_status()
        df = pd.read_html(io.BytesIO(response.content), header=0, encoding='euc-kr')[0]
        df['종목코드'] = df['종목코드'].astype(str).str.zfill(6)
        return df[['회사명', '종목코드']]
    
    def _get_dart_corp_list_from_file(self) -> pd.DataFrame:
        url = "https://opendart.fss.or.kr/api/corpCode.xml"
        params = {"crtfc_key": self.dart_api_key}
        response = requests.get(url, params=params, timeout=60.0, headers=HEADERS)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
            xml_content = zf.read('CORPCODE.xml')
        root = ET.fromstring(xml_content)
        data = []
        for item in root.findall('.//list'):
            data.append({
                'corp_code': item.find('corp_code').text,
                'corp_name': item.find('corp_name').text,
                'stock_code': item.find('stock_code').text.strip() if item.find('stock_code') is not None and item.find('stock_code').text is not None else None,
            })
        return pd.DataFrame(data)
    
    def _create_unified_stock_map(self, krx_df: pd.DataFrame, dart_df: pd.DataFrame) -> Dict[str, Dict[str, str]]:
        dart_df.rename(columns={'corp_name': '회사명', 'stock_code': '종목코드'}, inplace=True)
        # krx_df를 기준으로 dart_df의 'corp_code'를 병합
        merged_df = pd.merge(krx_df, dart_df[['회사명', 'corp_code']], on='회사명', how='left')
        merged_df.dropna(subset=['corp_code'], inplace=True) # corp_code가 없는 데이터는 제외
        
        clean_name = lambda name: re.sub(r'\(주\)|주식회사|\(유\)|유한회사', '', name).strip()
        merged_df['회사명'] = merged_df['회사명'].apply(clean_name)
        merged_df.drop_duplicates(subset=['회사명'], keep='first', inplace=True)
        
        # 최종 맵: {회사명: {'code': 종목코드, 'corp_code': DART고유번호}}
        return {row['회사명']: {'code': row['종목코드'], 'corp_code': row['corp_code']} for _, row in merged_df.iterrows()}

    # --- 전체 로직 실행 함수 ---
    async def get_news_candidates(self, time_limit_seconds: int, display_count: int) -> Dict[str, Any]:
        
        # --- 1. 네이버 뉴스 검색 ---
        logger.info("\n--- [단계 2.1: 네이버 뉴스 검색] ---")
        raw_news_items = await run_in_threadpool(self._search_naver_news, '경제', display_count)
        if not raw_news_items:
            return {"message": "네이버 뉴스 API에서 뉴스를 가져오지 못했습니다.", "raw_naver_news": [], "filtered_news": [], "dart_verified_news": []}
        
        # 프론트엔드 전달용 데이터 가공 (1단계)
        raw_news_for_display = [{
            "news_title": re.sub('<[^<]+?>', '', item.get("title", "")), 
            "news_published": item.get("pubDate"),
            "news_link": item.get("originallink")
        } for item in raw_news_items]

        # --- 2. 키워드/시간 필터링 및 회사명 추출 ---
        logger.info("\n--- [단계 2.2: 키워드/시간/회사명 필터링] ---")
        positive_keywords = ["수주", "호실적", "실적개선", "흑자전환", "영업이익 증가", "매출 증가", "역대 최대", "사상 최대 실적", "분기 최대 실적", "실적 서프라이즈", "턴어라운드", "공급 계약", "장기 계약", "MOU 체결", "파트너십", "유통망 확보", "정부 지원", "정책 수혜", "규제 완화", "국책 과제 선정", "R&D 지원", "신기술 공개", "특허 등록", "글로벌 인증", "양산 성공", "FDA 승인", "수출 확대", "글로벌 진출", "자사주 매입", "배당 확대", "경영권 분쟁 해소", "경영진 교체", "유상증자 성공", "투자 유치", "IPO 기대감", "스팩 합병", "목표가 상향", "인수합병", "계열사 편입", "구조적 성장"]
        keyword_filtered_news = self._filter_news_by_keywords(raw_news_items, positive_keywords)
        time_filtered_news = self._filter_news_by_time(keyword_filtered_news, time_limit_seconds)
        
        # 프론트엔드 전달용 데이터 가공 (2단계)
        candidates = self._extract_candidates_from_news(time_filtered_news)
        
        # --- 3. DART 공시 검증 ---
        logger.info("\n--- [단계 3: DART 공시 검증] ---")
        tasks = [self._verify_news_with_dart(candidate) for candidate in candidates]
        verified_results = await asyncio.gather(*tasks)
        
        # 프론트엔드 전달용 데이터 가공 (3단계)
        dart_verified_news = []
        for res in verified_results:
            if res.get("disclosure") and res["disclosure"].get("url"):
                dart_verified_news.append({
                    "stock_name": res["stock_name"],
                    "stock_code": res["stock_code"],
                    "news_title": res["news_title"],
                    "news_link": res["news_link"],
                    "news_published": res["news_published"],
                    "disclosure_report_name": res["disclosure"]["report_name"],
                    "disclosure_url": res["disclosure"]["url"],
                })

        message = f"뉴스 {len(raw_news_items)}개 -> 필터링 후보 {len(candidates)}개 -> DART 검증 통과 {len(dart_verified_news)}개"
        return {
            "message": message,
            "raw_naver_news": raw_news_for_display,
            "filtered_news": candidates,
            "dart_verified_news": dart_verified_news
        }

    def _search_naver_news(self, query: str, display_count: int) -> List[Dict]:
        """'최신순(date)' 정렬로 뉴스를 가져옵니다."""
        naver_headers = {**HEADERS, "X-Naver-Client-Id": self.naver_client_id, "X-Naver-Client-Secret": self.naver_client_secret}
        params = {"query": query, "display": display_count, "sort": "date"}
        logger.info(f"네이버 뉴스 API 요청: params={params}")
        
        response = requests.get("https://openapi.naver.com/v1/search/news.json", headers=naver_headers, params=params, timeout=20.0)
        response.raise_for_status()
        all_items = response.json().get("items", [])
        logger.info(f"네이버 뉴스 수신 완료: 총 {len(all_items)}개")
        return all_items
    
    def _clean_text(self, text: str) -> str:
        """HTML 태그 제거와 엔티티 디코딩을 모두 수행하는 헬퍼 함수"""
        clean_text = re.sub('<[^<]+?>', '', text)
        clean_text = html.unescape(clean_text)
        return clean_text
        
    def _filter_news_by_keywords(self, news_items: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        HTML 태그를 먼저 제거한 후, 깨끗한 텍스트에서 positive_keywords를 찾아 뉴스를 필터링합니다.
        """
        filtered = []
        for item in news_items:
            try:
                # title과 description에서 각각 HTML 태그를 제거합니다.
                clean_title = self._clean_text(item.get("title", ""))
                clean_description = self._clean_text(item.get("description", ""))
                content = clean_title + " " + clean_description
                
                # 깨끗한 content에서 키워드를 찾습니다.
                if any(keyword in content for keyword in keywords):
                    filtered.append(item)
            except Exception:
                continue # 혹시 모를 오류가 발생해도 건너뜁니다.
                
        logger.info(f"키워드 필터링: {len(news_items)}개 -> {len(filtered)}개")
        return filtered

    def _filter_news_by_time(self, news_items: List[Dict], time_limit_seconds: int) -> List[Dict]:
        """필터링된 뉴스 리스트에 시간 제한을 적용합니다."""
        now_utc = datetime.now(timezone.utc)
        time_limit = timedelta(seconds=time_limit_seconds)
        
        final_filtered = []
        for item in news_items:
            try:
                published_time_aware = datetime.strptime(item["pubDate"], '%a, %d %b %Y %H:%M:%S %z')
                if (now_utc - published_time_aware) <= time_limit:
                    item['news_title'] = self._clean_text(item.get("title", "")),
                    item['news_link'] = item.get("originallink")
                    item['news_published'] = item.get("pubDate")
                    final_filtered.append(item)
            except (ValueError, KeyError):
                continue
        
        logger.info(f"시간 필터링: {len(news_items)}개 -> {len(final_filtered)}개")
        return final_filtered
    
    def _extract_candidates_from_news(self, news_items: List[Dict]) -> List[Dict]:
            """
            필터링된 뉴스 리스트 각각에 대해, 가장 먼저 언급된 회사명을 찾아 정보를 추가합니다.
            하나의 뉴스에서는 단 하나의 회사만 추출합니다.
            """
            candidates = []
            for item in news_items:
                content = item.get("news_title", "")
                for stock_name, stock_info in self.unified_stock_map.items():
                    if stock_name in content:
                        candidates.append({
                            "stock_name": stock_name,
                            "stock_code": stock_info['code'],
                            "corp_code": stock_info['corp_code'],
                            "news_title": item["news_title"],
                            "news_link": item["news_link"],
                            "news_published": item["news_published"]
                        })
                        break 
            logger.info(f"뉴스 {len(news_items)}개 -> 회사명 매칭 -> 최종 {len(candidates)}개 뉴스 후보 추출")
            return candidates
    
    # ✅ --- DART 공시 검증 함수 추가 ---
    async def _verify_news_with_dart(self, candidate: Dict) -> Dict:
        """단일 후보에 대해 DART 공시를 검증하고 결과를 후보 정보에 추가합니다."""
        logger.info(f"-> '{candidate['stock_name']}' 공시 검증 시작...")
        disclosure_result = await run_in_threadpool(self._check_disclosure_for_stock, candidate["corp_code"])
        candidate["disclosure"] = disclosure_result
        return candidate

    def _check_disclosure_for_stock(self, corp_code: str) -> Dict[str, Any]:
        """DART에서 기업 고유번호로 최근 3일치 공시를 찾아 첫 번째 공시를 반환합니다."""
        url = "https://opendart.fss.or.kr/api/list.json"
        now_in_seoul = datetime.now(pytz.timezone('Asia/Seoul'))
        bgn_de = (now_in_seoul - timedelta(days=3)).strftime('%Y%m%d')
        end_de = now_in_seoul.strftime('%Y%m%d')

        for page_no in range(1, 11):
            params = {"crtfc_key": self.dart_api_key, "corp_code": corp_code, "bgn_de": bgn_de, "end_de": end_de, "pblntf_ty": "A", "page_no": page_no, "page_count": 100}
            response = requests.get(url, params=params, timeout=10.0, headers=HEADERS)
            response.raise_for_status()
            data = response.json()
            if data.get('status') == '013': break
            if data.get('status') != '000': return {"report_name": f"DART API 오류: {data.get('message')}", "url": None}
            disclosures = data.get('list', [])
            if disclosures:
                first_disclosure = disclosures[0]
                report_name = first_disclosure.get('report_nm', '')
                logger.info(f"'{corp_code}' 공시 찾음 ({page_no} 페이지): '{report_name}'")
                return {"report_name": report_name, "url": f"http://dart.fss.or.kr/dsaf001/main.do?rcpNo={first_disclosure['rcept_no']}"}
        
        logger.info(f"'{corp_code}': 최근 3일 내 공시(최대 10페이지)에서 내용 없음.")
        return {"report_name": "최근 3일 내 공시 없음", "url": None}