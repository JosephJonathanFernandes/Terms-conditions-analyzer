"use strict";

import { toast as sonner } from "sonner";

export function useToast() {
  return {
    toast: sonner,
  };
}

export const toast = {
  success: (message: string, opts?: Parameters<typeof sonner>[1]) =>
    sonner.success(message, { ...opts, className: "text-navy-900" }),
  error: (message: string, opts?: Parameters<typeof sonner>[1]) =>
    sonner.error(message, { ...opts, className: "text-navy-900" }),
  warning: (message: string, opts?: Parameters<typeof sonner>[1]) =>
    sonner.warning(message, { ...opts, className: "text-navy-900" }),
  info: (message: string, opts?: Parameters<typeof sonner>[1]) =>
    sonner.info(message, { ...opts, className: "text-navy-900" }),
  promise: <T,>(
    promise: Promise<T>,
    messages: {
      loading: string;
      success: string | ((data: T) => string);
      error: string | ((error: unknown) => string);
    },
    opts?: Parameters<typeof sonner>[1]
  ) =>
    sonner.promise(promise, {
      ...messages,
      ...opts,
      className: "text-navy-900",
    }),
};

export type ToastType = "success" | "error" | "warning" | "info";
