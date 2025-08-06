export interface Option {
  value: string;
  label: string;
}

// Screener 페이지 결과 데이터 타입
export interface StockResult {
  symbol: string;
  company: string;
  price: number;
  change: number;
  marketCap: string;
  per: string;
  sector: string;
}

// 평가 항목 데이터 타입
export interface EvaluationItem {
  name: string;
}

// Strategy 페이지 데이터 타입
export interface AdjustmentCondition {
  id: string;
  label: string;
  type: 'number' | 'text';
  defaultValue: string;
}

export interface TradingStrategy {
  id: string;
  name: string;
  description: string;
}

export interface TradingResult {
  stock: string;
  buyPrice: number;
  sellPrice: number;
  quantity: number;
  profit: number;
  returnRate: number;
}
