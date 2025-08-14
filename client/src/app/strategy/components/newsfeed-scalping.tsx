/* eslint-disable @typescript-eslint/no-explicit-any */
'use client';

import { useState } from 'react';
import { Loader2, CheckCircle } from 'lucide-react';

import { CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { searchNewsCandidates } from '@/lib/api';
import {
  NewsSearchResponse,
} from '@/types/strategy';

export const NewsFeedScalping = () => {
  const [newsSeconds, setNewsSeconds] = useState(600);
  const [displayCount, setDisplayCount] = useState(20);

  const [newsSearch, setNewsSearch] = useState<
    NewsSearchResponse & { isLoading: boolean }
  >({
    isLoading: false,
    message: '검색 버튼을 눌러 단계별 결과를 확인하세요.',
    raw_naver_news: [],
    filtered_news: [],
    dart_verified_news: [],
  });

  const handleNewsSearch = async () => {
    setNewsSearch({
      isLoading: true,
      message: '모든 단계 처리 중...',
      raw_naver_news: [],
      filtered_news: [],
      dart_verified_news: [],
    });
    try {
      const response = await searchNewsCandidates(newsSeconds, displayCount);
      setNewsSearch({ ...response, isLoading: false });
    } catch (error: any) {
      setNewsSearch({
        isLoading: false,
        message: `오류 발생: ${error.message}`,
        raw_naver_news: [],
        filtered_news: [],
        dart_verified_news: [],
      });
    }
  };

  return (
    <CardContent>
      <div className="space-y-4">
        <div className="flex flex-col md:flex-row md:items-center gap-4">
          <div className="flex items-center gap-2 flex-1">
            <Input
              id="news-seconds"
              type="number"
              value={newsSeconds}
              onChange={(e) => setNewsSeconds(Number(e.target.value))}
              className="w-[120] text-center"
            />
            <Label htmlFor="news-seconds" className="shrink-0">
              초전 뉴스까지
            </Label>
          </div>
          <div className="flex items-center gap-2 flex-1">
            <Label htmlFor="display-count" className="shrink-0">
              가져올 뉴스 수
            </Label>
            <Input
              id="display-count"
              type="number"
              value={displayCount}
              onChange={(e) => setDisplayCount(Number(e.target.value))}
              className="w-[120] text-center"
            />
          </div>
          <Button
            className="w-full md:w-auto font-semibold"
            onClick={handleNewsSearch}
            disabled={newsSearch.isLoading}
          >
            {newsSearch.isLoading && (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            )}
            {newsSearch.isLoading ? '검색 중...' : '검색 실행'}
          </Button>
        </div>

        <div className="mt-2 p-4 border rounded-md bg-muted/20 min-h-[200px] w-full text-sm">
          <p className="font-semibold mb-2">{newsSearch.message}</p>

          {newsSearch.isLoading === false && (
            <div className="flex flex-col gap-6">
              {/* 1. 네이버 뉴스 */}
              <div>
                <h4 className="font-bold text-base mb-2">
                  1. 네이버 뉴스 ({newsSearch.raw_naver_news.length}개)
                </h4>
                <div className="space-y-1 text-xs max-h-60 overflow-y-auto pr-2">
                  {newsSearch.raw_naver_news.length > 0 ? (
                    newsSearch.raw_naver_news.map((item, index) => (
                      <div key={`raw-${index}`} className="flex items-center">
                        <a
                          href={item.news_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="truncate text-blue-600 hover:underline"
                          title={item.news_title}
                          dangerouslySetInnerHTML={{ __html: item.news_title }}
                        />
                        <span className="text-amber-700 mx-2">|</span>
                        <span className="text-gray-700 mr-2">
                          {/* [{item.news_published.split(' ')[4]}] */}
                          [{item.news_published}]
                        </span>
                      </div>
                    ))
                  ) : (
                    <p>데이터가 없습니다.</p>
                  )}
                </div>
              </div>

              {/* 2. 필터링된 뉴스 */}
              <div>
                <h4 className="font-bold text-base mb-2">
                  2. 필터링된 뉴스 ({newsSearch.filtered_news.length}개)
                </h4>
                <div className="space-y-2 text-xs max-h-60 overflow-y-auto pr-2">
                  {newsSearch.filtered_news.length > 0 ? (
                    newsSearch.filtered_news.map((item, index) => (
                      <div key={`filtered-${index}`}>
                        <p className="font-semibold text-blue-600 truncate">
                          {item.stock_name} ({item.stock_code})
                        </p>
                        <a
                          href={item.news_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="hover:underline text-muted-foreground block truncate"
                          title={item.news_title}
                          dangerouslySetInnerHTML={{ __html: item.news_title }}
                        />
                      </div>
                    ))
                  ) : (
                    <p>데이터가 없습니다.</p>
                  )}
                </div>
              </div>

              {/* 3. DART 검증된 뉴스 */}
              <div>
                <h4 className="font-bold text-base mb-2">
                  3. DART 검증 완료 ({newsSearch.dart_verified_news.length}개)
                </h4>
                <div className="space-y-2 text-xs max-h-60 overflow-y-auto pr-2">
                  {newsSearch.dart_verified_news.length > 0 ? (
                    newsSearch.dart_verified_news.map((item, index) => (
                      <div key={`verified-${index}`}>
                        <p className="font-semibold text-green-600 truncate">
                          {item.stock_name} ({item.stock_code})
                        </p>
                        <a
                          href={item.news_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-muted-foreground hover:underline block truncate"
                          title={item.news_title}
                          dangerouslySetInnerHTML={{
                            __html: `뉴스: ${item.news_title}`,
                          }}
                        />
                        <a
                          href={item.disclosure_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center hover:underline text-foreground"
                          title={item.disclosure_report_name}
                        >
                          <CheckCircle className="w-3 h-3 mr-1 flex-shrink-0" />
                          <span className="truncate">
                            공시: {item.disclosure_report_name}
                          </span>
                        </a>
                      </div>
                    ))
                  ) : (
                    <p>데이터가 없습니다.</p>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </CardContent>
  );
};
