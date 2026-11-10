import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
    setupFiles: "./src/tests/setup.ts",
    include: ["src/tests/**/*.test.tsx", "src/tests/**/*.test.ts", "src/components/__tests__/**/*.test.tsx", "src/components/__tests__/**/*.test.ts"],
  },
});
