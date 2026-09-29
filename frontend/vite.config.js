import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// In development, forward API and redirect requests to the local backend.
// In production, nginx (or the Kubernetes Ingress) does this routing.
const backend = process.env.BACKEND_URL ?? "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": backend,
      "/r": backend,
    },
  },
});
