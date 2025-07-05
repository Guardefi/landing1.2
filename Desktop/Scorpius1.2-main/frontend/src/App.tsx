import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { useState } from "react";
import { AuthProvider } from "./contexts/AuthContext";
import { SubscriptionProvider } from "./contexts/SubscriptionContext";
import ProtectedRoute, {
  AdminRoute,
  ProRoute,
  EnterpriseRoute,
} from "./components/ProtectedRoute";
import Navigation from "./components/Navigation";
import Index from "./pages/Index";
import Scanner from "./pages/Scanner";
import SecurityElite from "./pages/SecurityElite";
import TradingAI from "./pages/TradingAI";
import BridgeNetwork from "./pages/BridgeNetwork";
import Analytics from "./pages/Analytics";
import Computing from "./pages/Computing";
import Monitoring from "./pages/Monitoring";
import MempoolMonitor from "./pages/MempoolMonitor";
import Forensics from "./pages/Forensics";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import SimulationSandbox from "./pages/SimulationSandbox";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Subscription from "./pages/Subscription";
import LicenseVerification from "./pages/LicenseVerification";
import GrafanaMonitoring from "./pages/GrafanaMonitoring";
import ApiStatus from "./pages/ApiStatus";
import NotFound from "./pages/NotFound";
import { queryClient } from "./lib/react-query";
import { InteractiveGrid } from "./components/ui/InteractiveGrid";

const MainApp = () => {
  const [isNavOpen, setIsNavOpen] = useState(true);
  const location = useLocation();

  // Hide navigation on auth pages
  const isAuthPage =
    location.pathname === "/login" ||
    location.pathname === "/register" ||
    location.pathname === "/license-verification";

  return (
    <div className="relative min-h-screen" style={{ perspective: "1000px" }}>
      <InteractiveGrid className="opacity-20" />
      {!isAuthPage && (
        <Navigation isOpen={isNavOpen} setIsOpen={setIsNavOpen} />
      )}
      <div
        className={`transition-all duration-300 ${
          !isAuthPage ? (isNavOpen ? "ml-80" : "ml-0") + " pt-12" : ""
        }`}
      >
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/license-verification"
            element={<LicenseVerification />}
          />

          {/* Protected Routes with Basic Authentication */}
          <Route
            path="/scanner"
            element={
              <ProtectedRoute>
                <Scanner />
              </ProtectedRoute>
            }
          />
          <Route
            path="/wallet-scanner"
            element={
              <ProtectedRoute>
                <Scanner />
              </ProtectedRoute>
            }
          />
          <Route
            path="/honeypot"
            element={
              <ProtectedRoute>
                <Scanner />
              </ProtectedRoute>
            }
          />
          <Route
            path="/time-machine"
            element={
              <ProtectedRoute>
                <Forensics />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mempool/monitor"
            element={
              <ProtectedRoute>
                <MempoolMonitor />
              </ProtectedRoute>
            }
          />
          <Route
            path="/mempool"
            element={
              <ProtectedRoute>
                <MempoolMonitor />
              </ProtectedRoute>
            }
          />
          <Route
            path="/forensics/analysis"
            element={
              <ProtectedRoute>
                <Forensics />
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            }
          />
          <Route
            path="/subscription"
            element={
              <ProtectedRoute>
                <Subscription />
              </ProtectedRoute>
            }
          />
          <Route
            path="/simulation"
            element={
              <ProtectedRoute>
                <SimulationSandbox />
              </ProtectedRoute>
            }
          />

          {/* Pro Tier Routes */}
          <Route
            path="/security/elite"
            element={
              <ProRoute>
                <SecurityElite />
              </ProRoute>
            }
          />
          <Route
            path="/trading/ai"
            element={
              <ProRoute>
                <TradingAI />
              </ProRoute>
            }
          />
          <Route
            path="/bridge/network"
            element={
              <ProRoute>
                <BridgeNetwork />
              </ProRoute>
            }
          />

          {/* Enterprise Routes */}
          <Route
            path="/analytics/enterprise"
            element={
              <EnterpriseRoute>
                <Analytics />
              </EnterpriseRoute>
            }
          />
          <Route
            path="/computing/cluster"
            element={
              <EnterpriseRoute>
                <Computing />
              </EnterpriseRoute>
            }
          />
          <Route
            path="/reports/enterprise"
            element={
              <EnterpriseRoute>
                <Reports />
              </EnterpriseRoute>
            }
          />

          {/* Admin Routes */}
          <Route
            path="/monitoring/health"
            element={
              <AdminRoute>
                <Monitoring />
              </AdminRoute>
            }
          />
          <Route
            path="/monitoring/grafana"
            element={
              <AdminRoute>
                <GrafanaMonitoring />
              </AdminRoute>
            }
          />
          <Route
            path="/api/status"
            element={
              <AdminRoute>
                <ApiStatus />
              </AdminRoute>
            }
          />

          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <SubscriptionProvider>
          <TooltipProvider>
            <Toaster />
            <Sonner position="top-right" richColors closeButton />
            <BrowserRouter>
              <MainApp />
            </BrowserRouter>
          </TooltipProvider>
        </SubscriptionProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
