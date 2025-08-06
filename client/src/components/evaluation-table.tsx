'use client';

import React from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface EvaluationItem {
  name: string;
  score: string;
  note: string;
}

interface EvaluationCategory {
  category: string;
  items: EvaluationItem[];
}

interface EvaluationTableProps {
  data: EvaluationCategory[];
}

export function EvaluationTable({ data }: EvaluationTableProps) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-[20%] text-center font-bold">평가 항목</TableHead>
          <TableHead className="w-[35%] text-center font-bold">점수</TableHead>
          <TableHead className="w-[45%] text-center font-bold">Note</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {data.map((categoryData, index) => (
          <React.Fragment key={index}>
            {/* 카테고리 헤더 행 */}
            <TableRow className="bg-muted/50 hover:bg-muted/50">
              <TableCell colSpan={3} className="font-bold text-foreground">
                {categoryData.category}
              </TableCell>
            </TableRow>
            {/* 각 카테고리별 항목 행 */}
            {categoryData.items.map((item) => (
              <TableRow key={item.name} className="hover:bg-accent/10">
                <TableCell className="font-semibold">{item.name}</TableCell>
                <TableCell className="text-xs text-muted-foreground whitespace-pre-wrap">
                  {item.score}
                </TableCell>
                <TableCell className="text-xs text-center text-muted-foreground">
                  {item.note}
                </TableCell>
              </TableRow>
            ))}
          </React.Fragment>
        ))}
      </TableBody>
    </Table>
  );
}
