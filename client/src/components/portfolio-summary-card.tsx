'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface PortfolioSummaryCardProps {
  title: string;
  totalMarketValue: number;
  totalDaysGain: number;
  totalGain: number;
  currency: 'USD' | 'KRW';
}

const getGainColor = (value: number) =>
  value >= 0 ? 'text-green-600' : 'text-red-600';

const formatCurrency = (value: number, currency: 'USD' | 'KRW') => {
  return new Intl.NumberFormat(currency === 'KRW' ? 'ko-KR' : 'en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: currency === 'KRW' ? 0 : 2,
    maximumFractionDigits: 2,
  }).format(value);
};

export function PortfolioSummaryCard({
  title,
  totalMarketValue,
  totalDaysGain,
  totalGain,
  currency,
}: PortfolioSummaryCardProps) {
  const daysGainPercent =
    totalMarketValue - totalDaysGain !== 0
      ? (totalDaysGain / (totalMarketValue - totalDaysGain)) * 100
      : 0;
  const totalGainPercent =
    totalMarketValue - totalGain !== 0
      ? (totalGain / (totalMarketValue - totalGain)) * 100
      : 0;

  return (
    <Card className='bg-background'>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-1">
        <p className="text-xl font-bold tracking-tighter">
          {formatCurrency(totalMarketValue, currency)}
        </p>
        <div className={`text-sm font-semibold ${getGainColor(totalDaysGain)}`}>
          {totalDaysGain >= 0 ? '+' : ''}
          {formatCurrency(totalDaysGain, currency)}
          <span className="ml-2">({daysGainPercent.toFixed(2)}%)</span>
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
