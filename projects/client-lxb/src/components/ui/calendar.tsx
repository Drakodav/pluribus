import * as React from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";

export interface CalendarProps {
  value?: Date | null;
  onChange?: (date: Date | null) => void;
  disabledDate?: (date: Date) => boolean;
  minDate?: Date;
  className?: string;
}

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

export function Calendar({ value, onChange, disabledDate, minDate, className }: CalendarProps) {
  // Current viewing month/year state
  const [viewDate, setViewDate] = React.useState<Date>(() => value || new Date());

  const currentYear = viewDate.getFullYear();
  const currentMonth = viewDate.getMonth();

  // Keep viewDate in sync if value changes externally
  React.useEffect(() => {
    if (value) {
      setViewDate(new Date(value.getFullYear(), value.getMonth(), 1));
    }
  }, [value]);

  const goToPrevMonth = () => {
    setViewDate(new Date(currentYear, currentMonth - 1, 1));
  };

  const goToNextMonth = () => {
    setViewDate(new Date(currentYear, currentMonth + 1, 1));
  };

  // Check if a date is disabled
  const isDateDisabled = (d: Date): boolean => {
    if (minDate) {
      const minStart = new Date(minDate.getFullYear(), minDate.getMonth(), minDate.getDate());
      const testStart = new Date(d.getFullYear(), d.getMonth(), d.getDate());
      if (testStart < minStart) return true;
    }
    if (disabledDate && disabledDate(d)) return true;
    return false;
  };

  // Generate calendar days
  const firstDayOfMonth = new Date(currentYear, currentMonth, 1);
  const lastDayOfMonth = new Date(currentYear, currentMonth + 1, 0);

  // Day of week index (0 = Monday in standard European/Irish business calendar)
  const startingDayIndex = (firstDayOfMonth.getDay() + 6) % 7;
  const totalDays = lastDayOfMonth.getDate();

  // Days from previous month to pad grid
  const prevMonthLastDay = new Date(currentYear, currentMonth, 0).getDate();
  const paddingPrevDays: number[] = [];
  for (let i = startingDayIndex - 1; i >= 0; i--) {
    paddingPrevDays.push(prevMonthLastDay - i);
  }

  // Days of current month
  const monthDays: number[] = [];
  for (let d = 1; d <= totalDays; d++) {
    monthDays.push(d);
  }

  // Days from next month to fill remaining row (up to multiple of 7)
  const remainingCells = (7 - ((paddingPrevDays.length + monthDays.length) % 7)) % 7;
  const paddingNextDays: number[] = [];
  for (let d = 1; d <= remainingCells; d++) {
    paddingNextDays.push(d);
  }

  const today = new Date();
  const isToday = (d: Date) =>
    d.getDate() === today.getDate() &&
    d.getMonth() === today.getMonth() &&
    d.getFullYear() === today.getFullYear();

  const isSelected = (d: Date) =>
    value != null &&
    d.getDate() === value.getDate() &&
    d.getMonth() === value.getMonth() &&
    d.getFullYear() === value.getFullYear();

  // Check if prev button should be disabled (cannot go earlier than minDate month)
  const canGoPrev = React.useMemo(() => {
    if (!minDate) return true;
    const prevMonthEnd = new Date(currentYear, currentMonth, 0);
    const minStart = new Date(minDate.getFullYear(), minDate.getMonth(), 1);
    return prevMonthEnd >= minStart;
  }, [minDate, currentYear, currentMonth]);

  return (
    <div className={cn("w-[300px] select-none p-1", className)}>
      {/* Month / Year Navigation */}
      <div className="flex items-center justify-between pb-3">
        <button
          type="button"
          onClick={goToPrevMonth}
          disabled={!canGoPrev}
          aria-label="Previous month"
          className="flex h-8 w-8 items-center justify-center rounded-full text-foreground/70 transition-colors hover:bg-muted hover:text-foreground disabled:opacity-20 disabled:pointer-events-none"
        >
          <ChevronLeft className="h-4 w-4" />
        </button>

        <span className="text-sm font-semibold text-foreground">
          {MONTHS[currentMonth]} {currentYear}
        </span>

        <button
          type="button"
          onClick={goToNextMonth}
          aria-label="Next month"
          className="flex h-8 w-8 items-center justify-center rounded-full text-foreground/70 transition-colors hover:bg-muted hover:text-foreground"
        >
          <ChevronRight className="h-4 w-4" />
        </button>
      </div>

      {/* Weekday Labels */}
      <div className="grid grid-cols-7 mb-2 text-center">
        {WEEKDAYS.map((day) => (
          <span
            key={day}
            className="text-[11px] font-medium tracking-wide uppercase text-muted-foreground"
          >
            {day}
          </span>
        ))}
      </div>

      {/* Days Grid */}
      <div className="grid grid-cols-7 gap-1 text-center">
        {/* Previous Month Padding */}
        {paddingPrevDays.map((d) => (
          <span
            key={`prev-${d}`}
            className="flex h-9 w-9 items-center justify-center text-xs text-muted-foreground/30 pointer-events-none"
          >
            {d}
          </span>
        ))}

        {/* Current Month Days */}
        {monthDays.map((d) => {
          const dateObj = new Date(currentYear, currentMonth, d);
          const disabled = isDateDisabled(dateObj);
          const selected = isSelected(dateObj);
          const currentDay = isToday(dateObj);

          return (
            <button
              key={`day-${d}`}
              type="button"
              disabled={disabled}
              onClick={() => onChange?.(dateObj)}
              className={cn(
                "flex h-9 w-9 items-center justify-center rounded-full text-xs transition-all duration-150 outline-none",
                selected
                  ? "bg-primary text-primary-foreground font-semibold shadow-xs ring-2 ring-primary/30"
                  : currentDay
                    ? "border border-primary/50 font-semibold text-primary hover:bg-primary/10"
                    : "text-foreground hover:bg-muted active:scale-95",
                disabled &&
                  "opacity-25 pointer-events-none cursor-not-allowed text-muted-foreground",
              )}
            >
              {d}
            </button>
          );
        })}

        {/* Next Month Padding */}
        {paddingNextDays.map((d) => (
          <span
            key={`next-${d}`}
            className="flex h-9 w-9 items-center justify-center text-xs text-muted-foreground/30 pointer-events-none"
          >
            {d}
          </span>
        ))}
      </div>
    </div>
  );
}
