import { PortfolioItem } from "@/data/portfolio-data";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { formatCurrency, formatPercent, getGainColor } from '@/lib/utils';

export const PortfolioTable = ({
  stocks,
  currency,
}: {
  stocks: PortfolioItem[];
  currency: 'USD' | 'KRW';
}) => {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[350px]">Ticker</TableHead>
          <TableHead>Shares</TableHead>
          <TableHead className="text-right">Avg Cost</TableHead>
          <TableHead className="text-right">Price</TableHead>
          <TableHead className="text-right">Day&apos;s Gain</TableHead>
          <TableHead className="text-right">Total Gain</TableHead>
          <TableHead className="text-right">Market Value</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {stocks.map((stock) => {
          const totalGainPercent =
            (stock.totalGain / (stock.avgCost * stock.shares)) * 100;

          return (
            <TableRow key={stock.ticker}>
              <TableCell className="font-medium">
                <div>{stock.ticker}</div>
                <div className="text-xs text-muted-foreground">
                  {stock.name}
                </div>
              </TableCell>
              <TableCell>{stock.shares}</TableCell>
              <TableCell className="text-right">
                {formatCurrency(stock.avgCost, currency)}
              </TableCell>
              <TableCell className="text-right">
                {formatCurrency(stock.price)}
              </TableCell>
              <TableCell
                className={`text-right ${getGainColor(stock.daysGain)}`}
              >
                <div>{formatCurrency(stock.daysGain, currency)}</div>
                <div className="text-xs">1.1%</div>
              </TableCell>
              <TableCell
                className={`text-right ${getGainColor(stock.totalGain)}`}
              >
                <div>{formatCurrency(stock.totalGain, currency)}</div>
                <div className="text-xs">{formatPercent(totalGainPercent)}</div>
              </TableCell>
              <TableCell className="text-right font-semibold">
                {formatCurrency(stock.marketValue, currency)}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
};
