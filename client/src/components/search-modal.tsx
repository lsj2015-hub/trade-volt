'use client';

import { useState, useEffect, useMemo } from 'react';
import { Loader2, AlertTriangle } from 'lucide-react';
import debounce from 'lodash.debounce';

import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Label } from '@/components/ui/label';

// 타입과 API 함수 import 경로는 프로젝트 구조에 맞게 확인해주세요.
import { StockItem } from '@/types/stock';
import { searchStocks, APIError } from '@/lib/api';

interface SearchModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SearchModal({ isOpen, onOpenChange }: SearchModalProps) {
  const [query, setQuery] = useState('');
  const [market, setMarket] = useState('KOR');
  const [results, setResults] = useState<StockItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // --- 🌟 1. useCallback을 useMemo로 변경 ---
  // debounce 함수는 매 렌더링마다 새로 생성될 필요가 없으므로,
  // useMemo를 사용하여 컴포넌트가 처음 마운트될 때 딱 한 번만 생성하도록 합니다.
  const debouncedFetch = useMemo(
    () =>
      debounce(async (currentQuery: string, currentMarket: string) => {
        if (currentQuery.trim().length < 2) {
          setResults([]);
          setError(null);
          return;
        }
        setLoading(true);
        setError(null);
        try {
          const data = await searchStocks(currentQuery, currentMarket);

          console.log('API 응답 데이터:', data); 

          setResults(data);
        } catch (err) {
          if (err instanceof APIError) {
            setError(err.message);
          } else if (err instanceof Error) {
            setError(err.message);
          } else {
            setError('알 수 없는 오류가 발생했습니다.');
          }
          setResults([]); // 에러 발생 시 기존 결과 초기화
        } finally {
          setLoading(false);
        }
      }, 300), // 300ms 지연
    [] // 의존성 배열이 비어있으므로 이 함수는 재생성되지 않습니다.
  );

  // --- 🌟 2. useEffect 의존성 배열을 간결하게 수정 ---
  // debouncedFetch 함수는 이제 useMemo 덕분에 재생성되지 않는 안정적인(stable) 값이므로,
  // 더 이상 useEffect의 의존성 배열에 포함할 필요가 없습니다.
  useEffect(() => {
    debouncedFetch(query, market);
    // 컴포넌트가 사라질 때 예약된 debounce 함수를 취소하는 cleanup 함수
    return () => debouncedFetch.cancel();
  }, [query, market]); // query나 market이 변경될 때만 이 effect가 실행됩니다.

  // 모달이 닫힐 때 상태를 초기화하는 effect
  useEffect(() => {
    if (!isOpen) {
      setQuery('');
      setResults([]);
      setMarket('KOR');
      setError(null);
    }
  }, [isOpen]);

  // UI 렌더링 로직
  const renderContent = () => {
    if (loading) {
      return (
        <div className="flex justify-center items-center h-full">
          <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
        </div>
      );
    }
    if (error) {
      return (
        <div className="flex flex-col justify-center items-center h-full text-destructive">
          <AlertTriangle className="h-6 w-6 mb-2" />
          <p>{error}</p>
        </div>
      );
    }
    if (results.length > 0) {
      console.log('렌더링 직전 results 상태:', results);
      
      return results.map((item) => (
        <div
          key={item.code}
          className="flex justify-between p-2 hover:bg-muted rounded-md cursor-pointer"
        >
          <span className="font-medium">{item.name}</span>
          <span className="text-muted-foreground">{item.code}</span>
        </div>
      ));
    }
    return (
      <p className="text-center text-muted-foreground pt-4">
        {query.length > 1
          ? '검색 결과가 없습니다.'
          : '검색어를 2자 이상 입력해주세요.'}
      </p>
    );
  };

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[625px]">
        <DialogHeader>
          <DialogTitle>종목 검색</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <Input
            placeholder="회사명 또는 종목코드를 입력하세요..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            autoFocus
          />
          <RadioGroup
            value={market}
            onValueChange={setMarket}
            className="flex items-center space-x-4"
          >
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="KOR" id="r-kor" />
              <Label htmlFor="r-kor">국내주식</Label>
            </div>
            <div className="flex items-center space-x-2">
              <RadioGroupItem value="USA" id="r-usa" />
              <Label htmlFor="r-usa">미국주식</Label>
            </div>
          </RadioGroup>
          <div className="mt-4 h-64 overflow-y-auto border rounded-md p-2">
            {renderContent()}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
