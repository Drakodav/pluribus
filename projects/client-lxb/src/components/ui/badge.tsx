import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-xs font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border border-transparent bg-primary text-primary-foreground shadow-sm",
        secondary: "border border-border/60 bg-secondary text-secondary-foreground",
        outline: "border border-border text-foreground bg-background/80 backdrop-blur-xs",
        champagne: "border border-primary/20 bg-primary/10 text-primary font-semibold shadow-xs",
        blush:
          "border border-border/80 bg-secondary text-secondary-foreground font-semibold shadow-xs",
        seasonal:
          "border border-primary/30 bg-primary/15 text-foreground font-semibold shadow-xs ring-1 ring-primary/20",
        destructive: "border border-transparent bg-destructive/10 text-destructive",
      },
      size: {
        default: "px-3 py-1 text-xs",
        sm: "px-2.5 py-0.5 text-[11px]",
        lg: "px-4 py-1.5 text-sm",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div data-slot="badge" className={cn(badgeVariants({ variant, size }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
