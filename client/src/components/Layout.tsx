'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Bell,
  Search,
  LayoutDashboard,
  ListFilter,
  BrainCircuit,
  History,
  FlaskConical,
  Zap,
  Building2,
  ChartBarStacked,
} from 'lucide-react';

import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { SearchModal } from './search-modal';
import { StockItem } from '@/types/stock';
import { TradeModal } from './trade-modal';
import { usePortfolio } from '@/context/PortfolioContext';

const menuItems = [
  { name: 'My Portfolio', href: '/', icon: LayoutDashboard },
  { name: 'Stock Analysis', href: '/stock-analysis', icon: Building2 },
  { name: 'Stock Screener', href: '/screener', icon: ListFilter },
  { name: 'Trading strategy', href: '/strategy', icon: BrainCircuit },
  {
    name: 'Benchmark Analysis',
    href: '/benchmark-analysis',
    icon: ChartBarStacked,
  },
  { name: 'Stratege Backtest', href: '/backtest', icon: History },
  { name: 'Something to do', href: '/something', icon: FlaskConical },
];

// 상단 메뉴바 컴포넌트
const Header = ({ onSearchClick }: { onSearchClick: () => void }) => {
  return (
    <header className="h-16 flex items-center justify-between px-6 bg-card border-b">
      {/* 검색창 */}
      <div className="relative w-full max-w-sm">
        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground cursor-pointer"
          onClick={onSearchClick} // 클릭 시 모달을 열도록 함수 연결
        />
        <Input
          placeholder="Search for stocks and more"
          className="pl-10"
          onFocus={onSearchClick} // 입력창 포커스 시에도 모달 열기
        />
      </div>

      {/* 사용자 정보 및 알림 */}
      <div className="flex items-center gap-4">
        {/* hover:bg-gray-100 -> hover:bg-muted로 변경 */}
        <button className="p-2 rounded-full hover:bg-muted transition-colors">
          {/* text-gray-600 -> text-muted-foreground로 변경 */}
          <Bell className="h-6 w-6 text-muted-foreground" />
        </button>
        <Avatar className="h-9 w-9">
          <AvatarImage src="https://github.com/shadcn.png" alt="@shadcn" />
          <AvatarFallback>M</AvatarFallback>
        </Avatar>
      </div>
    </header>
  );
};

// 사이드바 컴포넌트
const Sidebar = () => {
  const pathname = usePathname();

  return (
    <aside className="w-64 flex-shrink-0 bg-card border-r flex-col hidden md:flex">
      <div className="h-16 flex items-center justify-center border-b">
        <Link href="/" className="flex items-center gap-2">
          <Zap className="h-7 w-7 text-primary" />
          <h1 className="text-2xl font-bold text-foreground">Trade Volt</h1>
        </Link>
      </div>
      <nav className="flex-1 px-4 py-6">
        <ul>
          {menuItems.map((item) => {
            const Icon = item.icon;
            return (
              <li key={item.name} className="mb-2">
                <Link
                  href={item.href}
                  // 활성화/비활성화 스타일에 테마 색상을 적용합니다.
                  className={`flex items-center gap-3 px-4 py-2.5 text-sm font-medium rounded-lg transition-colors ${
                    pathname === item.href
                      ? 'bg-primary text-primary-foreground shadow-sm'
                      : 'text-muted-foreground hover:bg-muted/50'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </aside>
  );
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  // Search Modal 상태
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  // Trade Modal 상태
  const [isTradeModalOpen, setIsTradeModalOpen] = useState(false);
  const [selectedStock, setSelectedStock] = useState<
    (StockItem & { market: 'KOR' | 'OVERSEAS' }) | null
  >(null);

  // --- Context로부터 포트폴리오 새로고침 함수를 가져옵니다. ---
  const { fetchPortfolioData } = usePortfolio();

  // --- 🌟 SearchModal에서 종목 클릭 시 호출될 함수 ---
  const handleStockSelect = (stock: StockItem, market: 'KOR' | 'OVERSEAS') => {
    setSelectedStock({ ...stock, market });
    setIsSearchOpen(false); // 검색 모달 닫기
    setIsTradeModalOpen(true); // 거래 모달 열기
  };

  // --- 🌟 3. 거래 완료 시 호출될 함수는 이제 Context의 함수를 실행합니다. ---
  const handleTradeComplete = () => {
    fetchPortfolioData(); // 전역 데이터를 새로고침
  };

  return (
    // 전체 레이아웃에 테마의 배경색과 글자색을 적용합니다.
    <div className="flex h-screen bg-background text-foreground">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header onSearchClick={() => setIsSearchOpen(true)} />
        <main id="main-scroll-area" className="flex-1 overflow-y-auto">
          {children}
        </main>
        {/* 🌟 onStockSelect prop을 SearchModal에 전달 */}
        <SearchModal
          isOpen={isSearchOpen}
          onOpenChange={setIsSearchOpen}
          onStockSelect={handleStockSelect}
        />

        {/* 🌟 TradeModal 렌더링 */}
        <TradeModal
          isOpen={isTradeModalOpen}
          onOpenChange={setIsTradeModalOpen}
          stock={selectedStock}
          onTradeComplete={handleTradeComplete}
        />
      </div>
    </div>
  );
}
