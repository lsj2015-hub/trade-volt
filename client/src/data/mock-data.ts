import { StockResult, TradingResult } from "../types/type";

// 임의의 점수 데이터를 생성합니다. (항목 수 x 회사 수)
const mockScores = [
  [7, 5, 6, 7],
  [5, 4, 3, 5],
  [4, 3, 5, 4],
  [3, 5, 5, 5],
  [5, 8, 8, 6], // 5개
  [6, 6, 5, 6],
  [3, 4, 4, 4],
  [3, 3, 2, 2],
  [2, 2, 3, 3],
  [3, 3, 3, 2], // 10개
  [4, 4, 4, 2],
  [4, 4, 5, 4], // 12개
  [4, 4, 3, 3],
  [3, 2, 3, 2],
  [2, 2, 3, 2],
  [3, 2, 3, 3],
  [3, 4, 4, 3], // 17개
  [2, 2, 2, 3],
  [2, 1, 2, 1], // 19개
  [3, 1, 3, 1],
  [3, 2, 3, 1],
  [3, 1, 1, 3],
  [5, 4, 3, 3],
  [2, 3, 3, 2], // 24개
  [3, 2, 3, 3],
];

const stockResults: StockResult[] = [
  {
    symbol: 'NVDA',
    company: 'NVIDIA Corporation',
    price: 875.23,
    change: 2.34,
    marketCap: '2.15T',
    per: '68.4',
    sector: 'AI',
  },
  {
    symbol: 'TSLA',
    company: 'Tesla Inc',
    price: 248.5,
    change: -1.85,
    marketCap: '789.4B',
    per: '24.3',
    sector: 'EV Battery',
  },
  {
    symbol: 'AMD',
    company: 'Advanced Micro Devices',
    price: 164.89,
    change: -0.52,
    marketCap: '266.2B',
    per: '21.8',
    sector: 'Semiconductor',
  },
  {
    symbol: 'LMT',
    company: 'Lockheed Martin',
    price: 441.25,
    change: 0.73,
    marketCap: '105.8B',
    per: '18.9',
    sector: 'Defense',
  },
];

const tradingResults: TradingResult[] = [
  {
    stock: '삼성전자',
    buyPrice: 85000,
    sellPrice: 86500,
    quantity: 10,
    profit: 15000,
    returnRate: 1.76,
  },
  {
    stock: 'SK하이닉스',
    buyPrice: 210000,
    sellPrice: 205000,
    quantity: 5,
    profit: -25000,
    returnRate: -2.38,
  },
  {
    stock: 'LG에너지솔루션',
    buyPrice: 350000,
    sellPrice: 360500,
    quantity: 3,
    profit: 31500,
    returnRate: 3.0,
  },
];

export { mockScores, stockResults, tradingResults };