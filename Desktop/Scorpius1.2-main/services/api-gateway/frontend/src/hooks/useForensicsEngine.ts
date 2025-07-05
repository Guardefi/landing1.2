/**
 * React Hook for Blockchain Forensics Engine
 *
 * Manages state and API interactions for the forensics investigation platform.
 * Provides real-time updates, caching, and comprehensive error handling.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import {
  forensicsApiService,
  ForensicsAlert,
  InvestigationCase,
  AddressProfile,
  TransactionPattern,
  ForensicsStatistics,
  AddressInvestigationResult,
  InvestigationReport,
  RiskLevel,
  AddressInvestigationRequest,
  CaseCreationRequest,
  EvidenceRequest,
  TransactionAnomaly,
  ComplianceViolation,
} from '../services/forensicsApi';

interface UseForensicsEngineState {
  // Data State
  alerts: ForensicsAlert[];
  cases: InvestigationCase[];
  addressProfiles: Record<string, AddressProfile>;
  investigations: Record<string, AddressInvestigationResult>;
  patterns: TransactionPattern[];
  statistics: ForensicsStatistics | null;

  // UI State
  loading: {
    alerts: boolean;
    cases: boolean;
    investigation: boolean;
    statistics: boolean;
    patterns: boolean;
    general: boolean;
  };

  error: {
    alerts: string | null;
    cases: string | null;
    investigation: string | null;
    statistics: string | null;
    patterns: string | null;
    general: string | null;
  };

  // Real-time monitoring
  monitoring: {
    active: boolean;
    monitoring_id: string | null;
    addresses_monitored: string[];
    alerts_generated: number;
  };

  // Cache management
  lastUpdated: {
    alerts: number;
    cases: number;
    statistics: number;
    patterns: number;
  };
}

interface UseForensicsEngineReturn extends UseForensicsEngineState {
  // Address Investigation
  investigateAddress: (
    request: AddressInvestigationRequest,
  ) => Promise<AddressInvestigationResult | null>;
  getAddressProfile: (address: string) => Promise<AddressProfile | null>;

  // Case Management
  createCase: (request: CaseCreationRequest) => Promise<string | null>;
  getCase: (caseId: string) => Promise<InvestigationCase | null>;
  updateCaseStatus: (caseId: string, status: string) => Promise<boolean>;
  addEvidence: (request: EvidenceRequest) => Promise<boolean>;
  generateReport: (caseId: string) => Promise<InvestigationReport | null>;

  // Alert Management
  refreshAlerts: () => Promise<void>;
  getHighRiskAlerts: () => Promise<ForensicsAlert[]>;
  markAlertReviewed: (alertId: string) => Promise<boolean>;
  addAlertNotes: (alertId: string, notes: string) => Promise<boolean>;

  // Pattern Detection
  detectPatterns: (addresses: string[]) => Promise<TransactionPattern[]>;
  analyzeAnomalies: (transactions: any[]) => Promise<TransactionAnomaly[]>;

  // Compliance
  checkCompliance: (address: string) => Promise<ComplianceViolation[]>;
  checkSanctions: (
    address: string,
  ) => Promise<{ is_sanctioned: boolean; details?: any }>;

  // Statistics and Metrics
  refreshStatistics: () => Promise<void>;
  getInvestigationMetrics: () => Promise<any>;
  exportData: (params: any) => Promise<Blob | null>;

  // AI Analysis
  runAIAnalysis: (data: any) => Promise<any>;

  // Network Analysis
  analyzeNetwork: (params: any) => Promise<any>;

  // Real-time Monitoring
  startMonitoring: (params: any) => Promise<boolean>;
  stopMonitoring: () => Promise<boolean>;

  // Utility functions
  clearError: (type: keyof UseForensicsEngineState['error']) => void;
  refreshAllData: () => Promise<void>;
  getRiskLevelColor: (riskLevel: RiskLevel) => string;
  getRiskLevelLabel: (riskLevel: RiskLevel) => string;
}

const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
const POLLING_INTERVAL = 30 * 1000; // 30 seconds

export const useForensicsEngine = (): UseForensicsEngineReturn => {
  const [state, setState] = useState<UseForensicsEngineState>({
    alerts: [],
    cases: [],
    addressProfiles: {},
    investigations: {},
    patterns: [],
    statistics: null,

    loading: {
      alerts: false,
      cases: false,
      investigation: false,
      statistics: false,
      patterns: false,
      general: false,
    },

    error: {
      alerts: null,
      cases: null,
      investigation: null,
      statistics: null,
      patterns: null,
      general: null,
    },

    monitoring: {
      active: false,
      monitoring_id: null,
      addresses_monitored: [],
      alerts_generated: 0,
    },

    lastUpdated: {
      alerts: 0,
      cases: 0,
      statistics: 0,
      patterns: 0,
    },
  });

  const pollingRef = useRef<NodeJS.Timeout | null>(null);

  // Helper function to update loading state
  const setLoading = useCallback(
    (type: keyof UseForensicsEngineState['loading'], value: boolean) => {
      setState(prev => ({
        ...prev,
        loading: { ...prev.loading, [type]: value },
      }));
    },
    [],
  );

  // Helper function to set error state
  const setError = useCallback(
    (type: keyof UseForensicsEngineState['error'], error: string | null) => {
      setState(prev => ({
        ...prev,
        error: { ...prev.error, [type]: error },
      }));
    },
    [],
  );

  // Helper function to update last updated timestamp
  const updateLastUpdated = useCallback(
    (type: keyof UseForensicsEngineState['lastUpdated']) => {
      setState(prev => ({
        ...prev,
        lastUpdated: { ...prev.lastUpdated, [type]: Date.now() },
      }));
    },
    [],
  );

  // Clear error function
  const clearError = useCallback(
    (type: keyof UseForensicsEngineState['error']) => {
      setError(type, null);
    },
    [setError],
  );

  // Address Investigation
  const investigateAddress = useCallback(
    async (
      request: AddressInvestigationRequest,
    ): Promise<AddressInvestigationResult | null> => {
      setLoading('investigation', true);
      setError('investigation', null);

      try {
        const result = await forensicsApiService.investigateAddress(request);

        setState(prev => ({
          ...prev,
          investigations: {
            ...prev.investigations,
            [request.address]: result,
          },
          addressProfiles: {
            ...prev.addressProfiles,
            [request.address]: result.profile,
          },
        }));

        return result;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Failed to investigate address';
        setError('investigation', errorMessage);
        return null;
      } finally {
        setLoading('investigation', false);
      }
    },
    [setLoading, setError],
  );

  const getAddressProfile = useCallback(
    async (address: string): Promise<AddressProfile | null> => {
      // Check cache first
      if (state.addressProfiles[address]) {
        return state.addressProfiles[address];
      }

      try {
        const profile = await forensicsApiService.getAddressProfile(address);

        setState(prev => ({
          ...prev,
          addressProfiles: {
            ...prev.addressProfiles,
            [address]: profile,
          },
        }));

        return profile;
      } catch (error) {
        console.error('Failed to get address profile:', error);
        return null;
      }
    },
    [state.addressProfiles],
  );

  // Case Management
  const createCase = useCallback(
    async (request: CaseCreationRequest): Promise<string | null> => {
      setLoading('cases', true);
      setError('cases', null);

      try {
        const response = await forensicsApiService.createInvestigationCase(request);
        await refreshCases(); // Refresh cases list
        return response.case_id;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Failed to create case';
        setError('cases', errorMessage);
        return null;
      } finally {
        setLoading('cases', false);
      }
    },
    [setLoading, setError],
  );

  const getCase = useCallback(
    async (caseId: string): Promise<InvestigationCase | null> => {
      try {
        return await forensicsApiService.getInvestigationCase(caseId);
      } catch (error) {
        console.error('Failed to get case:', error);
        return null;
      }
    },
    [],
  );

  const updateCaseStatus = useCallback(
    async (caseId: string, status: string): Promise<boolean> => {
      try {
        const result = await forensicsApiService.updateCaseStatus(caseId, status);
        if (result.success) {
          await refreshCases();
        }
        return result.success;
      } catch (error) {
        console.error('Failed to update case status:', error);
        return false;
      }
    },
    [],
  );

  const addEvidence = useCallback(
    async (request: EvidenceRequest): Promise<boolean> => {
      try {
        const result = await forensicsApiService.addEvidenceToCase(request);
        return result.success;
      } catch (error) {
        console.error('Failed to add evidence:', error);
        return false;
      }
    },
    [],
  );

  const generateReport = useCallback(
    async (caseId: string): Promise<InvestigationReport | null> => {
      try {
        return await forensicsApiService.generateInvestigationReport(caseId);
      } catch (error) {
        console.error('Failed to generate report:', error);
        return null;
      }
    },
    [],
  );

  // Alert Management
  const refreshAlerts = useCallback(async (): Promise<void> => {
    setLoading('alerts', true);
    setError('alerts', null);

    try {
      const alerts = await forensicsApiService.getAllAlerts();
      setState(prev => ({ ...prev, alerts }));
      updateLastUpdated('alerts');
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to refresh alerts';
      setError('alerts', errorMessage);
    } finally {
      setLoading('alerts', false);
    }
  }, [setLoading, setError, updateLastUpdated]);

  const getHighRiskAlerts = useCallback(async (): Promise<ForensicsAlert[]> => {
    try {
      return await forensicsApiService.getHighRiskAlerts();
    } catch (error) {
      console.error('Failed to get high risk alerts:', error);
      return [];
    }
  }, []);

  const markAlertReviewed = useCallback(
    async (alertId: string): Promise<boolean> => {
      try {
        const result = await forensicsApiService.markAlertAsReviewed(alertId);
        if (result.success) {
          await refreshAlerts();
        }
        return result.success;
      } catch (error) {
        console.error('Failed to mark alert as reviewed:', error);
        return false;
      }
    },
    [refreshAlerts],
  );

  const addAlertNotes = useCallback(
    async (alertId: string, notes: string): Promise<boolean> => {
      try {
        const result = await forensicsApiService.addInvestigatorNotes(alertId, notes);
        return result.success;
      } catch (error) {
        console.error('Failed to add alert notes:', error);
        return false;
      }
    },
    [],
  );

  // Cases refresh helper
  const refreshCases = useCallback(async (): Promise<void> => {
    setLoading('cases', true);
    setError('cases', null);

    try {
      const cases = await forensicsApiService.getAllCases();
      setState(prev => ({ ...prev, cases }));
      updateLastUpdated('cases');
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to refresh cases';
      setError('cases', errorMessage);
    } finally {
      setLoading('cases', false);
    }
  }, [setLoading, setError, updateLastUpdated]);

  // Pattern Detection
  const detectPatterns = useCallback(
    async (addresses: string[]): Promise<TransactionPattern[]> => {
      setLoading('patterns', true);
      setError('patterns', null);

      try {
        const patterns = await forensicsApiService.detectTransactionPatterns(addresses);
        setState(prev => ({ ...prev, patterns }));
        updateLastUpdated('patterns');
        return patterns;
      } catch (error) {
        const errorMessage =
          error instanceof Error ? error.message : 'Failed to detect patterns';
        setError('patterns', errorMessage);
        return [];
      } finally {
        setLoading('patterns', false);
      }
    },
    [setLoading, setError, updateLastUpdated],
  );

  const analyzeAnomalies = useCallback(
    async (transactions: any[]): Promise<TransactionAnomaly[]> => {
      try {
        return await forensicsApiService.analyzeTransactionAnomalies(transactions);
      } catch (error) {
        console.error('Failed to analyze anomalies:', error);
        return [];
      }
    },
    [],
  );

  // Compliance
  const checkCompliance = useCallback(
    async (address: string): Promise<ComplianceViolation[]> => {
      try {
        return await forensicsApiService.checkCompliance(address);
      } catch (error) {
        console.error('Failed to check compliance:', error);
        return [];
      }
    },
    [],
  );

  const checkSanctions = useCallback(
    async (address: string): Promise<{ is_sanctioned: boolean; details?: any }> => {
      try {
        return await forensicsApiService.checkSanctionsList(address);
      } catch (error) {
        console.error('Failed to check sanctions:', error);
        return { is_sanctioned: false };
      }
    },
    [],
  );

  // Statistics and Metrics
  const refreshStatistics = useCallback(async (): Promise<void> => {
    setLoading('statistics', true);
    setError('statistics', null);

    try {
      const statistics = await forensicsApiService.getForensicsStatistics();
      setState(prev => ({ ...prev, statistics }));
      updateLastUpdated('statistics');
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Failed to refresh statistics';
      setError('statistics', errorMessage);
    } finally {
      setLoading('statistics', false);
    }
  }, [setLoading, setError, updateLastUpdated]);

  const getInvestigationMetrics = useCallback(async () => {
    try {
      return await forensicsApiService.getInvestigationMetrics();
    } catch (error) {
      console.error('Failed to get investigation metrics:', error);
      return null;
    }
  }, []);

  const exportData = useCallback(async (params: any): Promise<Blob | null> => {
    try {
      return await forensicsApiService.exportInvestigationData(params);
    } catch (error) {
      console.error('Failed to export data:', error);
      return null;
    }
  }, []);

  // AI Analysis
  const runAIAnalysis = useCallback(async (data: any) => {
    try {
      return await forensicsApiService.runAIAnalysis(data);
    } catch (error) {
      console.error('Failed to run AI analysis:', error);
      return null;
    }
  }, []);

  // Network Analysis
  const analyzeNetwork = useCallback(async (params: any) => {
    try {
      return await forensicsApiService.analyzeTransactionNetwork(params);
    } catch (error) {
      console.error('Failed to analyze network:', error);
      return null;
    }
  }, []);

  // Real-time Monitoring
  const startMonitoring = useCallback(async (params: any): Promise<boolean> => {
    try {
      const result = await forensicsApiService.startRealTimeMonitoring(params);
      setState(prev => ({
        ...prev,
        monitoring: {
          active: true,
          monitoring_id: result.monitoring_id,
          addresses_monitored: params.addresses,
          alerts_generated: 0,
        },
      }));
      return true;
    } catch (error) {
      console.error('Failed to start monitoring:', error);
      return false;
    }
  }, []);

  const stopMonitoring = useCallback(async (): Promise<boolean> => {
    if (!state.monitoring.monitoring_id) return false;

    try {
      const result = await forensicsApiService.stopRealTimeMonitoring(
        state.monitoring.monitoring_id,
      );
      if (result.success) {
        setState(prev => ({
          ...prev,
          monitoring: {
            active: false,
            monitoring_id: null,
            addresses_monitored: [],
            alerts_generated: 0,
          },
        }));
      }
      return result.success;
    } catch (error) {
      console.error('Failed to stop monitoring:', error);
      return false;
    }
  }, [state.monitoring.monitoring_id]);

  // Utility functions
  const getRiskLevelColor = useCallback((riskLevel: RiskLevel): string => {
    switch (riskLevel) {
      case RiskLevel.LOW:
        return 'text-green-500';
      case RiskLevel.MEDIUM:
        return 'text-yellow-500';
      case RiskLevel.HIGH:
        return 'text-orange-500';
      case RiskLevel.CRITICAL:
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  }, []);

  const getRiskLevelLabel = useCallback((riskLevel: RiskLevel): string => {
    switch (riskLevel) {
      case RiskLevel.LOW:
        return 'Low';
      case RiskLevel.MEDIUM:
        return 'Medium';
      case RiskLevel.HIGH:
        return 'High';
      case RiskLevel.CRITICAL:
        return 'Critical';
      default:
        return 'Unknown';
    }
  }, []);

  const refreshAllData = useCallback(async (): Promise<void> => {
    setLoading('general', true);

    try {
      await Promise.allSettled([refreshAlerts(), refreshCases(), refreshStatistics()]);
    } finally {
      setLoading('general', false);
    }
  }, [refreshAlerts, refreshCases, refreshStatistics, setLoading]);

  // Initial data loading
  useEffect(() => {
    refreshAllData();
  }, []);

  // Real-time polling when monitoring is active
  useEffect(() => {
    if (state.monitoring.active) {
      pollingRef.current = setInterval(() => {
        refreshAlerts();
      }, POLLING_INTERVAL);
    } else if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }

    return () => {
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, [state.monitoring.active, refreshAlerts]);

  // Check cache expiration and refresh if needed
  useEffect(() => {
    const now = Date.now();
    const checkInterval = setInterval(() => {
      const currentTime = Date.now();

      if (currentTime - state.lastUpdated.alerts > CACHE_DURATION) {
        refreshAlerts();
      }
      if (currentTime - state.lastUpdated.cases > CACHE_DURATION) {
        refreshCases();
      }
      if (currentTime - state.lastUpdated.statistics > CACHE_DURATION) {
        refreshStatistics();
      }
    }, CACHE_DURATION);

    return () => clearInterval(checkInterval);
  }, [state.lastUpdated, refreshAlerts, refreshCases, refreshStatistics]);

  return {
    ...state,

    // Address Investigation
    investigateAddress,
    getAddressProfile,

    // Case Management
    createCase,
    getCase,
    updateCaseStatus,
    addEvidence,
    generateReport,

    // Alert Management
    refreshAlerts,
    getHighRiskAlerts,
    markAlertReviewed,
    addAlertNotes,

    // Pattern Detection
    detectPatterns,
    analyzeAnomalies,

    // Compliance
    checkCompliance,
    checkSanctions,

    // Statistics and Metrics
    refreshStatistics,
    getInvestigationMetrics,
    exportData,

    // AI Analysis
    runAIAnalysis,

    // Network Analysis
    analyzeNetwork,

    // Real-time Monitoring
    startMonitoring,
    stopMonitoring,

    // Utility functions
    clearError,
    refreshAllData,
    getRiskLevelColor,
    getRiskLevelLabel,
  };
};

export default useForensicsEngine;
