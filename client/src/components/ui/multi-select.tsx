'use client';

import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { X } from 'lucide-react';

import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';
import {
  Command,
  CommandGroup,
  CommandItem,
  CommandList,
} from '@/components/ui/command';
import { Button } from './button';
import { Option } from '../../types/type';

const multiSelectVariants = cva(
  'flex items-center justify-between rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
  {
    variants: {
      variant: {
        default: 'h-10',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

interface MultiSelectProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof multiSelectVariants> {
  options: Option[];
  onValueChange: (value: string[]) => void;
  defaultValue: string[];
  placeholder?: string;
}

const MultiSelect = React.forwardRef<HTMLButtonElement, MultiSelectProps>(
  (
    {
      options,
      onValueChange,
      variant,
      defaultValue = [],
      placeholder = 'Select options',
      className,
      ...props
    },
    ref
  ) => {
    const [selectedValues, setSelectedValues] =
      React.useState<string[]>(defaultValue);
    const [isPopoverOpen, setIsPopoverOpen] = React.useState(false);

    // --- 컴포넌트 외부 클릭 감지를 위한 ref 추가 ---
    const popoverRef = React.useRef<HTMLDivElement>(null);

    React.useEffect(() => {
      setSelectedValues(defaultValue);
    }, [defaultValue]);

    // --- 외부 클릭 시 드롭다운을 닫는 로직 ---
    React.useEffect(() => {
      function handleClickOutside(event: MouseEvent) {
        if (
          popoverRef.current &&
          !popoverRef.current.contains(event.target as Node)
        ) {
          setIsPopoverOpen(false);
        }
      }
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }, [popoverRef]);

    const handleSelect = (value: string) => {
      const newSelectedValues = selectedValues.includes(value)
        ? selectedValues.filter((v) => v !== value)
        : [...selectedValues, value];
      setSelectedValues(newSelectedValues);
      onValueChange(newSelectedValues);
    };

    const handleDeselect = (value: string) => {
      const newSelectedValues = selectedValues.filter((v) => v !== value);
      setSelectedValues(newSelectedValues);
      onValueChange(newSelectedValues);
    };

    return (
      // --- ref를 div에 연결 ---
      <div className="relative" ref={popoverRef}>
        <Button
          ref={ref}
          {...props}
          onClick={() => setIsPopoverOpen((prev) => !prev)}
          className={cn(multiSelectVariants({ variant, className }))}
        >
          <div className="flex w-full items-center justify-between">
            <div className="flex flex-wrap items-center gap-2">
              {selectedValues.length > 0 ? (
                selectedValues.map((value) => {
                  const option = options.find((o) => o.value === value);
                  return (
                    <Badge
                      key={value}
                      variant="secondary"
                      className="px-2 py-1"
                      onClick={(e) => e.stopPropagation()} // 뱃지 클릭이 버튼으로 전파되는 것을 막음
                    >
                      {option?.label}
                      <X
                        className="ml-2 h-4 w-4 cursor-pointer"
                        onClick={(e) => {
                          e.stopPropagation(); // X 아이콘 클릭이 뱃지로 전파되는 것을 막음
                          handleDeselect(value);
                        }}
                      />
                    </Badge>
                  );
                })
              ) : (
                <span className="text-muted-foreground">{placeholder}</span>
              )}
            </div>
          </div>
        </Button>
        {isPopoverOpen && (
          <Command className="absolute top-full z-10 mt-2 w-full h-50 rounded-md border bg-popover text-popover-foreground shadow-md">
            <CommandList>
              <CommandGroup>
                {options.map((option) => (
                  <CommandItem
                    key={option.value}
                    onSelect={() => handleSelect(option.value)}
                    className={cn(
                      'cursor-pointer',
                      selectedValues.includes(option.value) &&
                        'bg-accent text-accent-foreground'
                    )}
                  >
                    {option.label}
                  </CommandItem>
                ))}
              </CommandGroup>
            </CommandList>
          </Command>
        )}
      </div>
    );
  }
);

MultiSelect.displayName = 'MultiSelect';
export { MultiSelect };
