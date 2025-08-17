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
    const response = await fetch(url, options);

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      const errorMessage =
        errorData?.detail ||
        `서버에서 오류가 발생했습니다. (상태 코드: ${response.status})`;
      throw new APIError(errorMessage, response.status);
    }
    return response.json();
  } catch (error) {
    if (error instanceof APIError) {
      throw error;
    }
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
/**
 * 시장 성과 분석을 요청합니다. (임시 데이터 반환)
 * @param requestData - 국가, 시장, 기간, 종목 수를 포함하는 객체
 */
export const analyzePerformance = async (
  requestData: PerformanceAnalysisRequest
): Promise<PerformanceAnalysisResponse> => {
  // 서버 호출 대신 임시 데이터 반환
  await new Promise((resolve) => setTimeout(resolve, 1500)); // 로딩 시뮬레이션

  console.log('Performance analysis request:', requestData);

  // 시장별 다른 데이터 반환
  const mockData: PerformanceAnalysisResponse = {
    top_performers: generateMockPerformers(
      requestData.market,
      'top',
      requestData.top_n
    ),
    bottom_performers: generateMockPerformers(
      requestData.market,
      'bottom',
      requestData.top_n
    ),
    total_analyzed: Math.floor(Math.random() * 500) + 200,
    analysis_period: `${requestData.start_date} ~ ${requestData.end_date}`,
    market: requestData.market,
    cache_hit: false,
    processing_time: Math.random() * 3 + 1,
  };

  return mockData;
};

// 임시 데이터 생성 함수
function generateMockPerformers(
  market: string,
  type: 'top' | 'bottom',
  count: number
) {
  const performers = [];

  // 시장별 종목 템플릿
  const stockTemplates = {
    KOSPI: [
      { ticker: '005930', name: '삼성전자' },
      { ticker: '000660', name: 'SK하이닉스' },
      { ticker: '035420', name: 'NAVER' },
      { ticker: '051910', name: 'LG화학' },
      { ticker: '006400', name: '삼성SDI' },
      { ticker: '207940', name: '삼성바이오로직스' },
      { ticker: '068270', name: '셀트리온' },
      { ticker: '035720', name: '카카오' },
      { ticker: '003670', name: '포스코홀딩스' },
      { ticker: '028260', name: '삼성물산' },
    ],
    KOSDAQ: [
      { ticker: '293490', name: '카카오게임즈' },
      { ticker: '086900', name: '메디톡스' },
      { ticker: '196170', name: '알테오젠' },
      { ticker: '361610', name: 'SK아이이테크놀로지' },
      { ticker: '348210', name: '넥스틴' },
      { ticker: '393890', name: '더존비즈온' },
      { ticker: '263750', name: '펄어비스' },
      { ticker: '357780', name: '솔브레인' },
      { ticker: '140860', name: '파크시스템스' },
      { ticker: '225570', name: '넥슨게임즈' },
    ],
    NASDAQ: [
      { ticker: 'AAPL', name: 'Apple Inc.' },
      { ticker: 'MSFT', name: 'Microsoft Corporation' },
      { ticker: 'GOOGL', name: 'Alphabet Inc.' },
      { ticker: 'AMZN', name: 'Amazon.com Inc.' },
      { ticker: 'TSLA', name: 'Tesla Inc.' },
      { ticker: 'META', name: 'Meta Platforms Inc.' },
      { ticker: 'NVDA', name: 'NVIDIA Corporation' },
      { ticker: 'NFLX', name: 'Netflix Inc.' },
      { ticker: 'ADBE', name: 'Adobe Inc.' },
      { ticker: 'CRM', name: 'Salesforce Inc.' },
    ],
    NYSE: [
      { ticker: 'JPM', name: 'JPMorgan Chase & Co.' },
      { ticker: 'JNJ', name: 'Johnson & Johnson' },
      { ticker: 'V', name: 'Visa Inc.' },
      { ticker: 'PG', name: 'Procter & Gamble Co.' },
      { ticker: 'UNH', name: 'UnitedHealth Group Inc.' },
      { ticker: 'HD', name: 'Home Depot Inc.' },
      { ticker: 'MA', name: 'Mastercard Inc.' },
      { ticker: 'DIS', name: 'Walt Disney Co.' },
      { ticker: 'PYPL', name: 'PayPal Holdings Inc.' },
      { ticker: 'BAC', name: 'Bank of America Corp.' },
    ],
  };

  const templates =
    stockTemplates[market as keyof typeof stockTemplates] ||
    stockTemplates.NASDAQ;

  for (let i = 0; i < Math.min(count, templates.length); i++) {
    const template = templates[i];

    // 상위/하위에 따른 수익률 범위 설정
    let performance: number;
    if (type === 'top') {
      performance = Math.random() * 30 + 5; // 5% ~ 35%
    } else {
      performance = -(Math.random() * 25 + 5); // -5% ~ -30%
    }

    performers.push({
      ticker: template.ticker,
      name: template.name,
      performance: Math.round(performance * 100) / 100,
    });
  }

  // 수익률 기준 정렬
  if (type === 'top') {
    performers.sort((a, b) => b.performance - a.performance);
  } else {
    performers.sort((a, b) => a.performance - b.performance);
  }

  return performers;
}

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
 * @param market 검색할 시장 (KOR, USA 등)
 */
export const searchStocks = async (
  query: string,
  market: string = 'KOR'
): Promise<StockItem[]> => {
  if (query.trim().length < 2) {
    return Promise.resolve([]);
  }
  return fetchAPI(
    `${API_BASE_URL}/api/search-stocks?query=${encodeURIComponent(
      query
    )}&market=${market}`
  );
};
