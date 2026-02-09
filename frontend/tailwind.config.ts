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
        // Midnight Aurora Theme
        primary: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
          800: "#065f46",
          900: "#064e3b",
        },
        accent: {
          blue: "#3b82f6",
          amber: "#f59e0b",
          violet: "#8b5cf6",
          rose: "#f43f5e",
        },
        aurora: {
          emerald: "#10b981",
          teal: "#14b8a6",
          blue: "#3b82f6",
          sky: "#0ea5e9",
        },
        dark: {
          950: "#030712",
          900: "#050a15",
          800: "#0a1628",
          700: "#0f1f3d",
          600: "#172554",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "-apple-system", "sans-serif"],
        display: ["Inter", "system-ui", "sans-serif"],
      },
      boxShadow: {
        glass: "0 8px 32px 0 rgba(0, 0, 0, 0.36), inset 0 1px 0 rgba(255,255,255,0.05)",
        "glow-emerald": "0 0 20px rgba(16, 185, 129, 0.4), 0 0 40px rgba(16, 185, 129, 0.2)",
        "glow-blue": "0 0 20px rgba(59, 130, 246, 0.4), 0 0 40px rgba(59, 130, 246, 0.2)",
        "glow-amber": "0 0 20px rgba(245, 158, 11, 0.4), 0 0 40px rgba(245, 158, 11, 0.2)",
        "3d": "0 20px 40px -10px rgba(0, 0, 0, 0.5), 0 8px 16px -6px rgba(0, 0, 0, 0.3)",
        "3d-hover": "0 30px 60px -15px rgba(0, 0, 0, 0.5), 0 0 40px rgba(16, 185, 129, 0.15)",
        "depth": "0 1px 2px rgba(0,0,0,0.3), 0 4px 8px rgba(0,0,0,0.2), 0 12px 24px rgba(0,0,0,0.15)",
      },
      backdropBlur: {
        xs: "2px",
      },
      animation: {
        float: "float 8s ease-in-out infinite",
        "float-slow": "float-slow 12s ease-in-out infinite",
        "glow-pulse": "glow-pulse 3s ease-in-out infinite",
        "gradient-shift": "gradient-shift 8s ease infinite",
        "slide-up": "slide-up 0.5s cubic-bezier(0.16, 1, 0.3, 1)",
        "slide-down": "slide-down 0.3s ease-out",
        "bounce-in": "bounce-in 0.6s cubic-bezier(0.34, 1.56, 0.64, 1)",
        "fade-in": "fade-in 0.4s ease-out",
        "typing-dot": "typing-dot 1.4s ease-in-out infinite",
        "aurora-wave": "aurora-wave 6s ease-in-out infinite",
        "spin-slow": "spin 3s linear infinite",
        "pulse-ring": "pulse-ring 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "shimmer": "shimmer 2s linear infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0px) rotate(0deg)" },
          "33%": { transform: "translateY(-15px) rotate(1deg)" },
          "66%": { transform: "translateY(8px) rotate(-1deg)" },
        },
        "float-slow": {
          "0%, 100%": { transform: "translate(0, 0) scale(1)" },
          "25%": { transform: "translate(30px, -20px) scale(1.05)" },
          "50%": { transform: "translate(-15px, 15px) scale(0.95)" },
          "75%": { transform: "translate(-25px, -10px) scale(1.02)" },
        },
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 20px rgba(16, 185, 129, 0.3)" },
          "50%": { boxShadow: "0 0 40px rgba(16, 185, 129, 0.6), 0 0 60px rgba(59, 130, 246, 0.3)" },
        },
        "gradient-shift": {
          "0%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
          "100%": { backgroundPosition: "0% 50%" },
        },
        "slide-up": {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "slide-down": {
          "0%": { transform: "translateY(-10px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "bounce-in": {
          "0%": { transform: "scale(0.3)", opacity: "0" },
          "50%": { transform: "scale(1.05)" },
          "70%": { transform: "scale(0.9)" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        "fade-in": {
          "0%": { opacity: "0", transform: "translateY(8px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "typing-dot": {
          "0%, 60%, 100%": { transform: "translateY(0) scale(1)", opacity: "0.4" },
          "30%": { transform: "translateY(-8px) scale(1.2)", opacity: "1" },
        },
        "aurora-wave": {
          "0%, 100%": { opacity: "0.3", transform: "translateX(0) scaleY(1)" },
          "50%": { opacity: "0.6", transform: "translateX(10px) scaleY(1.1)" },
        },
        "pulse-ring": {
          "0%": { transform: "scale(0.8)", opacity: "1" },
          "100%": { transform: "scale(2.2)", opacity: "0" },
        },
        "shimmer": {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-mesh":
          "radial-gradient(at 20% 30%, rgba(16, 185, 129, 0.12) 0px, transparent 50%), radial-gradient(at 80% 10%, rgba(59, 130, 246, 0.1) 0px, transparent 50%), radial-gradient(at 10% 70%, rgba(14, 165, 233, 0.08) 0px, transparent 50%), radial-gradient(at 90% 60%, rgba(139, 92, 246, 0.08) 0px, transparent 50%), radial-gradient(at 50% 90%, rgba(16, 185, 129, 0.1) 0px, transparent 50%)",
      },
    },
  },
  plugins: [],
};
export default config;
