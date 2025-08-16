'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { formatCurrency, getGainColor } from '@/lib/utils';

interface PortfolioSummaryCardProps {
  title: string;
  totalMarketValue: number;
  totalDayGain: number;
  totalGain: number;
  currency: 'USD' | 'KRW';
}

export function PortfolioSummaryCard({
  title,
  totalMarketValue,
  totalDayGain,
  totalGain,
  currency,
}: PortfolioSummaryCardProps) {
  const dayGainPercent =
    totalMarketValue - totalDayGain !== 0
      ? (totalDayGain / (totalMarketValue - totalDayGain)) * 100
      : 0;
  const totalGainPercent =
    totalMarketValue - totalGain !== 0
      ? (totalGain / (totalMarketValue - totalGain)) * 100
      : 0;

  return (
    <Card className="bg-background">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        <p className="text-xl font-bold tracking-tighter">
          {formatCurrency(totalMarketValue, currency)}
        </p>
        <div className={`text-sm font-semibold ${getGainColor(totalDayGain)}`}>
          {totalDayGain >= 0 ? '+' : ''}
          {formatCurrency(totalDayGain, currency)}
          <span className="ml-2">({dayGainPercent.toFixed(2)}%)</span>
          <span className="text-xs text-muted-foreground ml-2">
            Day&apos;s Gain
          </span>
        </div>
        <div className={`text-sm font-semibold ${getGainColor(totalGain)}`}>
          {totalGain >= 0 ? '+' : ''}
          {formatCurrency(totalGain, currency)}
          <span className="ml-2">({totalGainPercent.toFixed(2)}%)</span>
          <span className="text-xs text-muted-foreground ml-2">Total Gain</span>
        </div>
      </CardContent>
    </Card>
  );
}
