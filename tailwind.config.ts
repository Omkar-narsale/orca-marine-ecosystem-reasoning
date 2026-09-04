import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        marine: {
          950: "#06101E",
          900: "#0B192C",
          850: "#0E243F",
          800: "#132D50",
          700: "#1B3F6E",
          600: "#255694",
          500: "#3174C2",
          400: "#4B95EC",
          300: "#7DB5F5",
          200: "#B9D8FC",
          100: "#E2EEFD",
          50: "#F0F6FE",
        },
        teal: {
          50: "#F0FDFA",
          100: "#CCFBF1",
          500: "#14B8A6",
          600: "#0D9488",
          700: "#0F766E",
        },
        ocean: {
          depth: "#0A192F",
          cyan: "#00E5FF",
          emerald: "#10B981",
          amber: "#F59E0B",
          crimson: "#EF4444",
          violet: "#6366F1",
        }
      },
      fontFamily: {
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Monaco", "Consolas", "monospace"],
      },
      boxShadow: {
        'soft': '0 2px 10px rgba(11, 25, 44, 0.06)',
        'card': '0 4px 20px -2px rgba(11, 25, 44, 0.08), 0 2px 6px -1px rgba(11, 25, 44, 0.04)',
        'elevated': '0 10px 30px -5px rgba(11, 25, 44, 0.12), 0 4px 12px -2px rgba(11, 25, 44, 0.06)',
      }
    },
  },
  plugins: [],
};
export default config;
