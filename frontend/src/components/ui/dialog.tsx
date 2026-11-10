"use client";

import * as React from "react";
import { X } from "lucide-react";
interface DialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: React.ReactNode;
}

const Dialog = React.forwardRef<HTMLDivElement, DialogProps>(
  ({ open, onOpenChange, children }, ref) => {
    const handleKeyDown = (e: React.KeyboardEvent) => {
      if (e.key === "Escape") onOpenChange(false);
    };

    if (!open) return null;

    return (
      <div
        ref={ref}
        onKeyDown={handleKeyDown}
        onClick={(e) => {
          if (e.target === e.currentTarget) onOpenChange(false);
        }}
        className="fixed inset-0 z-50 flex items-center justify-center"
      >
        <div className="absolute inset-0 bg-black/40 backdrop-blur-sm" />
        <div className="relative w-full max-w-lg mx-4 transform">
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 animate-in fade-in slide-in-from-top-2 duration-200">
            <button
              onClick={() => onOpenChange(false)}
              className="absolute top-3 right-3 text-gray-500 hover:text-gray-700"
            >
              <X className="w-5 h-5" />
            </button>
            {children}
          </div>
        </div>
      </div>
    );
  }
);
Dialog.displayName = "Dialog";

export { Dialog };
