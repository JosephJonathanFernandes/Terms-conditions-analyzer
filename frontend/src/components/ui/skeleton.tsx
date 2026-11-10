import * as React from "react";
import { cn } from "@/lib/utils";

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "text" | "circular" | "block";
  className?: string;
}

const Skeleton = React.forwardRef<HTMLDivElement, SkeletonProps>(
  ({ className, variant = "text", ...props }, ref) => {
    const base = "animate-pulse rounded-md bg-gray-200";
    const variants: Record<string, string> = {
      text: "h-4 w-48",
      circular: "h-10 w-10 rounded-full",
      block: "h-full w-full",
    };
    return (
      <div
        ref={ref}
        data-testid={`skeleton-${variant}`}
        className={cn(base, variants[variant], className)}
        {...props}
      />
    );
  }
);
Skeleton.displayName = "Skeleton";

// Add data-testid to SkeletonCard's inner skeletons

export { Skeleton };

export function SkeletonText({ count = 3 }: { count?: number }) {
  return (
    <div className="space-y-3">
      {[...Array(count)].map((_, i) => (
        <Skeleton key={i} variant="text" className={i === count - 1 ? "w-2/3" : "w-full"} />
      ))}
    </div>
  );
}

export function SkeletonCard() {
  return (
    <div className="card">
      <Skeleton variant="block" className="h-8 w-1/3 mb-3" />
      <SkeletonText count={4} />
    </div>
  );
}

export function SkeletonTableRow() {
  return (
    <div className="flex items-center gap-4 py-3 border-b border-gray-100">
      <Skeleton variant="text" className="w-1/4" />
      <Skeleton variant="text" className="w-1/6" />
      <Skeleton variant="text" className="w-1/3" />
      <Skeleton variant="text" className="w-1/4" />
      <Skeleton variant="circular" />
    </div>
  );
}
