'use client';

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
import { useState } from 'react';

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
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  return (
    // 전체 레이아웃에 테마의 배경색과 글자색을 적용합니다.
    <div className="flex h-screen bg-background text-foreground">
      <Sidebar />
      <div className="flex flex-1 flex-col">
        <Header onSearchClick={() => setIsSearchOpen(true)} />
        <main id="main-scroll-area" className="flex-1 overflow-y-auto">
          {children}
        </main>
        {/* SearchModal 컴포넌트 렌더링 */}
        <SearchModal isOpen={isSearchOpen} onOpenChange={setIsSearchOpen} />
      </div>
    </div>
  );
}
