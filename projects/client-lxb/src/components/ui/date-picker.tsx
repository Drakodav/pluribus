import * as React from "react";
import { Calendar as CalendarIcon, X, Sparkles } from "lucide-react";
import { Popover, PopoverContent, PopoverTrigger } from "./popover";
import { Calendar } from "./calendar";
import { Badge } from "./badge";
import { cn } from "@/lib/utils";

export interface DatePickerProps {
  id?: string;
  name?: string;
  value?: string; // YYYY-MM-DD
  onChange?: (dateString: string) => void;
  placeholder?: string;
  className?: string;
  minDate?: Date;
  disabled?: boolean;
}

// Convert YYYY-MM-DD string to local Date object
function parseIsoDate(val?: string): Date | null {
  if (!val) return null;
  const parts = val.split("-");
  if (parts.length !== 3) return null;
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1;
  const day = parseInt(parts[2], 10);
  if (isNaN(year) || isNaN(month) || isNaN(day)) return null;
  return new Date(year, month, day);
}

// Format local Date object to YYYY-MM-DD
function formatToIso(date: Date): string {
  const y = date.getFullYear();
  const m = String(date.getMonth() + 1).padStart(2, "0");
  const d = String(date.getDate()).padStart(2, "0");
  return `${y}-${m}-${d}`;
}

// Format for luxury UI presentation: "Saturday, 14 Nov 2026"
function formatDisplayDate(date: Date): string {
  return date.toLocaleDateString("en-IE", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

// Calculate relative badge text ("In 5 days", "This Saturday", etc.)
function getRelativeDescription(targetDate: Date): string {
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(targetDate.getFullYear(), targetDate.getMonth(), targetDate.getDate());
  const diffTime = target.getTime() - today.getTime();
  const diffDays = Math.round(diffTime / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "Today";
  if (diffDays === 1) return "Tomorrow";
  if (diffDays > 1 && diffDays < 7) {
    return target.toLocaleDateString("en-IE", { weekday: "long" });
  }
  if (diffDays >= 7 && diffDays < 14) return "In ~1 week";
  if (diffDays >= 14 && diffDays < 30) return `In ${Math.round(diffDays / 7)} weeks`;
  if (diffDays >= 30) return `In ${Math.round(diffDays / 30)} month(s)`;
  return "";
}

export function DatePicker({
  id,
  name,
  value,
  onChange,
  placeholder = "Select celebration date...",
  className,
  minDate = new Date(), // Defaults to today (no dates in past)
  disabled = false,
}: DatePickerProps) {
  const [open, setOpen] = React.useState(false);

  const selectedDate = React.useMemo(() => parseIsoDate(value), [value]);

  const handleSelectDate = (date: Date | null) => {
    if (date) {
      onChange?.(formatToIso(date));
    } else {
      onChange?.("");
    }
    setOpen(false);
  };

  const handleClear = (e: React.MouseEvent) => {
    e.stopPropagation();
    onChange?.("");
  };

  // Shortcut helpers
  const getUpcomingSaturday = (weeksAhead = 0): Date => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    const dayOfWeek = d.getDay(); // 0 is Sunday, 6 is Saturday
    const daysUntilSaturday = (6 - dayOfWeek + 7) % 7 || 7;
    d.setDate(d.getDate() + daysUntilSaturday + weeksAhead * 7);
    return d;
  };

  const getDaysAhead = (days: number): Date => {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + days);
    return d;
  };

  const shortcuts = [
    { label: "This Sat", date: getUpcomingSaturday(0) },
    { label: "Next Sat", date: getUpcomingSaturday(1) },
    { label: "In 2 Wks", date: getDaysAhead(14) },
    { label: "In 1 Mo", date: getDaysAhead(30) },
  ];

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <div className={cn("relative flex w-full items-center", className)}>
        <PopoverTrigger
          id={id}
          type="button"
          disabled={disabled}
          className={cn(
            "flex h-11 w-full items-center justify-between rounded-2xl border border-border bg-card px-4 text-left text-sm text-foreground shadow-xs transition-colors outline-none",
            "hover:border-primary/50 focus-visible:border-primary focus-visible:ring-3 focus-visible:ring-primary/20",
            !selectedDate && "text-muted-foreground",
            disabled && "opacity-50 cursor-not-allowed",
          )}
        >
          <span className="flex items-center gap-2.5 truncate">
            <CalendarIcon className="h-4 w-4 text-primary shrink-0" />
            {selectedDate ? (
              <span className="font-medium text-foreground truncate">
                {formatDisplayDate(selectedDate)}
              </span>
            ) : (
              <span className="text-muted-foreground truncate">{placeholder}</span>
            )}
          </span>

          <div className="flex items-center gap-1.5 shrink-0 ml-2">
            {selectedDate && (
              <>
                <Badge
                  variant="outline"
                  className="text-[10px] px-2 py-0.5 border-primary/30 text-primary bg-primary/5"
                >
                  {getRelativeDescription(selectedDate)}
                </Badge>
                <span
                  role="button"
                  tabIndex={0}
                  onClick={handleClear}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      onChange?.("");
                    }
                  }}
                  title="Clear date"
                  className="flex h-5 w-5 items-center justify-center rounded-full text-muted-foreground hover:bg-muted hover:text-foreground cursor-pointer"
                >
                  <X className="h-3 w-3" />
                </span>
              </>
            )}
          </div>
        </PopoverTrigger>
      </div>

      <PopoverContent align="start" className="w-auto p-4 space-y-3">
        {/* Quick Shortcuts Bar */}
        <div className="flex items-center justify-between gap-1 pb-2 border-b border-border/50">
          <span className="text-[11px] font-semibold text-muted-foreground uppercase tracking-wider flex items-center gap-1">
            <Sparkles className="h-3 w-3 text-primary" /> Shortcuts:
          </span>
          <div className="flex items-center gap-1">
            {shortcuts.map((sc) => (
              <button
                key={sc.label}
                type="button"
                onClick={() => handleSelectDate(sc.date)}
                className="rounded-full px-2 py-1 text-[11px] font-medium bg-muted text-muted-foreground hover:bg-primary/10 hover:text-primary transition-colors"
              >
                {sc.label}
              </button>
            ))}
          </div>
        </div>

        {/* Calendar Picker Component */}
        <Calendar value={selectedDate} onChange={handleSelectDate} minDate={minDate} />

        {/* Helpful Advance Notice Note */}
        <div className="pt-2 border-t border-border/50 text-[11px] text-muted-foreground leading-tight flex items-center justify-between">
          <span>✨ Handcrafted to order</span>
          <button
            type="button"
            onClick={() => handleSelectDate(new Date())}
            className="text-primary hover:underline font-medium"
          >
            Today
          </button>
        </div>
      </PopoverContent>
    </Popover>
  );
}
