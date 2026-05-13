/// <reference types="vitest" />
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        subway: {
          blue: "#0039A6",
          yellow: "#FCCC0A",
          ink: "#0B1B3F",
        },
      },
    },
  },
  plugins: [],
};

export default config;
