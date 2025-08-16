'use client';

import React from 'react';
import { LayoutDashboard } from 'lucide-react';

import { Card, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

import { usStocks, koreanStocks } from '@/data/portfolio-data';
import { getGainColor } from '@/lib/utils';

import { PortfolioSummaryCard } from './components/portfolio-summary-card';
import { PortfolioTable } from './components/portfolio-table';

export default function MyPortfolioPage() {
  // --- 각 포트폴리오의 합계를 계산하는 로직 추가 ---
  const usdToKrwRate = 1403.46;

  const koreanSummary = {
    value: koreanStocks.reduce((sum, s) => sum + s.marketValue, 0),
    daysGain: koreanStocks.reduce((sum, s) => sum + s.daysGain, 0),
    totalGain: koreanStocks.reduce((sum, s) => sum + s.totalGain, 0),
  };
  const usSummary = {
    value: usStocks.reduce((sum, s) => sum + s.marketValue, 0),
    daysGain: usStocks.reduce((sum, s) => sum + s.daysGain, 0),
    totalGain: usStocks.reduce((sum, s) => sum + s.totalGain, 0),
  };

  const totalPortfolioValue =
    koreanSummary.value + usSummary.value * usdToKrwRate;
  const totalDaysGain =
    koreanSummary.daysGain + usSummary.daysGain * usdToKrwRate;
  const totalGain =
    koreanSummary.totalGain + usSummary.totalGain * usdToKrwRate;

  const totalDaysGainPercent =
    totalPortfolioValue - totalDaysGain !== 0
      ? (totalDaysGain / (totalPortfolioValue - totalDaysGain)) * 100
      : 0;
  const totalGainPercent =
    totalPortfolioValue - totalGain !== 0
      ? (totalGain / (totalPortfolioValue - totalGain)) * 100
      : 0;

  const formatKrw = (value: number) =>
    new Intl.NumberFormat('ko-KR', {
      style: 'currency',
      currency: 'KRW',
    }).format(value);


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
      <Card className='gap-3'>
        <CardContent className="p-3">
          <p className="text-4xl font-bold tracking-tighter">
            {formatKrw(totalPortfolioValue)}
          </p>
          <div className="flex items-center gap-2 mt-2">
            <div
              className={`text-lg font-semibold ${getGainColor(totalDaysGain)}`}
            >
              {totalDaysGain >= 0 ? '+' : ''}
              {formatKrw(totalDaysGain)}
              <span className="ml-2">({totalDaysGainPercent.toFixed(2)}%)</span>
              <span className="text-sm text-muted-foreground ml-2">
                Day&apos;s Gain
              </span>
            </div>
            <div className={`text-lg font-semibold ${getGainColor(totalGain)}`}>
              {totalGain >= 0 ? '+' : ''}
              {formatKrw(totalGain)}
              <span className="ml-2">({totalGainPercent.toFixed(2)}%)</span>
              <span className="text-sm text-muted-foreground ml-2">
                Total Gain
              </span>
            </div>
          </div>
        </CardContent>

      {/* --- 개별 포트폴리오 요약 카드 섹션 --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mx-5 mb-5">
          <PortfolioSummaryCard
            title="Korean Stocks Portfolio"
            totalMarketValue={koreanSummary.value}
            totalDaysGain={koreanSummary.daysGain}
            totalGain={koreanSummary.totalGain}
            currency="KRW"
          />
          <PortfolioSummaryCard
            title="US Stocks Portfolio"
            totalMarketValue={usSummary.value}
            totalDaysGain={usSummary.daysGain}
            totalGain={usSummary.totalGain}
            currency="USD"
          />
        </div>
      </Card>


      <Card>
        <CardContent className="p-6">
          <Tabs defaultValue="korea">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="korea">My List (KOREA)</TabsTrigger>
              <TabsTrigger value="usa">My List (USA)</TabsTrigger>
            </TabsList>
            <TabsContent value="korea" className="mt-4">
              <PortfolioTable stocks={koreanStocks} currency="KRW" />
            </TabsContent>
            <TabsContent value="usa" className="mt-4">
              <PortfolioTable stocks={usStocks} currency="USD" />
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
}
 