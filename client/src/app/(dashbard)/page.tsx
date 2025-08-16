'use client';

import { useState, useEffect } from 'react';
import { LayoutDashboard, Loader2 } from 'lucide-react';

import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { getGainColor } from '@/lib/utils';
import { PortfolioSummaryCard } from './components/portfolio-summary-card';
import { PortfolioTable } from './components/portfolio-table';

import { usePortfolio } from '@/context/PortfolioContext';

export default function MyPortfolioPage() {
  const { portfolioData, isLoading } = usePortfolio();

  console.log('portfolioData ', portfolioData);

  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  if (!isMounted || isLoading) {
    return (
      <div className="flex justify-center items-center h-96">
        <Loader2 className="w-10 h-10 animate-spin text-muted-foreground" />
      </div>
    );
  }

  // 데이터 로드 실패 또는 데이터가 없을 경우
  if (!portfolioData) {
    return <div>포트폴리오를 불러오지 못했습니다.</div>;
  }

  const usdToKrwRate = 1403.46; // 환율은 우선 고정값으로 유지

  // API 응답 데이터에서 국내/해외 주식 분리
  const domesticStocks = portfolioData.portfolio.filter(
    (s) => s.market === 'KOR'
  );
  const overseasStocks = portfolioData.portfolio.filter(
    (s) => s.market === 'OVERSEAS'
  );

  // 국내 주식 요약 계산
  const domesticSummary = {
    value: domesticStocks.reduce((sum, s) => sum + s.valuation, 0),
    daysGain: domesticStocks.reduce((sum, s) => sum + s.days_gain, 0),
    totalGain: domesticStocks.reduce((sum, s) => sum + s.profit_loss, 0),
  };

  // 미국 주식 요약 계산 (평가금액, 총 손익)
  const overseasSummary = {
    value: overseasStocks.reduce((sum, s) => sum + s.valuation, 0),
    daysGain: overseasStocks.reduce((sum, s) => sum + s.days_gain, 0),
    totalGain: overseasStocks.reduce((sum, s) => sum + s.profit_loss, 0),
  };

  // 전체 포트폴리오 요약 계산
  const totalPortfolioValue = portfolioData.total_assets;
  const totalDaysGain = portfolioData.total_days_gain;
  const totalGain = portfolioData.total_profit_loss;

  const totalPurchaseAmount = totalPortfolioValue - totalGain;
  const totalGainPercent =
    totalPurchaseAmount !== 0 ? (totalGain / totalPurchaseAmount) * 100 : 0;

  const yesterdayTotalValue = totalPortfolioValue - totalDaysGain;
  const daysGainPercent =
    yesterdayTotalValue !== 0 ? (totalDaysGain / yesterdayTotalValue) * 100 : 0;

  console.log('totalDaysGain', totalDaysGain);

  return (
    <div className="p-6 md:p-10 space-y-5">
      <header>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-2">
          <LayoutDashboard /> My Portfolio
        </h1>
        <p className="text-muted-foreground mt-1">
          보유 종목 현황을 확인합니다.
        </p>
      </header>

      {/* --- 최상단에 요약 카드 섹션 추가 --- */}
      <Card className="gap-3">
        <CardContent className="p-6">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-4xl font-bold tracking-tighter">
                {totalPortfolioValue.toLocaleString('ko-KR', {
                  style: 'currency',
                  currency: 'KRW',
                })}
              </p>
            </div>
            <div className="text-right">
              <div className={`font-semibold ${getGainColor(totalDaysGain)}`}>
                {totalDaysGain >= 0 ? '+' : ''}
                {totalDaysGain.toLocaleString('ko-KR', {
                  style: 'currency',
                  currency: 'KRW',
                })}
                <span className="ml-2">({daysGainPercent.toFixed(2)}%)</span>
                <span className="text-xs text-muted-foreground ml-2">
                  Day&apos;s Gain
                </span>
              </div>
              <div className={`font-semibold ${getGainColor(totalGain)}`}>
                {totalGain >= 0 ? '+' : ''}
                {totalGain.toLocaleString('ko-KR', {
                  style: 'currency',
                  currency: 'KRW',
                })}
                <span className="ml-2">({totalGainPercent.toFixed(2)}%)</span>
                <span className="text-xs text-muted-foreground ml-2">
                  Total Gain
                </span>
              </div>
            </div>
          </div>
        </CardContent>

        {/* --- 개별 포트폴리오 요약 카드 섹션 --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mx-5 mb-5">
          <PortfolioSummaryCard
            title="Korean Stocks Portfolio"
            totalMarketValue={domesticSummary.value}
            totalDayGain={domesticSummary.daysGain}
            totalGain={domesticSummary.totalGain}
            currency="KRW"
          />
          <PortfolioSummaryCard
            title="Overseas Stocks Portfolio"
            totalMarketValue={overseasSummary.value}
            totalDayGain={overseasSummary.daysGain}
            totalGain={overseasSummary.totalGain}
            currency="USD"
          />
        </div>
      </Card>

      <Card>
        <CardContent className="p-6">
          <Tabs defaultValue="korea">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="korea">My List (KOREA)</TabsTrigger>
              <TabsTrigger value="overseas">My List (OVERSEAS)</TabsTrigger>
            </TabsList>
            <TabsContent value="korea" className="mt-4">
              <PortfolioTable stocks={domesticStocks} currency="KRW" />
            </TabsContent>
            <TabsContent value="overseas" className="mt-4">
              <PortfolioTable stocks={overseasStocks} currency="USD" />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
