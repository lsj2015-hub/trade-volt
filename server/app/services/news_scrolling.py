import logging
import re
from typing import List, Dict, Any
from starlette.concurrency import run_in_threadpool
import requests
from datetime import datetime, timedelta, timezone

from ..config import settings

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
}

class NewsScalpingService:
    def __init__(self):
        self.naver_client_id = settings.NAVER_CLIENT_ID
        self.naver_client_secret = settings.NAVER_CLIENT_SECRET
        logging.getLogger("requests").setLevel(logging.WARNING)
        logger.info("✅ NewsScalpingService 초기화 (키워드/시간 필터링 모드).")

    async def get_live_naver_news(self, time_limit_seconds: int, display_count: int) -> Dict[str, Any]:
        logger.info("\n--- [뉴스 검색 및 필터링 시작] ---")
        
        # 1. 넓은 범위의 검색어로 최신 뉴스를 먼저 가져옵니다.
        raw_news_items = await run_in_threadpool(self._search_naver_news, '경제', display_count)
        
        if not raw_news_items:
            message = "네이버 뉴스 API에서 뉴스를 가져오지 못했습니다."
            return {"message": message, "data": []}

        # 2. 가져온 뉴스를 positive_keywords로 필터링합니다.
        positive_keywords = [
            "수주", "호실적", "실적개선", "흑자전환", "영업이익 증가", "매출 증가", "사상 최대 실적",
            "분기 최대 실적", "실적 서프라이즈", "턴어라운드", "공급 계약", "장기 계약", "MOU 체결",
            "파트너십", "유통망 확보", "정부 지원", "정책 수혜", "규제 완화", "국책 과제 선정", "R&D 지원",
            "신기술 공개", "특허 등록", "글로벌 인증", "양산 성공", "FDA 승인", "수출 확대", "글로벌 진출", 
            "자사주 매입", "배당 확대", "경영권 분쟁 해소", "경영진 교체", "유상증자 성공", "투자 유치", 
            "IPO 기대감", "스팩 합병", "목표가 상향", "인수합병", "계열사 편입", "구조적 성장", "산업"
        ]
        
        keyword_filtered_news = self._filter_news_by_keywords(raw_news_items, positive_keywords)
        
        # 3. 키워드로 필터링된 뉴스를 대상으로 시간 필터링을 적용합니다.
        time_filtered_news = self._filter_news_by_time(keyword_filtered_news, time_limit_seconds)

        if not time_filtered_news:
            message = "필터링 조건에 맞는 최신 뉴스를 찾지 못했습니다."
            logger.info(f"--- [결과] --- \n{message}")
            return {"message": message, "data": []}
        
        message = f"성공적으로 {len(time_filtered_news)}개의 최신 뉴스를 필터링했습니다."
        logger.info(f"--- [결과] --- \n{message}")
        
        return {"message": message, "data": time_filtered_news}

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
        
    def _filter_news_by_keywords(self, news_items: List[Dict], keywords: List[str]) -> List[Dict]:
        """
        [Jupyter Notebook 로직 100% 반영] HTML 태그를 먼저 제거한 후,
        깨끗한 텍스트에서 positive_keywords를 찾아 뉴스를 필터링합니다.
        """
        filtered = []
        for item in news_items:
            try:
                # --- ✅ [핵심 수정] Jupyter Notebook과 동일하게 HTML 태그를 먼저 제거합니다. ---
                # 1. title과 description에서 각각 HTML 태그를 제거합니다.
                clean_title = re.sub('<[^<]+?>', '', item.get("title", ""))
                clean_description = re.sub('<[^<]+?>', '', item.get("description", ""))
                
                # 2. 깨끗해진 텍스트를 합쳐서 content를 만듭니다.
                content = clean_title + " " + clean_description
                
                # 3. 깨끗한 content에서 키워드를 찾습니다.
                if any(keyword in content for keyword in keywords):
                    # 필터링을 통과한 뉴스 아이템 원본을 추가합니다.
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
                    final_filtered.append({
                        "news_title": re.sub('<[^<]+?>', '', item.get("title", "")),
                        "news_link": item.get("link"),
                        "news_published": item.get("pubDate")
                    })
            except (ValueError, KeyError):
                continue
        
        logger.info(f"시간 필터링: {len(news_items)}개 -> {len(final_filtered)}개")
        return final_filtered
