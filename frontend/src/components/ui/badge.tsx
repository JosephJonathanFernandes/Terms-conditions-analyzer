import * as React from "react";

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "secondary" | "destructive" | "outline";
}

const Badge = React.forwardRef<HTMLDivElement, BadgeProps>(
  ({ className, variant = "default", ...props }, ref) => {
    const variants: Record<string, string> = {
      default: "bg-blue-100 text-blue-800",
      secondary: "bg-gray-100 text-gray-800",
      destructive: "bg-red-100 text-red-800",
      outline: "border border-gray-300",
    };
    return (
      <div
        ref={ref}
        className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${variants[variant]} ${className || ""}`}
        {...props}
      />
    );
  }
);
Badge.displayName = "Badge";

export { Badge };
