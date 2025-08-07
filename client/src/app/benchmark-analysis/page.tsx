import { ChartBarStacked } from 'lucide-react';

import { SectorAnalysisSection } from './components/SectorAnalysisSection';
import { PerformanceAnalysisSection } from './components/PerformanceAnalysisSection';
import { CompareStocksSection } from './components/CompareStocksSection';
import { TradingEntitySection } from './components/TradingEntitySection';
import { FluctuationAnalysisSection } from './components/FluctuationAnalysisSection';

import { ScrollToTopButton } from '@/components/scroll-to-top-button';

export default function BenchmarkAnaysisPage() {
  return (
    <div className="p-6 md:p-10 space-y-5">
      <header>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-2">
          <ChartBarStacked /> Benchmark Analysis
        </h1>
        <p className="text-muted-foreground mt-1">
          지표와 대비해서 수익률을 비교합니다.
        </p>
      </header>
      <div className="max-w-5xl mx-auto py-8 flex flex-col gap-6">
        <SectorAnalysisSection />
        <PerformanceAnalysisSection />
        <CompareStocksSection />
        <TradingEntitySection />
        <FluctuationAnalysisSection />
      </div>

      {/* ✅ 플로팅 버튼 컴포넌트 추가 */}
      <ScrollToTopButton />
    </div>
  );
}
