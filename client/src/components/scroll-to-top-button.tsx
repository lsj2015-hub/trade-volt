'use client';

import { useEffect, useState } from 'react';
import { ArrowUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export const ScrollToTopButton = () => {
  const [isVisible, setIsVisible] = useState(false);

  // 맨 위로 스크롤하는 함수 수정
  const scrollToTop = () => {
    // id로 스크롤 영역을 직접 찾습니다.
    const scrollableArea = document.getElementById('main-scroll-area');
    if (scrollableArea) {
      scrollableArea.scrollTo({
        top: 0,
        behavior: 'smooth',
      });
    }
  };

  useEffect(() => {
    // id로 스크롤 영역을 찾습니다.
    const scrollableArea = document.getElementById('main-scroll-area');

    // 스크롤 위치를 감지하는 함수 수정
    const toggleVisibility = () => {
      if (scrollableArea && scrollableArea.scrollTop > 300) {
        setIsVisible(true);
      } else {
        setIsVisible(false);
      }
    };

    // window 대신 찾은 스크롤 영역에 이벤트 리스너를 추가합니다.
    if (scrollableArea) {
      scrollableArea.addEventListener('scroll', toggleVisibility);
    }

    return () => {
      if (scrollableArea) {
        scrollableArea.removeEventListener('scroll', toggleVisibility);
      }
    };
  }, []);

  return (
    <Button
      variant="secondary"
      size="icon"
      onClick={scrollToTop}
      className={cn(
        'fixed bottom-8 right-8 h-12 w-12 rounded-full shadow-lg transition-opacity duration-300 z-50', // z-index 추가
        isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'
      )}
    >
      <ArrowUp className="h-6 w-6" />
      <span className="sr-only">Go to top</span>
    </Button>
  );
};
