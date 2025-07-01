'use client';

import { useState } from 'react';
import { OverviewDashboard } from './OverviewDashboard';
import { SecurityOperationsCenter } from './SecurityOperationsCenter';
import { AITradingEngine } from './AITradingEngine';
import { CrossChainBridge } from './CrossChainBridge';
import { AdvancedAnalytics } from './AdvancedAnalytics';
import { SystemMonitoring } from './SystemMonitoring';
import { DigitalForensics } from './DigitalForensics';
import { QuantumSecurity } from './QuantumSecurity';

export type DashboardModule =
  | 'overview'
  | 'security'
  | 'trading'
  | 'bridge'
  | 'analytics'
  | 'monitoring'
  | 'forensics'
  | 'quantum';

interface ScorpiusDashboardProps {
  initialModule?: DashboardModule;
}

export function ScorpiusDashboard({
  initialModule = 'overview',
}: ScorpiusDashboardProps) {
  const [activeModule, setActiveModule] = useState<DashboardModule>(initialModule);

  const renderModule = () => {
    switch (activeModule) {
      case 'overview':
        return <OverviewDashboard />;
      case 'security':
        return <SecurityOperationsCenter />;
      case 'trading':
        return <AITradingEngine />;
      case 'bridge':
        return <CrossChainBridge />;
      case 'analytics':
        return <AdvancedAnalytics />;
      case 'monitoring':
        return <SystemMonitoring />;
      case 'forensics':
        return <DigitalForensics />;
      case 'quantum':
        return <QuantumSecurity />;
      default:
        return <OverviewDashboard />;
    }
  };

  return <div className="p-6">{renderModule()}</div>;
}

// Export individual modules for direct usage
export {
  OverviewDashboard,
  SecurityOperationsCenter,
  AITradingEngine,
  CrossChainBridge,
  AdvancedAnalytics,
  SystemMonitoring,
  DigitalForensics,
  QuantumSecurity,
};
