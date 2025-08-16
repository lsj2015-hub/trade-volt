'use client';

import { createContext, useState, useContext, ReactNode, useEffect } from 'react';

import { getPortfolio } from '@/lib/api';
import { Portfolio } from '@/types/stock';

// Context에 담길 데이터의 타입 정의
interface PortfolioContextType {
  portfolioData: Portfolio | null;
  isLoading: boolean;
  fetchPortfolioData: () => Promise<void>;
}

// Context 생성
const PortfolioContext = createContext<PortfolioContextType | undefined>(undefined);

// Context를 제공하는 Provider 컴포넌트
export function PortfolioProvider({ children }: { children: ReactNode }) {
  const [portfolioData, setPortfolioData] = useState<Portfolio | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchPortfolioData = async () => {
    try {
      setIsLoading(true);
      const data = await getPortfolio();
      setPortfolioData(data);
    } catch (error) {
      console.error("포트폴리오 데이터를 가져오는 데 실패했습니다:", error);
      setPortfolioData(null); // 에러 발생 시 데이터 초기화
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolioData();
  }, []);

  const value = { portfolioData, isLoading, fetchPortfolioData };

  console.log('context - portfolioData', portfolioData);

  return (
    <PortfolioContext.Provider value={value}>
      {children}
    </PortfolioContext.Provider>
  );
}

// 다른 컴포넌트에서 Context를 쉽게 사용하기 위한 Custom Hook
export function usePortfolio() {
  const context = useContext(PortfolioContext);
  if (context === undefined) {
    throw new Error('usePortfolio must be used within a PortfolioProvider');
  }
  return context;
}