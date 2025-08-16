import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 숫자에 따라 텍스트 색상을 반환하는 헬퍼 함수
export const getGainColor = (value: number) =>
  value >= 0 ? 'text-green-600' : 'text-red-600';

/**
 * 숫자를 지정된 통화 형식의 문자열로 변환합니다.
 * @param value 포맷팅할 숫자
 * @param currency 통화 코드 ('KRW' 또는 'USD')
 * @returns 통화 기호와 3자리 콤마가 포함된 문자열 (예: "₩1,000" 또는 "$10.50")
 */
export const formatCurrency = (
  value: number,
  currency: 'USD' | 'KRW' = 'KRW'
): string => {
  return new Intl.NumberFormat(currency === 'KRW' ? 'ko-KR' : 'en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: currency === 'KRW' ? 0 : 2,
    maximumFractionDigits: 2,
  }).format(value);
};

export const formatPercent = (value: number) => `${value.toFixed(2)}%`;