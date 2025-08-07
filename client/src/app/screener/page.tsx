'use client';

import React, { useState } from 'react';
import { Info, List, ListFilter } from 'lucide-react';
import dynamic from 'next/dynamic';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge, BadgeProps } from '@/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { MultiSelect } from '@/components/ui/multi-select';

import {
  debtOptions,
  evaluationData,
  evaluationItems,
  growthOptions,
  perOptions,
  revenueOptions,
  sectorOptions,
} from '@/data/evaluation-criteria';
import { stockResults } from '@/data/mock-data';

import { EvaluationTable } from './components/evaluation-table';
import { CompanyEvaluationTable } from './components/company-evaluation-table';

const ScrollToTopButton = dynamic(
  () => import('@/components/scroll-to-top-button').then((mod) => mod.ScrollToTopButton),
  { ssr: false } // ssr: false 옵션이 서버 사이드 렌더링을 비활성화합니다.
)

const getSectorBadgeVariant = (sector: string): BadgeProps['variant'] => {
  switch (sector) {
    case 'AI':
      return 'default';
    case 'EV Battery':
      return 'secondary';
    case 'Defense':
      return 'accent';
    case 'Semiconductor':
      return 'outline';
    default:
      return 'secondary';
  }
};

const CriteriaRow = ({
  label,
  description,
  children,
}: {
  label: string;
  description: string;
  children: React.ReactNode;
}) => (
  <div className="flex flex-col lg:flex-row lg:items-center gap-2 lg:gap-4 py-4 border-b">
    <p className="font-semibold lg:w-[200px] shrink-0 flex-1/3">{label}</p>
    <div className="w-full lg:w-[300px] shrink-0 flex-1/3">{children}</div>
    <p className="text-sm text-muted-foreground w-full flex flex-1/3 gap-2">
      <Info className="h-4 w-4 text-amber-800" />
      {description}
    </p>
  </div>
);

export default function InvestmentScreenerPage() {
  const [selectedSectors, setSelectedSectors] = useState<string[]>(['ai']);

  return (
    <div className="p-6 md:p-10">
      <header className="mb-8">
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
          Investment Stock Screener
        </h1>
        <p className="text-muted-foreground mt-1">
          중장기 투자 기준에 따라 우량주를 필터링합니다.
        </p>
      </header>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-2">
            <ListFilter className="h-5 w-5" />
            Screening Criteria
          </CardTitle>
        </CardHeader>
        <CardContent className="mx-5">
          <CriteriaRow
            label="Revenue (₩ 억)"
            description="일정 수준 이상의 안정적인 기업 매출 규모 확보"
          >
            <Select defaultValue={revenueOptions[1]}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {revenueOptions.map((o) => (
                  <SelectItem key={o} value={o}>
                    {o}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CriteriaRow>
          <CriteriaRow
            label="Revenue Growth - 3 Year Average (%)"
            description="꾸준한 실적 성장 기반 확보"
          >
            <Select defaultValue={growthOptions[1]}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {growthOptions.map((o) => (
                  <SelectItem key={o} value={o}>
                    {o}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CriteriaRow>
          <CriteriaRow
            label="Operating Profit Growth - 3 Year Average (%)"
            description="영업활동의 수익성이 지속적으로 개선되는 기업 선별"
          >
            <Select defaultValue={growthOptions[1]}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {growthOptions.map((o) => (
                  <SelectItem key={o} value={o}>
                    {o}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CriteriaRow>
          <CriteriaRow
            label="ROE (Return on Equity)"
            description="자본을 효율적으로 사용하는 고품질 기업"
          >
            <Select defaultValue={growthOptions[1]}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {growthOptions.map((o) => (
                  <SelectItem key={o} value={o}>
                    {o}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CriteriaRow>
          <CriteriaRow
            label="Debt Ratio (Maximum %)"
            description="재무 안정성 확보를 위한 부채비율 조건"
          >
            <Select defaultValue={debtOptions[1]}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {debtOptions.map((o) => (
                  <SelectItem key={o} value={o}>
                    {o}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CriteriaRow>
          <CriteriaRow
            label="PER (업종 평균 대비)"
            description="성장성 대비 부담 없는 밸류에이션"
          >
            <Select defaultValue={perOptions[1]}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {perOptions.map((o) => (
                  <SelectItem key={o} value={o}>
                    {o}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </CriteriaRow>
          <CriteriaRow
            label="Sector Focus"
            description="시장 성장률 자체가 높은 산업 섹터 중심"
          >
            <MultiSelect
              options={sectorOptions}
              onValueChange={setSelectedSectors}
              defaultValue={selectedSectors}
              placeholder="섹터 선택..."
            />
          </CriteriaRow>
          <div className="pt-6 flex justify-end">
            <Button className="font-semibold">검색</Button>
          </div>
        </CardContent>
      </Card>

      {/* 결과 테이블 */}
      <div className="mt-10">
        <Card>
          <CardHeader className="flex justify-between items-center mb-4">
            <CardTitle className="text-xl flex items-center gap-2">
              <List className="h-5 w-5" />
              Screening Results
            </CardTitle>
            <span className="text-sm font-medium text-muted-foreground">
              {stockResults.length} stocks
            </span>
          </CardHeader>
          <Table className="w-full mx-5">
            <TableHeader className="bg-muted/50">
              <TableRow>
                <TableHead className="text-center">Symbol</TableHead>
                <TableHead className="text-center">Company</TableHead>
                <TableHead className="text-right">Price</TableHead>
                <TableHead className="text-right">Market Cap</TableHead>
                <TableHead className="text-right">PER</TableHead>
                <TableHead className="text-center">Sector</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {stockResults.map((stock) => (
                <TableRow key={stock.symbol}>
                  <TableCell className="font-bold text-center">
                    {stock.symbol}
                  </TableCell>
                  <TableCell className="text-center">
                    <a href="#" className="hover:underline">
                      {stock.company}
                    </a>
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="font-medium">${stock.price.toFixed(2)}</div>
                    <div
                      className={`text-xs ${
                        stock.change >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}
                    >
                      {stock.change >= 0 ? '+' : ''}
                      {stock.change.toFixed(2)}%
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    {stock.marketCap}
                  </TableCell>
                  <TableCell className="text-right">{stock.per}</TableCell>
                  <TableCell className="text-center">
                    <Badge variant={getSectorBadgeVariant(stock.sector)}>
                      {stock.sector}
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Card>
      </div>

      {/* --- 맨 아래에 평가 기준표 섹션 추가 --- */}
      <div className="mt-10">
        <header className="mb-8">
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">
            Evaluation Criteria
          </h1>
          <p className="text-muted-foreground mt-1">
            중장기 투자 종목 선별을 위한 정량/정성 평가 기준입니다.
          </p>
        </header>
        <Card>
          <CardContent className="px-5">
            <EvaluationTable data={evaluationData} />
          </CardContent>
        </Card>
      </div>

      <div className="mt-10">
        <CompanyEvaluationTable items={evaluationItems} stocks={stockResults} />
      </div>

      {/* --- 플로팅 버튼 --- */}
      <ScrollToTopButton />
    </div>
  );
}
