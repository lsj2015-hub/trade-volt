import { PortfolioItem } from "@/data/portfolio-data";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { getGainColor } from "@/lib/utils";

export const PortfolioTable = ({
  stocks,
  currency,
}: {
  stocks: PortfolioItem[];
  currency: 'USD' | 'KRW';
}) => {
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat(currency === 'KRW' ? 'ko-KR' : 'en-US', {
      style: 'currency',
      currency,
    }).format(value);
  };

  const formatPercent = (value: number) =>
    `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`;

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[150px]">Ticker</TableHead>
          <TableHead>Shares</TableHead>
          <TableHead className="text-right">Avg Cost / Share</TableHead>
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
                {formatCurrency(stock.avgCost)}
              </TableCell>
              <TableCell className="text-right">
                {formatCurrency(stock.price)}
              </TableCell>
              <TableCell
                className={`text-right ${getGainColor(stock.daysGain)}`}
              >
                {formatCurrency(stock.daysGain)}
              </TableCell>
              <TableCell
                className={`text-right ${getGainColor(stock.totalGain)}`}
              >
                <div>{formatCurrency(stock.totalGain)}</div>
                <div className="text-xs">{formatPercent(totalGainPercent)}</div>
              </TableCell>
              <TableCell className="text-right font-semibold">
                {formatCurrency(stock.marketValue)}
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
};
