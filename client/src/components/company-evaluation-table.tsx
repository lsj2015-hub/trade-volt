'use client';

import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableFooter,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BrainCircuit } from 'lucide-react';
import { mockScores } from '@/data/mock-data';

// 페이지에서 받아올 데이터의 타입을 정의합니다.
interface Stock {
  symbol: string;
  // 다른 속성들...
}

interface EvaluationItem {
  name: string;
}

interface CompanyEvaluationTableProps {
  items: EvaluationItem[];
  stocks: Stock[];
}



export function CompanyEvaluationTable({
  items,
  stocks,
}: CompanyEvaluationTableProps) {
  // 각 회사의 총점을 계산합니다.
  const totalScores = stocks.map((_, companyIndex) =>
    mockScores.reduce((sum, scoreRow) => sum + (scoreRow[companyIndex] || 0), 0)
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-xl flex items-center gap-2">
          <BrainCircuit className="h-5 w-5" />
          Company Evaluation Score
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[250px] font-semibold">
                평가 항목
              </TableHead>
              {/* 회사를 테이블 헤더로 동적으로 생성합니다. */}
              {stocks.map((stock) => (
                <TableHead
                  key={stock.symbol}
                  className="text-center font-semibold"
                >
                  {stock.symbol}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {/* 평가 항목과 각 회사별 점수를 표시합니다. */}
            {items.map((item, itemIndex) => (
              <TableRow key={item.name}>
                <TableCell className="font-medium">{item.name}</TableCell>
                {stocks.map((stock, stockIndex) => (
                  <TableCell
                    key={stock.symbol}
                    className="text-center text-muted-foreground"
                  >
                    {mockScores[itemIndex]?.[stockIndex] || 'N/A'}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
          <TableFooter>
            <TableRow className="bg-muted/50">
              <TableHead className="text-center font-bold">총점</TableHead>
              {/* 각 회사의 총점을 표시합니다. */}
              {totalScores.map((score, index) => (
                <TableHead
                  key={stocks[index].symbol}
                  className="text-center font-bold"
                >
                  {score}
                </TableHead>
              ))}
            </TableRow>
          </TableFooter>
        </Table>
      </CardContent>
    </Card>
  );
}
