import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0F1419',
        foreground: '#FFFFFF',
        card: '#1A1F2E',
        'card-foreground': '#FFFFFF',
        primary: '#00D2FF',
        'primary-foreground': '#000000',
        secondary: '#252A3A',
        'secondary-foreground': '#FFFFFF',
        muted: '#718096',
        'muted-foreground': '#A0AEC0',
        accent: '#FF6B9D',
        'accent-foreground': '#FFFFFF',
        destructive: '#FF4757',
        'destructive-foreground': '#FFFFFF',
        border: '#374151',
        input: '#374151',
        ring: '#00D2FF',
        success: '#00FF94',
        warning: '#FFD93D',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 5px #00D2FF' },
          '50%': { boxShadow: '0 0 20px #00D2FF, 0 0 30px #00D2FF' },
        },
      },
    },
  },
  plugins: [],
};
export default config;
