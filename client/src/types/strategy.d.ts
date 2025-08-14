// 1단계: 네이버 API 원본 뉴스
export interface RawNewsItem {
  news_title: string;
  news_published: string;
  news_link: str;
}

// 2단계: 키워드/시간 필터링 및 회사명 추출 완료
export interface FilteredNewsItem {
  stock_name: string;
  stock_code: string;
  news_title: string;
  news_link: string;
  news_published: string;
}

// 3단계: DART 공시 검증 완료
export interface VerifiedNewsItem extends FilteredNewsItem {
  disclosure_report_name: string;
  disclosure_url: string;
}

// 최종 응답 타입 (모든 단계를 포함)
export interface NewsSearchResponse {
  message: string;
  raw_naver_news: RawNewsItem[];
  filtered_news: FilteredNewsItem[];
  dart_verified_news: VerifiedNewsItem[];
}
