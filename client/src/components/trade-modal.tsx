'use client';

import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import { toast } from 'sonner';
import { Calendar as CalendarIcon, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Calendar } from '@/components/ui/calendar';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import { cn } from '@/lib/utils';

import { StockItem, HoldingItem, TransactionData } from '@/types/stock';
import { getHolding, getStockPrice, postTrade } from '@/lib/api';

import {
  TRADING_FEES,
  KOREA_SECURITIES_TAX_RATE,
} from '@/data/securites_trading_fee';

interface TradeModalProps {
  isOpen: boolean;
  onOpenChange: (open: boolean) => void;
  stock: (StockItem & { market: 'KOR' | 'OVERSEAS' }) | null;
  onTradeComplete: () => void;
}

export function TradeModal({
  isOpen,
  onOpenChange,
  stock,
  onTradeComplete,
}: TradeModalProps) {
  const [holding, setHolding] = useState<HoldingItem | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPrice, setCurrentPrice] = useState('0');

  const [transactionDate, setTransactionDate] = useState<Date>(new Date());
  const [quantity, setQuantity] = useState('');
  const [price, setPrice] = useState('');

  const [commission, setCommission] = useState(0);
  const [tax, setTax] = useState(0);
  const [totalAmount, setTotalAmount] = useState(0);
  const [commissionRate, setCommissionRate] = useState(0);

  // --- 🌟 2. market(KOR/OVERSEAS)에 따라 TRADING_FEES 객체를 사용하여 올바른 수수료/세금을 적용하는 로직 ---
  useEffect(() => {
    if (!stock) return;

    const numPrice = parseFloat(price) || 0;
    const numQuantity = parseFloat(quantity) || 0;
    const baseAmount = numPrice * numQuantity;

    let applicableCommissionRate = 0;
    let applicableTax = 0;

    // 시장(market)에 따라 올바른 수수료율과 세금 정책을 선택
    if (stock.market === 'KOR') {
      applicableCommissionRate = TRADING_FEES.DOMESTIC_FEE.buy_commission_rate;
      applicableTax = 0; // 국내 주식 매수 시 거래세 0%
    } else if (stock.market === 'OVERSEAS') {
      applicableCommissionRate = TRADING_FEES.OVERSEAS_FEE.buy_commission_rate;
      applicableTax = 0; // 해외 주식 매수 시 거래세 0
    }

    // 계산된 값을 상태에 업데이트
    const calculatedCommission = baseAmount * applicableCommissionRate;
    setCommissionRate(applicableCommissionRate);
    setCommission(calculatedCommission);
    setTax(applicableTax);
    setTotalAmount(baseAmount + calculatedCommission);
  }, [price, quantity, stock]); // stock이 바뀔 때도 재계산하도록 의존성 배열에 추가

  useEffect(() => {
    async function loadData() {
      if (!stock) return;
      setIsLoading(true);
      setQuantity('');
      setPrice('');
      setTransactionDate(new Date());

      const holdingData = await getHolding(stock.code);
      setHolding(holdingData);

      const priceData = await getStockPrice(stock.market, stock.code);
      setCurrentPrice(priceData.price);
      setPrice(priceData.price === 'N/A' ? '' : priceData.price);

      setIsLoading(false);
    }
    if (isOpen) {
      loadData();
    }
  }, [isOpen, stock]);

  const handleBuy = async () => {
    if (!stock || !quantity || !price) {
      toast.error('수량과 가격을 모두 입력해주세요.');
      return;
    }
    try {
      const tradeData: TransactionData = {
        stock_code: stock.code,
        stock_name: stock.name,
        market: stock.market,
        transaction_type: 'BUY',
        quantity: parseFloat(quantity),
        price: parseFloat(price),
        transaction_date: format(transactionDate, 'yyyy-MM-dd'),
      };
      await postTrade(tradeData);

      toast.success(`${stock.name} 매수가 완료되었습니다.`, {
        description: `${quantity}주를 ${parseFloat(
          price
        ).toLocaleString()}에 매수했습니다.`,
        action: {
          label: '확인',
          onClick: () => console.log('Toast dismissed'),
        },
      });

      onTradeComplete();
      onOpenChange(false);
    } catch (error) {
      console.error(error);
      
      toast.error('매수 처리 중 오류가 발생했습니다.', {
        description:
          error instanceof Error ? error.message : '잠시 후 다시 시도해주세요.',
      });
    }
  };

  const renderContent = () => {
    if (isLoading) {
      return (
        <div className="flex justify-center items-center h-48">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      );
    }

    if (holding) {
      return <div>보유 중인 주식입니다. (매도/추가매수 화면 구현 필요)</div>;
    }

    const currency = stock?.market === 'OVERSEAS' ? 'USD' : 'KRW';

    return (
      <div className="space-y-4 pt-4">
        {/* 매수일자 */}
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="date" className="text-right">
            매수일자
          </Label>
          <Popover>
            <PopoverTrigger asChild>
              <Button
                variant={'outline'}
                className={cn(
                  'col-span-3 justify-start text-left font-normal',
                  !transactionDate && 'text-muted-foreground'
                )}
              >
                <CalendarIcon className="mr-2 h-4 w-4" />
                {transactionDate ? (
                  format(transactionDate, 'PPP')
                ) : (
                  <span>날짜 선택</span>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-auto p-0">
              <Calendar
                mode="single"
                selected={transactionDate}
                onSelect={(date) => setTransactionDate(date || new Date())}
                initialFocus
              />
            </PopoverContent>
          </Popover>
        </div>
        {/* 매수가격 */}
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="price" className="text-right">
            매수가격
          </Label>
          <Input
            id="price"
            type="number"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            placeholder={`현재가: ${parseFloat(currentPrice).toLocaleString()}`}
            className="col-span-3"
          />
        </div>
        {/* 매수수량 */}
        <div className="grid grid-cols-4 items-center gap-4">
          <Label htmlFor="quantity" className="text-right">
            매수수량
          </Label>
          <Input
            id="quantity"
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            className="col-span-3"
          />
        </div>
        <hr className="my-4" />
        {/* 자동계산 영역 */}
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">
              수수료 ({(commissionRate * 100).toFixed(4)}%)
            </span>
            <span>
              {commission.toLocaleString(undefined, {
                style: 'currency',
                currency,
                maximumFractionDigits: 0,
              })}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">거래세 (매수 시 0%)</span>
            <span>
              {tax.toLocaleString(undefined, {
                style: 'currency',
                currency,
                maximumFractionDigits: 0,
              })}
            </span>
          </div>
          <div className="flex justify-between font-bold text-base">
            <span>총 매수금액</span>
            <span>
              {totalAmount.toLocaleString(undefined, {
                style: 'currency',
                currency,
                maximumFractionDigits: 0,
              })}
            </span>
          </div>
        </div>

        <DialogFooter className="pt-4">
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            취소
          </Button>
          <Button onClick={handleBuy}>매수</Button>
        </DialogFooter>
      </div>
    );
  };

  if (!stock) return null;

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {stock.name} ({stock.code})
          </DialogTitle>
          <DialogDescription>신규 매수</DialogDescription>
        </DialogHeader>
        {renderContent()}
      </DialogContent>
    </Dialog>
  );
}
