'use client';

import { useState } from 'react';
import { BrainCircuit, History, Settings } from 'lucide-react';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import {
  Table,
  TableBody,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { tradingStrategies } from '@/data/strategy-data';
import { tradingResults } from '@/data/mock-data';

import { BigBuySmallSell } from './components/big-buy-small-sell';
import { BollingerDay } from './components/bollinger-day';
import { Multifunction } from './components/multi-function';
import { NewsFeedScalping } from './components/newsfeed-scalping';

const strategyComponentMap: Record<string, React.ReactNode> = {
  'news-scalping': <NewsFeedScalping />,
  'bollinger-day': <BollingerDay />,
  'multi-function': <Multifunction />,
  'big-buy-small-sell': <BigBuySmallSell />,
};

export default function StrategyPage() {
  const [selectedStrategy, setSelectedStrategy] = useState('news-scalping');

  // --- 수익률 계산 로직 ---
  const totalProfit = tradingResults.reduce(
    (sum, item) => sum + item.profit,
    0
  );
  const totalInvestment = tradingResults.reduce(
    (sum, item) => sum + item.buyPrice * item.quantity,
    0
  );
  const overallReturnRate =
    totalInvestment > 0 ? (totalProfit / totalInvestment) * 100 : 0;

  return (
    <div className="p-6 md:p-10 space-y-10">
      <Card>
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2">
            <BrainCircuit className="h-5 w-5" />
            Day trading strategy
          </CardTitle>
        </CardHeader>
        <CardContent>
          <RadioGroup
            value={selectedStrategy}
            onValueChange={setSelectedStrategy}
            className="space-y-4"
          >
            {tradingStrategies.map((strategy) => (
              <div
                key={strategy.id}
                className="grid grid-cols-[auto_1fr_auto] items-center gap-4 p-4 border rounded-lg"
              >
                <RadioGroupItem value={strategy.id} id={strategy.id} />
                <div className="flex flex-col">
                  <Label
                    htmlFor={strategy.id}
                    className="font-semibold cursor-pointer"
                  >
                    {strategy.name}
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    {strategy.description}
                  </p>
                </div>
              </div>
            ))}
          </RadioGroup>
        </CardContent>
      </Card>

      {/* --- 2. Adjustment details 섹션 --- */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Adjustment details
          </CardTitle>
        </CardHeader>
        {/* 선택된 전략에 맞는 컴포넌트를 맵에서 찾아 렌더링합니다. */}
        {strategyComponentMap[selectedStrategy]}
      </Card>

      {/* --- 3. Day Trading Results 섹션 --- */}
      <Card>
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2">
            <History className="h-5 w-5" />
            Day Trading Results
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>매매 종목</TableHead>
                <TableHead className="text-right">매수가</TableHead>
                <TableHead className="text-right">매도가</TableHead>
                <TableHead className="text-right">수량</TableHead>
                <TableHead className="text-right">매매이익</TableHead>
                <TableHead className="text-right">수익률</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tradingResults.map((result, index) => (
                <TableRow key={index}>
                  <TableCell className="font-medium">{result.stock}</TableCell>
                  <TableCell className="text-right">
                    {result.buyPrice.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right">
                    {result.sellPrice.toLocaleString()}
                  </TableCell>
                  <TableCell className="text-right">
                    {result.quantity}
                  </TableCell>
                  <TableCell
                    className={`text-right ${
                      result.profit >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {result.profit.toLocaleString()}
                  </TableCell>
                  <TableCell
                    className={`text-right ${
                      result.returnRate >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}
                  >
                    {result.returnRate.toFixed(2)}%
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
            <TableFooter>
              <TableRow>
                <TableCell colSpan={4} className="font-bold">
                  합계
                </TableCell>
                <TableCell
                  className={`text-right font-bold ${
                    totalProfit >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {totalProfit.toLocaleString()}
                </TableCell>
                <TableCell
                  className={`text-right font-bold ${
                    overallReturnRate >= 0 ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {overallReturnRate.toFixed(2)}%
                </TableCell>
              </TableRow>
            </TableFooter>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
