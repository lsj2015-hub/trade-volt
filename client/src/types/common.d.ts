// - API로부터 받아오는 개별 주식 뉴스 기사의 타입 정의 ---
export interface StockNews {
  title: string;
  url: string;
  publishedDate: string;
  source: string;
  summary: string;
  translatedTitle?: string;
  translatedSummary?: string;
}

// --- 섹터 분석 관련 타입 ---
export interface SectorGroups {
  [market: string]: {
    [group: string]: string[];
  };
}

export interface TickerInfo {
  ticker: string;
  name: string;
}

export interface SectorTickerResponse {
  tickers: TickerInfo[];
}

export interface SectorAnalysisRequest {
  start_date: string;
  end_date: string;
  tickers: string[];
}

export interface ChartData {
  date: string;
  [key: string]: number | string | null;
}

export interface SectorAnalysisResponse {
  data: ChartData[];
}

// --- 수익율 상위/하위 종목 관련 타입 ---
export interface StockPerformance {
  ticker: string;
  name: string;
  performance: number;
}

export interface PerformanceAnalysisResponse {
  top_performers: StockPerformance[];
  bottom_performers: StockPerformance[];
}

export interface PerformanceAnalysisRequest {
  market: string;
  start_date: string;
  end_date: string;
  top_n: number;
}

/**
 * @description 주가 비교 분석 API 요청 시 서버로 보내는 데이터 타입
 */
export interface StockComparisonRequest {
  tickers: string[];
  start_date: string;
  end_date: string;
}

/**
 * @description 차트에 표시될 각 데이터 포인트의 타입
 */
export interface StockComparisonDataPoint {
  date: string;
  // [ticker: string]는 동적 키를 의미하며, 여러 티커의 데이터가 들어올 수 있습니다.
  [ticker: string]: number | string | null;
}

/**
 * @description 차트의 각 라인(계열)에 대한 정보를 담는 타입
 */
export interface StockComparisonSeries {
  dataKey: string;
  name: string;
}

/**
 * @description 주가 비교 분석 API의 전체 응답 데이터 타입
 */
export interface StockComparisonResponse {
  data: StockComparisonDataPoint[];
  series: StockComparisonSeries[];
}

// --- 투자자별 매매동향 분석 관련 타입 ---
export interface TradingVolumeRequest {
  start_date: string;
  end_date: string;
  ticker: string;
  detail: boolean;
  institution_only: boolean;
}

export interface TradingVolumeData {
  [key: string]: string | number;
}

export interface TradingVolumeResponse {
  index_name: string;
  data: TradingVolumeData[];
}

export interface NetPurchaseRequest {
  start_date: string;
  end_date: string;
  market: 'KOSPI' | 'KOSDAQ';
  investor: string;
}

export interface NetPurchaseData {
  ticker: string;
  name: string;
  volume: number;
  value: number;
}

export interface NetPurchaseResponse {
  data: NetPurchaseData[];
}

// --- 변동성 종목 분석 관련 타입 ---
export interface FluctuationAnalysisRequest {
  country: string;
  market: string;
  start_date: string;
  end_date: string;
  decline_period: number;
  decline_rate: number;
  rebound_period: number;
  rebound_rate: number;
}

export interface EventInfo {
  ticker: string;
  name: string;
  trough_date: string;
  trough_price: number;
  rebound_date: string;
  rebound_price: number;
  rebound_performance: number;
}

export interface FluctuationStockInfo {
  ticker: string;
  name: string;
  occurrence_count: number;
  recent_trough_date: string;
  recent_trough_price: number;
  recent_rebound_date: string;
  recent_rebound_performance: number;
  events: EventInfo[];
}

export interface FluctuationAnalysisResponse {
  found_stocks: FluctuationStockInfo[];
}
