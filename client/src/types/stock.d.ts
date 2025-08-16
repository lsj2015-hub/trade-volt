// 통합 데이터 타입
export interface StockItem {
  code: string; // 종목 코드 (한국) 또는 Ticker (미국)
  name: string; // 종목명
}

export interface StockOverviewData {
  profile: StockProfile;
  summary: FinancialSummary;
  metrics: InvestmentMetrics;
  marketData: MarketData;
  recommendations: AnalystRecommendations;
  officers: Officer[];
}

// (1) 기업 기본 정보 (프로필)
export interface StockProfile {
  symbol: string;
  longName: string;
  industry: string;
  sector: string;
  longBusinessSummary: string;
  city: string;
  state: string;
  country: string;
  website: string;
  fullTimeEmployees: string;
}

// (2) 재무 요약 정보
export interface FinancialSummary {
  totalRevenue: string;
  netIncomeToCommon: string;
  operatingMargins: string;
  dividendYield: string;
  trailingEps: string;
  totalCash: string;
  totalDebt: string;
  debtToEquity: string;
  exDividendDate?: string | null;
}

// (3) 투자 지표
export interface InvestmentMetrics {
  trailingPE: string;
  forwardPE: string;
  priceToBook: string;
  returnOnEquity: string;
  returnOnAssets: string;
  beta: string;
}

// (4) 주가/시장 정보
export interface MarketData {
  currentPrice: string;
  previousClose: string;
  dayHigh: string;
  dayLow: string;
  fiftyTwoWeekHigh: string;
  fiftyTwoWeekLow: string;
  marketCap: string;
  sharesOutstanding: string;
  volume: string;
}

// (5) 분석가 의견
export interface AnalystRecommendations {
  recommendationMean: number;
  recommendationKey: string;
  numberOfAnalystOpinions: number;
  targetMeanPrice: string;
  targetHighPrice: string;
  targetLowPrice: string;
}

// 임원 정보
export interface Officer {
  name: string;
  title: string;
  totalPay: string;
}

// 재무제표 데이터
export interface FinancialStatementRow {
  item: string;
  [year: string]: string;
}
export interface FinancialStatementData {
  years: string[];
  data: FinancialStatementRow[];
}

// 주가 히스토리 데이터
export interface StockHistoryData {
  Date: string;
  Open: number;
  High: number;
  Low: number;
  Close: number;
  Volume: number;
}
export interface StockHistoryApiResponse {
  symbol: string;
  startDate: string;
  endDate: string;
  data: StockHistoryData[];
}

/**
 * 보유 주식 정보 타입 (백엔드 HoldingItem 스키마와 일치)
 */
export interface HoldingItem {
  stock_code: string;
  stock_name: string;
  market: 'KOR' | 'OVERSEAS';
  quantity: number;
  average_price: number;
  current_price: number;
  valuation: number;
  profit_loss: number;
  return_rate: number;
  days_gain: number;
}

/**
 * 포트폴리오 전체 응답 타입 (백엔드 PortfolioResponse 스키마와 일치)
 */
export interface Portfolio {
  portfolio: HoldingItem[];
  total_assets: number;
  total_profit_loss: number;
  total_return_rate: number;
  total_days_gain: number;
}

/**
 * 거래 생성 시 보낼 데이터 타입 (백엔드 TransactionCreate 스키마와 일치)
 */
export interface TransactionData {
  stock_code: string;
  stock_name: string;
  market: 'KOR' | 'OVERSEAS';
  transaction_type: 'BUY' | 'SELL';
  quantity: number;
  price: number;
  transaction_date: date;
}