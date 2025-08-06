'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
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
import { Button } from '@/components/ui/button';
import { BrainCircuit, Settings, History, ArrowDownCircle, ArrowUpCircle } from 'lucide-react';
import {
  adjustmentDetailsData,
  tradingStrategies,
} from '@/data/strategy-data';
import { tradingResults } from '@/data/mock-data';

export default function StrategyPage() {
  const [selectedStrategy, setSelectedStrategy] = useState('news-scalping');

  const currentDetails = adjustmentDetailsData[selectedStrategy] || {
    buy: [],
    sell: [],
  };
  
  // --- 수익률 계산 로직 추가 ---
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
        <CardContent>
          {/* 좌우 배치를 위한 그리드 컨테이너 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* 좌측: 매수 조건 (구분선과 여백 추가) */}
            <div className="space-y-4 md:border-r md:pr-8">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <ArrowDownCircle className="h-5 w-5 text-blue-500" />
                매수 조건
              </h3>
              {currentDetails.buy.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between gap-4"
                >
                  <Label htmlFor={item.id} className="shrink-0">
                    {item.label}
                  </Label>
                  {/* 입력창 크기 조절 */}
                  <Input
                    id={item.id}
                    type={item.type}
                    defaultValue={item.defaultValue}
                    className="w-full max-w-48"
                  />
                </div>
              ))}
            </div>
            {/* 우측: 매도 조건 (여백 추가) */}
            <div className="space-y-4 md:pl-8">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <ArrowUpCircle className="h-5 w-5 text-red-500" />
                매도 조건
              </h3>
              {currentDetails.sell.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between gap-4"
                >
                  <Label htmlFor={item.id} className="shrink-0">
                    {item.label}
                  </Label>
                  {/* 입력창 크기 조절 */}
                  <Input
                    id={item.id}
                    type={item.type}
                    defaultValue={item.defaultValue}
                    className="w-full max-w-48"
                  />
                </div>
              ))}
            </div>
          </div>
          {/* 매매 실행 버튼 */}
          <div className="mt-8 pt-6 border-t flex justify-end">
            <Button className="font-semibold">매매 실행</Button>
          </div>
        </CardContent>
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
