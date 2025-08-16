import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { HoldingItem } from '@/types/stock';
import { cn, getGainColor } from '@/lib/utils';

interface PortfolioTableProps {
  stocks: HoldingItem[];
  currency: string;
}

export const PortfolioTable = ({ stocks }: PortfolioTableProps) => {
  const formatCurrency = (value: number, market: 'KOR' | 'OVERSEAS') => {
    const currency = market === 'KOR' ? 'KRW' : 'USD';
    return value.toLocaleString(undefined, {
      style: 'currency',
      currency,
      maximumFractionDigits: 2,
    });
  };

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>종목명</TableHead>
          <TableHead className="text-right">보유수량</TableHead>
          <TableHead className="text-right">BEP단가</TableHead>
          <TableHead className="text-right">현재가</TableHead>
          <TableHead className="text-right">평가금액</TableHead>
          <TableHead className="text-right">평가손익</TableHead>
          <TableHead className="text-right">수익률</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {stocks.map((stock) => (
          <TableRow key={stock.stock_code}>
            <TableCell>
              <div className="font-medium">{stock.stock_name}</div>
              <div className="text-sm text-muted-foreground">
                {stock.stock_code}
              </div>
            </TableCell>
            <TableCell className="text-right">
              {stock.quantity.toLocaleString()}
            </TableCell>
            <TableCell className="text-right">
              {formatCurrency(stock.average_price, stock.market)}
            </TableCell>
            <TableCell className="text-right">
              {formatCurrency(stock.current_price, stock.market)}
            </TableCell>
            <TableCell className="text-right">
              {formatCurrency(stock.valuation, stock.market)}
            </TableCell>
            <TableCell
              className={cn('text-right', `${getGainColor(stock.profit_loss)}`)}
            >
              {formatCurrency(stock.profit_loss, stock.market)}
            </TableCell>
            <TableCell
              className={cn('text-right', `${getGainColor(stock.return_rate)}`)}
            >
              {stock.return_rate.toFixed(2)}%
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
