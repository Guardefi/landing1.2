'use client';

import { useState } from 'react';
import { DashboardLayout } from '../layout/DashboardLayout';
import { OverviewDashboard } from '../../pages/OverviewDashboard';
import { SecurityOperationsCenter } from './SecurityOperationsCenter';
import { AITradingEngine } from '../../pages/AITradingEngine';
import { CrossChainBridge } from '../../pages/CrossChainBridge';
import { AdvancedAnalytics } from '../../pages/AdvancedAnalytics';
import { SystemMonitoring } from './SystemMonitoring';
import { DigitalForensics } from '../../pages/DigitalForensics';
import { QuantumSecurity } from '../../pages/QuantumSecurity';

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

  return <DashboardLayout>{renderModule()}</DashboardLayout>;
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
