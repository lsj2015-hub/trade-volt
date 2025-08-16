// 포트폴리오 아이템의 타입을 정의합니다.
export interface PortfolioItem {
  ticker: string;
  name: string;
  shares: number;
  avgCost: number;
  price: number;
  daysGain: number;
  totalGain: number;
  marketValue: number;
}

// 미국 주식 데이터
export const overseasStocks: PortfolioItem[] = [
  {
    ticker: 'VRTX',
    name: 'Vertex Pharmace...',
    shares: 10,
    avgCost: 401.58,
    price: 456.87,
    daysGain: -122.9,
    totalGain: 552.9,
    marketValue: 4568.7,
  },
  {
    ticker: 'NVDA',
    name: 'NVIDIA Corporati...',
    shares: 40,
    avgCost: 130.22,
    price: 177.87,
    daysGain: -56.0,
    totalGain: 1906.11,
    marketValue: 7114.8,
  },
  {
    ticker: 'GOOGL',
    name: 'Alphabet Inc.',
    shares: 38,
    avgCost: 166.46,
    price: 191.9,
    daysGain: -175.94,
    totalGain: 966.6,
    marketValue: 7292.2,
  },
  {
    ticker: 'AAPL',
    name: 'Apple Inc.',
    shares: 37,
    avgCost: 118.29,
    price: 207.57,
    daysGain: -54.76,
    totalGain: 3303.45,
    marketValue: 7680.09,
  },
  {
    ticker: 'AMZN',
    name: 'Amazon.com, Inc.',
    shares: 10,
    avgCost: 105.23,
    price: 234.11,
    daysGain: 39.2,
    totalGain: 1288.76,
    marketValue: 2341.1,
  },
];

// 한국 주식 데이터
export const koreanStocks: PortfolioItem[] = [
  {
    ticker: '006260.KS',
    name: 'LS Corp.',
    shares: 50,
    avgCost: 187237,
    price: 162000,
    daysGain: -565000,
    totalGain: -1.26e6,
    marketValue: 8.1e6,
  },
  {
    ticker: '017670.KS',
    name: 'SK Telecom Co., L...',
    shares: 100,
    avgCost: 53100,
    price: 55500,
    daysGain: -60000,
    totalGain: 240000,
    marketValue: 5.55e6,
  },
  {
    ticker: '000270.KS',
    name: 'Kia Corporation',
    shares: 47,
    avgCost: 104947,
    price: 100800,
    daysGain: -70500,
    totalGain: -194900,
    marketValue: 4.74e6,
  },
  {
    ticker: '003670.KS',
    name: 'Posco Future M C...',
    shares: 22,
    avgCost: 235994,
    price: 137100,
    daysGain: -118800,
    totalGain: -2.18e6,
    marketValue: 3.02e6,
  },
  {
    ticker: '035720.KS',
    name: 'Kakao Corp.',
    shares: 70,
    avgCost: 73560,
    price: 55500,
    daysGain: -175000,
    totalGain: -1.26e6,
    marketValue: 3.89e6,
  },
];
