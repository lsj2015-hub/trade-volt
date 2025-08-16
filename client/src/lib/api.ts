import {
  StockProfile,
  FinancialSummary,
  InvestmentMetrics,
  MarketData,
  AnalystRecommendations,
  Officer,
  FinancialStatementData,
  StockHistoryApiResponse,
  StockHistoryData,
  StockOverviewData,
  StockItem,
  Portfolio,
  TransactionData,
  HoldingItem,
} from '@/types/stock';
import {
  StockNews,
  SectorGroups,
  SectorTickerResponse,
  SectorAnalysisRequest,
  SectorAnalysisResponse,
  PerformanceAnalysisRequest,
  PerformanceAnalysisResponse,
  StockComparisonRequest,
  StockComparisonResponse,
  TradingVolumeRequest,
  TradingVolumeResponse,
  NetPurchaseRequest,
  NetPurchaseResponse,
  FluctuationAnalysisRequest,
  FluctuationAnalysisResponse,
} from '../types/common';
import { NewsSearchResponse } from '@/types/strategy';

// 모든 API 요청에 대한 기본 URL
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// API 에러를 위한 커스텀 클래스
export class APIError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

interface TranslationResponse {
  translated_text: string;
}

// 모든 API 함수에 일관된 에러 핸들링 적용
const fetchAPI = async <T>(
  url: string,
  options: RequestInit = {}
): Promise<T> => {
  try {
    // 🌟 fetch 옵션에 기본 헤더를 추가하여 모든 요청에 적용될 수 있도록 개선
    const defaultHeaders = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const response = await fetch(url, { ...options, headers: defaultHeaders });

    if (!response.ok) {
      const errorData = await response
        .json()
        .catch(() => ({ detail: '서버 응답 오류' }));
      throw new APIError(
        errorData.detail || '서버에서 오류가 발생했습니다.',
        response.status
      );
    }
    // 응답 본문이 없는 경우(e.g., 204 No Content)를 대비
    const text = await response.text();
    return text ? (JSON.parse(text) as T) : ({} as T);
  } catch (error) {
    if (error instanceof APIError) throw error;
    console.error(`API 호출 실패: ${url}`, error);
    throw new Error('서버와 통신할 수 없습니다. 네트워크 연결을 확인해주세요.');
  }
};

// 통합 정보 조회
export const getStockOverview = (symbol: string): Promise<StockOverviewData> =>
  fetchAPI(`${API_BASE_URL}/api/stock/${symbol}/overview`);

// 주식 프로필 정보 조회
export const getStockProfile = (symbol: string): Promise<StockProfile> =>
  fetchAPI(`${API_BASE_URL}/api/stock/${symbol}/profile`);

// 재무 요약 정보 조회
export const getFinancialSummary = (
  symbol: string
): Promise<FinancialSummary> =>
  fetchAPI(`${API_BASE_URL}/api/stock/${symbol}/financial-summary`);

// 투자 지표 조회
export const getInvestmentMetrics = (
  symbol: string
): Promise<InvestmentMetrics> =>
  fetchAPI(`${API_BASE_URL}/api/stock/${symbol}/metrics`);

// 시장 데이터 조회
export const getMarketData = (symbol: string): Promise<MarketData> =>
  fetchAPI(`${API_BASE_URL}/api/stock/${symbol}/market-data`);

// 분석가 추천 정보 조회
export const getAnalystRecommendations = (
  symbol: string
): Promise<AnalystRecommendations> =>
  fetchAPI(`${API_BASE_URL}/api/stock/${symbol}/recommendations`);

// 임원 정보 조회
export const getStockOfficers = (
  symbol: string
): Promise<{ officers: Officer[] }> =>
  fetchAPI(`${API_BASE_URL}/api/stock/${symbol}/officers`);

// 재무제표 조회
export const getFinancialStatement = (
  symbol: string,
  statementType: 'income' | 'balance' | 'cashflow'
): Promise<FinancialStatementData> =>
  fetchAPI(`${API_BASE_URL}/api/stock/${symbol}/financials/${statementType}`);

// 주가 히스토리 조회
export const getStockHistory = (
  symbol: string,
  startDate: string,
  endDate: string
): Promise<StockHistoryApiResponse> =>
  fetchAPI(
    `${API_BASE_URL}/api/stock/${symbol}/history?start_date=${startDate}&end_date=${endDate}`
  );

// 야후 RSS 뉴스 조회
export const fetchStockNews = async (
  symbol: string,
  limit = 10
): Promise<StockNews[]> => {
  const result = await fetchAPI<{ news: StockNews[] }>(
    `${API_BASE_URL}/api/stock/${symbol}/news?limit=${limit}`
  );
  return result.news;
};

// 텍스트 번역
export const getTranslation = async (text: string): Promise<string> => {
  const result = await fetchAPI<TranslationResponse>(
    `${API_BASE_URL}/api/util/translate`,
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text }),
    }
  );
  return result.translated_text;
};

// AI에게 질문
export const askAi = (
  symbol: string,
  question: string,
  financialData: FinancialStatementData | null,
  historyData: StockHistoryData[] | null,
  newsData: StockNews[] | null
): Promise<{ response: string }> => {
  return fetchAPI(`${API_BASE_URL}/api/ai/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      symbol,
      question,
      financialData: financialData
        ? JSON.stringify(financialData)
        : '데이터 없음',
      historyData: historyData ? JSON.stringify(historyData) : '데이터 없음',
      newsData: newsData?.map((n) => ({
        title: n.title,
        summary: n.summary,
        url: n.url,
        publishedDate: n.publishedDate,
        source: n.source,
      })),
    }),
  });
};

// --- ✅ 섹터 분석 API 함수들 ---

/**
 * 모든 섹터 그룹 정보를 가져옵니다.
 */
export const getSectorGroups = (): Promise<SectorGroups> => {
  return fetchAPI(`${API_BASE_URL}/api/sectors/groups`);
};

/**
 * 특정 시장과 그룹에 속한 티커 목록을 가져옵니다.
 * @param market - 'KOSPI' 또는 'KOSDAQ'
 * @param group - 섹터 그룹 이름
 */
export const getSectorTickers = (
  market: string,
  group: string
): Promise<SectorTickerResponse> => {
  return fetchAPI(
    `${API_BASE_URL}/api/sectors/tickers?market=${market}&group=${encodeURIComponent(
      group
    )}`
  );
};

/**
 * 선택된 섹터들의 수익률을 분석합니다.
 * @param requestData - 시작일, 종료일, 티커 목록을 포함하는 객체
 */
export const analyzeSectors = (
  requestData: SectorAnalysisRequest
): Promise<SectorAnalysisResponse> => {
  return fetchAPI(`${API_BASE_URL}/api/sectors/analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
};

/**
 * 시장 성과 분석을 요청합니다.
 * @param requestData - 국가, 시장, 기간, 종목 수를 포함하는 객체
 */
export const analyzePerformance = (
  requestData: PerformanceAnalysisRequest
): Promise<PerformanceAnalysisResponse> => {
  return fetchAPI(`${API_BASE_URL}/api/performance/analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
};

/**
 * 여러 주식의 수익률을 비교 분석합니다.
 * @param requestData - 티커 목록, 시작일, 종료일을 포함하는 객체
 */
export const compareStocks = (
  requestData: StockComparisonRequest
): Promise<StockComparisonResponse> => {
  return fetchAPI(`${API_BASE_URL}/api/stock/compare`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
};

// --- ✅ 투자자별 매매동향 API 함수들 ---
export const getTradingVolume = (
  requestData: TradingVolumeRequest
): Promise<TradingVolumeResponse> => {
  return fetchAPI(`${API_BASE_URL}/api/krx/trading-volume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
};

export const getTopNetPurchases = (
  requestData: NetPurchaseRequest
): Promise<NetPurchaseResponse> => {
  return fetchAPI(`${API_BASE_URL}/api/krx/net-purchases`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
};

/**
 * @description 변동성 종목 분석을 요청합니다.
 * @param requestData
 */
export const analyzeFluctuations = (
  requestData: FluctuationAnalysisRequest
): Promise<FluctuationAnalysisResponse> => {
  return fetchAPI(`${API_BASE_URL}/api/stocks/fluctuation-analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestData),
  });
};

export const searchNewsCandidates = (
  timeLimitSeconds: number,
  displayCount: number
): Promise<NewsSearchResponse> => {
  return fetchAPI(`${API_BASE_URL}/api/strategy/news-feed-search`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      time_limit_seconds: timeLimitSeconds,
      display_count: displayCount,
    }),
  });
};

/**
 * 주식 종목을 검색하는 함수 (새로 추가될 수 있는 함수 예시)
 * @param query 검색어
 * @param market 검색할 시장 (KOR, OVERSEAS 등)
 */
export const searchStocks = (query: string, market: string): Promise<StockItem[]> => {
  if (query.trim().length < 2) {
    return Promise.resolve([]);
  }
  const url = `${API_BASE_URL}/api/search-stocks?query=${encodeURIComponent(
    query
  )}&market=${market}`;
  return fetchAPI<StockItem[]>(url);
};

/**
 * 특정 종목의 현재가를 조회하는 API
 * @param market "KOR" | "OVERSEAS"
 * @param stockCode 종목코드 또는 Ticker
 */
export const getStockPrice = async (
  market: string,
  stockCode: string
): Promise<{ price: string }> => {
  const url = `${API_BASE_URL}/api/stocks/price/${market}/${stockCode}`;
  return fetchAPI<{ price: string }>(url);
};

/**
 * 특정 종목의 보유 현황을 조회하는 API
 * @param stockCode 종목 코드 또는 Ticker
 */
export const getHolding = async (
  stockCode: string
): Promise<HoldingItem | null> => {
  const url = `${API_BASE_URL}/api/portfolio/${stockCode}`;
  try {
    const response = await fetchAPI<HoldingItem>(url);
    // FastAPI에서 null을 반환하면 빈 객체가 될 수 있으므로, 키 존재 여부로 실제 데이터 확인
    return response && response.stock_code ? response : null;
  } catch (error) {
    if (error instanceof APIError && error.status === 404) {
      return null;
    }
    throw error;
  }
};

/**
 * 전체 포트폴리오 정보를 조회하는 API
 */
export const getPortfolio = async (): Promise<Portfolio> => {
  const url = `${API_BASE_URL}/api/portfolio`;
  return fetchAPI<Portfolio>(url);
};

/**
 * 새로운 거래(매수/매도)를 기록하는 API
 * @param tradeData 거래 정보
 */
export const postTrade = async (
  tradeData: TransactionData
): Promise<TransactionData> => {
  const url = `${API_BASE_URL}/api/portfolio/trade`;
  return fetchAPI<TransactionData>(url, {
    method: 'POST',
    body: JSON.stringify(tradeData),
  });
};
