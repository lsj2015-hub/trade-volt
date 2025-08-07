'use client';

import { useState, useEffect } from 'react';
import { LayoutDashboard } from 'lucide-react';

import { FinancialStatementData, StockHistoryData } from '@/types/stock';
import { StockNews } from '@/types/common';

import { FinancialSection } from './components/FinancialSection';
import { HistorySection } from './components/HistorySection';
import { AiQuestionSection } from './components/AiQuestionSection';
import { NewsSection } from './components/NewsSection';
import { SearchSection } from './components/SearchSection';

import { ScrollToTopButton } from '@/components/scroll-to-top-button';

export default function StockAnalysisPage() {
  const [symbol, setSymbol] = useState<string>('AAPL');

  // AI에 컨텍스트를 제공하기 위한 상태들
  const [financialData, setFinancialData] =
    useState<FinancialStatementData | null>(null);
  const [stockHistoryData, setStockHistoryData] = useState<
    StockHistoryData[] | null
  >(null);
  const [newsData, setNewsData] = useState<StockNews[] | null>(null);

  // ✅ 이 부분을 새로운 코드로 교체합니다.
  useEffect(() => {
    // 브라우저의 자동 스크롤 복원 기능을 끄는 것을 유지합니다.
    if (window.history.scrollRestoration) {
      window.history.scrollRestoration = 'manual';
    }

    // setTimeout을 사용해 스크롤 명령을 다음 렌더링 사이클로 넘깁니다.
    // 이렇게 하면 브라우저의 자체 스크롤 복원 시도가 끝난 후 실행됩니다.
    const timer = setTimeout(() => {
      window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
    }, 0);

    // 컴포넌트가 언마운트될 때 타이머를 정리합니다.
    return () => clearTimeout(timer);
  }, []);

  const handleSymbolChange = (newSymbol: string) => {
    const upperCaseSymbol = newSymbol.trim().toUpperCase();
    if (upperCaseSymbol) {
      setSymbol(upperCaseSymbol);
      setFinancialData(null);
      setStockHistoryData(null);
      setNewsData(null);
    }
  };

  return (
    <div className="p-6 md:p-10 space-y-5">
      <header>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-2">
          <LayoutDashboard /> Stock Analysis
        </h1>
        <p className="text-muted-foreground mt-1">
          종목의 상세 정보를 분석합니다.
        </p>
      </header>
      <div className="max-w-5xl mx-auto py-8 flex flex-col gap-6">
        <SearchSection symbol={symbol} setSymbol={handleSymbolChange} />
        <FinancialSection symbol={symbol} setFinancialData={setFinancialData} />
        <HistorySection
          symbol={symbol}
          setStockHistoryData={setStockHistoryData}
        />
        <NewsSection symbol={symbol} setNewsData={setNewsData} />
        <AiQuestionSection
          symbol={symbol}
          financialData={financialData}
          stockHistoryData={stockHistoryData}
          newsData={newsData}
        />
      </div>

      {/* ✅ 플로팅 버튼 컴포넌트 추가 */}
      <ScrollToTopButton />
    </div>
  );
}
