import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd());
  const isProduction = mode === "production";

  return {
    base: "/",
    plugins: [react()],
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "./src"),
      },
    },
    server: {
      host: "0.0.0.0",
      port: parseInt(env.VITE_PORT || env.PORT || "3000"),
      hmr:
        process.env.HMR === "false" ||
        isProduction ||
        process.env.NODE_ENV === "production" ||
        !!process.env.FLY_APP_NAME
          ? false
          : true,
      proxy: {
        // Main API Gateway
        "/api": {
          target: env.VITE_API_BASE_URL || "http://localhost:8000",
          changeOrigin: true,
          secure: false,
        },
        // WebSocket connections
        "/ws": {
          target: env.VITE_WS_BASE_URL || "ws://localhost:8000",
          ws: true,
          changeOrigin: true,
        },
        // Scanner Service
        "/api/scanner": {
          target: env.VITE_SCANNER_API_URL || "http://localhost:8001",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/scanner/, "/api/v1"),
        },
        // Honeypot Service
        "/api/honeypot": {
          target: env.VITE_HONEYPOT_API_URL || "http://localhost:8002",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/honeypot/, "/api/v1"),
        },
        // Mempool Service
        "/api/mempool": {
          target: env.VITE_MEMPOOL_API_URL || "http://localhost:8003",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/mempool/, "/api/v1"),
        },
        // Bridge Service
        "/api/bridge": {
          target: env.VITE_BRIDGE_API_URL || "http://localhost:8004",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/bridge/, "/api/v1"),
        },
        // Bytecode Service
        "/api/bytecode": {
          target: env.VITE_BYTECODE_API_URL || "http://localhost:8005",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/bytecode/, "/api/v1"),
        },
        // Wallet Guard Service
        "/api/wallet": {
          target: env.VITE_WALLET_API_URL || "http://localhost:8006",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/wallet/, "/api/v1"),
        },
        // Time Machine Service
        "/api/time-machine": {
          target: env.VITE_TIME_MACHINE_API_URL || "http://localhost:8007",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/time-machine/, "/api/v1"),
        },
        // Quantum Service
        "/api/quantum": {
          target: env.VITE_QUANTUM_API_URL || "http://localhost:8008",
          changeOrigin: true,
          secure: false,
          rewrite: (path) => path.replace(/^\/api\/quantum/, "/api/v1"),
        },
      },
    },
    build: {
      outDir: "dist",
      sourcemap: !isProduction,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ["react", "react-dom"],
            ui: ["lucide-react"],
            charts: ["recharts"],
            utils: ["clsx", "tailwind-merge", "date-fns"],
            router: ["react-router-dom"],
            motion: ["framer-motion"],
          },
        },
      },
    },
    optimizeDeps: {
      include: ["react", "react-dom", "react-router-dom"],
    },
  };
});
