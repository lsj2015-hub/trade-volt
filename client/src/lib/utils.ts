import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

// 숫자에 따라 텍스트 색상을 반환하는 헬퍼 함수
export const getGainColor = (value: number) =>
  value >= 0 ? 'text-green-600' : 'text-red-600';