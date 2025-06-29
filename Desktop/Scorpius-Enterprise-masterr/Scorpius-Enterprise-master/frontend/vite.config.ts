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
      hmr: isProduction
        ? false
        : {
            port: parseInt(env.VITE_HMR_PORT || "24678"),
            clientPort: parseInt(
              env.VITE_HMR_CLIENT_PORT || env.VITE_HMR_PORT || "24678",
            ),
          },
      proxy: {
        // Proxy API calls to the gateway
        "/api": {
          target:
            env.VITE_API_BASE_URL ||
            (isProduction
              ? env.VITE_API_BASE_URL_PRODUCTION || "http://api-gateway:8000"
              : "http://localhost:8000"),
          changeOrigin: true,
        },
        // Proxy WebSocket connections
        "/ws": {
          target:
            env.VITE_WS_BASE_URL ||
            (isProduction
              ? env.VITE_WS_BASE_URL_PRODUCTION || "ws://api-gateway:8000"
              : "ws://localhost:8000"),
          ws: true,
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
