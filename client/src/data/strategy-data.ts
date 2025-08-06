import { AdjustmentCondition, TradingStrategy } from "../types/type";


export const adjustmentDetailsData: {
  [key: string]: {
    buy: AdjustmentCondition[];
    sell: AdjustmentCondition[];
  };
} = {
  'news-scalping': {
    buy: [
      {
        id: 'news-keyword',
        label: '뉴스 키워드',
        type: 'text',
        defaultValue: '실적, 계약',
      },
      {
        id: 'min-volume',
        label: '최소 거래량',
        type: 'number',
        defaultValue: '100000',
      },
    ],
    sell: [
      {
        id: 'profit-target',
        label: '목표 수익률 (%)',
        type: 'number',
        defaultValue: '3',
      },
    ],
  },
  'bollinger-day': {
    buy: [
      {
        id: 'bollinger-period',
        label: '볼린저밴드 기간',
        type: 'number',
        defaultValue: '20',
      },
      { id: 'std-dev', label: '표준편차', type: 'number', defaultValue: '2' },
    ],
    sell: [
      {
        id: 'bollinger-profit',
        label: '상단 터치 시 익절 (%)',
        type: 'number',
        defaultValue: '5',
      },
      {
        id: 'stop-loss',
        label: '하단 이탈 시 손절 (%)',
        type: 'number',
        defaultValue: '-3',
      },
    ],
  },
  'multi-function': {
    buy: [
      {
        id: 'rsi-buy-threshold',
        label: 'RSI 매수 기준 (이하)',
        type: 'number',
        defaultValue: '30',
      },
      {
        id: 'macd-signal-cross',
        label: 'MACD Signal 교차',
        type: 'text',
        defaultValue: '상향 돌파',
      },
      {
        id: 'ma-period-short',
        label: '단기 이동평균선',
        type: 'number',
        defaultValue: '5',
      },
      {
        id: 'ma-period-long',
        label: '장기 이동평균선',
        type: 'number',
        defaultValue: '20',
      },
    ],
    sell: [
      {
        id: 'rsi-sell-threshold',
        label: 'RSI 매도 기준 (이상)',
        type: 'number',
        defaultValue: '70',
      },
      {
        id: 'profit-target-multi',
        label: '목표 수익률 (%)',
        type: 'number',
        defaultValue: '10',
      },
      {
        id: 'stop-loss-multi',
        label: '손절 기준 (%)',
        type: 'number',
        defaultValue: '-5',
      },
    ],
  },
  'big-buy-small-sell': {
    buy: [
      {
        id: 'major-investor-threshold',
        label: '주요 매수 주체 (기관/외국인)',
        type: 'text',
        defaultValue: '외국인',
      },
      {
        id: 'net-buy-amount',
        label: '최소 순매수 금액 (억)',
        type: 'number',
        defaultValue: '100',
      },
      {
        id: 'volume-increase-ratio',
        label: '거래량 급증 비율 (%)',
        type: 'number',
        defaultValue: '300',
      },
    ],
    sell: [
      {
        id: 'profit-split-sell-1',
        label: '1차 분할매도 수익률 (%)',
        type: 'number',
        defaultValue: '5',
      },
      {
        id: 'profit-split-sell-2',
        label: '2차 분할매도 수익률 (%)',
        type: 'number',
        defaultValue: '10',
      },
      {
        id: 'major-sell-signal',
        label: '주요 매도 주체 전환 시 매도',
        type: 'text',
        defaultValue: '활성화',
      },
    ],
  },
};

export const tradingStrategies: TradingStrategy[] = [
  {
    id: 'news-scalping',
    name: 'Newsfeed Scalping By AI Evaluation Trading',
    description: 'AI가 뉴스를 분석하여 급등 가능성이 있는 종목을 스캘핑합니다.',
  },
  {
    id: 'bollinger-day',
    name: 'Volinger Day Trading',
    description: '볼린저밴드 지표를 활용한 단기 변동성 매매 전략입니다.',
  },
  {
    id: 'multi-function',
    name: 'Multi function Trading',
    description: '여러 보조지표를 종합하여 매수/매도 시점을 결정합니다.',
  },
  {
    id: 'big-buy-small-sell',
    name: 'Big Buy Small Sell Trading',
    description: '큰 손 매수세를 추종하고 작은 매도세에 분할 매도합니다.',
  },
];
