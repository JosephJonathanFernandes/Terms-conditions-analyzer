import * as React from "react";

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}
const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={`rounded-xl border border-gray-200 bg-white shadow-sm ${className || ""}`}
      {...props}
    />
  )
);
Card.displayName = "Card";

export interface CardContentProps extends React.HTMLAttributes<HTMLDivElement> {}
const CardContent = React.forwardRef<HTMLDivElement, CardContentProps>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={`py-6 px-6 ${className || ""}`} {...props} />
  )
);
CardContent.displayName = "CardContent";

export { Card, CardContent };
