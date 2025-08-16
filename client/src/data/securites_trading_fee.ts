// 증권사별 수수료 및 세금 정보
// 참고: 거래세는 매도 시에만 부과됩니다 (국내주식 기준).

export const KOREA_SECURITIES_TAX_RATE = 0.18 / 100; // 예: 0.18%

export const TRADING_FEES = {
  // 대략적인 수수료로 매매 BEF를 계산하기 위한 용도로 사용
  DOMESTIC_FEE: {
    buy_commission_rate: 0.015 / 100,
    sell_commission_rate: 0.015 / 100,
  },
  OVERSEAS_FEE: {
    buy_commission_rate: 0.25 / 100,
    sell_commission_rate: 0.25 / 100,
  },
};

