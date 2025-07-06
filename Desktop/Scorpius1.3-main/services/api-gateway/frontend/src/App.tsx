import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

// Components
import TopNavigation from '@/components/TopNavigation';

// Pages
import Dashboard from '@/pages/Dashboard';
import SmartContractScanner from '@/pages/SmartContractScanner';
import TimeMachine from '@/pages/TimeMachine';
import Settings from '@/pages/Settings';
import DigitalForensics from '@/pages/DigitalForensics';

import MEVOperations from '@/pages/MEVOperations';
import MempoolMonitor from '@/pages/MempoolMonitor';
import Reports from '@/pages/Reports';
import RealTime from '@/pages/RealTime';
import AITradingEngine from '@/pages/AITradingEngine';
import CrossChainBridge from '@/pages/CrossChainBridge';

// Contexts (existing)
import { AuthProvider } from '@/contexts/AuthContext';
import { SubscriptionProvider } from '@/contexts/SubscriptionContext';
import { ToastProvider } from '@/components/ui/enhanced-toast';

import './App.css';

// Simple app layout with navigation
function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-black text-white">
      <TopNavigation />
      <main className="relative">{children}</main>
    </div>
  );
}

// Root app component
export default function App() {
  return (
    <AuthProvider>
      <SubscriptionProvider>
        <ToastProvider>
          <Router>
            <AppLayout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/scanner" element={<SmartContractScanner />} />
                <Route path="/time-machine" element={<TimeMachine />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/forensics" element={<DigitalForensics />} />
                <Route path="/mev" element={<MEVOperations />} />
                <Route path="/mempool" element={<MempoolMonitor />} />
                <Route path="/reports" element={<Reports />} />
                <Route path="/realtime" element={<RealTime />} />
                <Route path="/ai-trading" element={<AITradingEngine />} />
                <Route path="/bridge" element={<CrossChainBridge />} />

                {/* Redirect unknown routes to dashboard */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </AppLayout>
          </Router>
        </ToastProvider>
      </SubscriptionProvider>
    </AuthProvider>
  );
}
