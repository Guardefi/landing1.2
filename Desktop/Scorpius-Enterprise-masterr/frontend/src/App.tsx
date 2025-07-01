import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { useState } from "react";
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
import Login from "./pages/Login";
import LicenseVerification from "./pages/LicenseVerification";
import NotFound from "./pages/NotFound";
import { queryClient } from "./lib/react-query";

const MainApp = () => {
  const [isNavOpen, setIsNavOpen] = useState(true);
  const location = useLocation();

  // Hide navigation on auth pages
  const isAuthPage =
    location.pathname === "/login" ||
    location.pathname === "/license-verification";

  return (
    <div className="relative min-h-screen cyber-grid">
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
          <Route
            path="/license-verification"
            element={<LicenseVerification />}
          />
          <Route path="/scanner" element={<Scanner />} />
          <Route path="/wallet-scanner" element={<Scanner />} />
          <Route path="/honeypot" element={<Scanner />} />
          <Route path="/time-machine" element={<Forensics />} />
          <Route path="/security/elite" element={<SecurityElite />} />
          <Route path="/trading/ai" element={<TradingAI />} />
          <Route path="/bridge/network" element={<BridgeNetwork />} />
          <Route path="/analytics/enterprise" element={<Analytics />} />
          <Route path="/computing/cluster" element={<Computing />} />
          <Route path="/monitoring/health" element={<Monitoring />} />
          <Route path="/mempool/monitor" element={<MempoolMonitor />} />
          <Route path="/mempool" element={<MempoolMonitor />} />
          <Route path="/forensics/analysis" element={<Forensics />} />
          <Route path="/reports/enterprise" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
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
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <MainApp />
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
