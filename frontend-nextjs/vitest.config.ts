/// <reference types="vitest" />

import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  test: {
    setupFiles: ["./vitest.setup.ts"],
    globals: true,
    environment: "jsdom",
    include: ["__tests__/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}"],
    css: true,
    coverage: {
      // you can include other reporters, but 'json-summary' is required, json is recommended
      reporter: ["text", "json-summary", "json"],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src/"),
    },
  },
});
