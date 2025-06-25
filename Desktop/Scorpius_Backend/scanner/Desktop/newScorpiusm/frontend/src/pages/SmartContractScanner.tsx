import { useState, useEffect, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence, useMotionValue, useSpring } from 'framer-motion';
import {
  Shield,
  Search,
  FileCode,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Eye,
  Download,
  Play,
  Pause,
  Clock,
  Zap,
  Target,
  Loader2,
  RefreshCw,
  Hash,
  Cpu,
  Activity,
  BarChart3,
  TrendingUp,
  Upload,
  FolderOpen,
  File,
  Trash2,
  Archive,
  Code,
  X,
  Plus,
  FileText,
  Package,
  Binary,
  Bug,
  Crosshair,
  Radar,
  Network,
  Database,
  Timer,
  GitCompare,
  Flag,
  Layers,
} from 'lucide-react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { LiveCounter } from '@/components/ui/live-counter';
import { SkeletonCard, SkeletonTable } from '@/components/ui/skeleton';
import { useToastActions } from '@/components/ui/enhanced-toast';
import { ScrollReveal, StaggeredReveal } from '@/components/ui/scroll-reveal';
import { ScannerAPI } from '@/services/scannerAPI';

interface UploadedFile {
  id: string;
  name: string;
  size: number;
  type: string;
  content: string;
  lastModified: number;
  path?: string;
  isContract?: boolean;
}

interface ProjectStructure {
  id: string;
  name: string;
  files: UploadedFile[];
  contracts: UploadedFile[];
  totalSize: number;
  uploadTime: Date;
}

const SmartContractScanner = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [scanResults, setScanResults] = useState<any[]>([]);
  const [isScanning, setIsScanning] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);
  const [contractAddress, setContractAddress] = useState('');
  const [scanHistory, setScanHistory] = useState<any[]>([]);
  const [selectedVulnerability, setSelectedVulnerability] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [showResultsPopup, setShowResultsPopup] = useState(false);
  const [stats, setStats] = useState({
    totalScans: 15247,
    vulnerabilitiesFound: 892,
    contractsAnalyzed: 3456,
    averageScore: 87.3,
  });

  // File upload state
  const [uploadedFiles, setUploadedFiles] = useState<UploadedFile[]>([]);
  const [projects, setProjects] = useState<ProjectStructure[]>([]);
  const [isDragOver, setIsDragOver] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{
    [key: string]: number;
  }>({});
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);
  const [scanMode, setScanMode] = useState<'address' | 'files'>('address');

  // Enhanced toast notifications
  const toast = useToastActions();

  // Tab system state
  const [activeTab, setActiveTab] = useState<
    'scanner' | 'simulations' | 'plugins' | 'honeypot' | 'bytecode'
  >('scanner');

  // Simulation state
  const [simulations, setSimulations] = useState<any[]>([]);
  const [activeSimulations, setActiveSimulations] = useState<any[]>([]);
  const [simulationEnvironments, setSimulationEnvironments] = useState<any[]>([]);
  const [selectedSimulation, setSelectedSimulation] = useState<any>(null);
  const [isCreatingSimulation, setIsCreatingSimulation] = useState(false);
  const [simulationStats, setSimulationStats] = useState({
    totalSimulations: 234,
    activeEnvironments: 12,
    completedTests: 1847,
    aiAnalysisRuns: 456,
  });

  // Simulation form state - ensure controlled inputs
  const [environmentType, setEnvironmentType] = useState('mainnet_fork');
  const [networkType, setNetworkType] = useState('ethereum');
  const [forkBlockNumber, setForkBlockNumber] = useState('');
  const [targetContract, setTargetContract] = useState('');

  // Plugin management state
  const [enabledPlugins, setEnabledPlugins] = useState<{
    [key: string]: { quickScan: boolean; deepScan: boolean };
  }>({
    mythx: { quickScan: true, deepScan: true },
    slither: { quickScan: true, deepScan: true },
    manticore: { quickScan: false, deepScan: true },
    mythril: { quickScan: true, deepScan: true },
    customAI: { quickScan: false, deepScan: true },
  });

  // Map frontend plugin IDs to backend plugin IDs
  const pluginIdMapping: { [key: string]: string } = {
    mythx: 'mythx-analyzer',
    slither: 'slither-static',
    manticore: 'manticore-analyzer',
    mythril: 'mythril-symbolic',
    customAI: 'custom-ai-analyzer', // This might not exist yet
  };
  const [customPlugins, setCustomPlugins] = useState<any[]>([]);
  const [isInstallingPlugin, setIsInstallingPlugin] = useState(false);
  const [pluginInstallSource, setPluginInstallSource] = useState<
    'marketplace' | 'git' | 'docker' | 'upload'
  >('marketplace');
  const [pluginUrl, setPluginUrl] = useState('');
  const [showPluginInstall, setShowPluginInstall] = useState(false);

  // Honeypot detector state
  const [honeypotEvents, setHoneypotEvents] = useState<any[]>([]);
  const [isHoneypotLive, setIsHoneypotLive] = useState(true);
  const [selectedHoneypotEvent, setSelectedHoneypotEvent] = useState<any>(null);
  const [honeypotFilters, setHoneypotFilters] = useState({
    contract: '',
    gasThreshold: 100000,
    minScore: 0,
    severity: 'all',
  });
  const [honeypotStats, setHoneypotStats] = useState({
    totalDetections: 1247,
    activeThreats: 23,
    successRate: 97.3,
    avgResponseTime: 2.1,
    contractsMonitored: 156,
    dailyBlocks: 28947,
  });

  // Bytecode matcher state
  const [bytecodeInput, setBytecodeInput] = useState('');
  const [isBytecodeAnalyzing, setIsBytecodeAnalyzing] = useState(false);
  const [bytecodeAnalysis, setBytecodeAnalysis] = useState<any>(null);
  const [bytecodeMatches, setBytecodeMatches] = useState<any[]>([]);
  const [selectedBytecodeMatch, setSelectedBytecodeMatch] = useState<any>(null);
  const [uploadedBytecode, setUploadedBytecode] = useState('');
  const [showBytecodeSource, setShowBytecodeSource] = useState(false);
  const [bytecodeStats, setBytecodeStats] = useState({
    totalScans: 15247,
    threatsDetected: 892,
    falsePositives: 43,
    avgSimilarity: 23.7,
  });

  // Mock scan results for demonstration
  const mockScanResults = [
    {
      id: '1',
      name: 'Reentrancy Vulnerability',
      severity: 'high',
      description: 'Potential reentrancy attack vector detected in withdrawal function',
      location: 'Line 45-67',
      confidence: 95,
      recommendation: 'Implement checks-effects-interactions pattern',
    },
    {
      id: '2',
      name: 'Integer Overflow',
      severity: 'medium',
      description: 'Arithmetic operations without SafeMath library',
      location: 'Line 123',
      confidence: 87,
      recommendation: 'Use SafeMath for all arithmetic operations',
    },
    {
      id: '3',
      name: 'Unchecked External Call',
      severity: 'low',
      description: 'External call without checking return value',
      location: 'Line 89',
      confidence: 72,
      recommendation: 'Always check return values of external calls',
    },
  ];

  // Mock scan history
  const mockScanHistory = [
    {
      id: 'scan_001',
      address: '0x742d35Cc6431C8BF3240C39B6969E3C77e1345eF',
      timestamp: new Date(Date.now() - 3600000),
      vulnerabilities: 3,
      score: 75,
      status: 'completed',
    },
    {
      id: 'scan_002',
      address: '0x9F8b2C4D5E6A7B8C9D0E1F2A3B4C5D6E7F8A9B0C',
      timestamp: new Date(Date.now() - 7200000),
      vulnerabilities: 1,
      score: 92,
      status: 'completed',
    },
    {
      id: 'scan_003',
      address: '0xA1B2C3D4E5F6789012345678901234567890ABCD',
      timestamp: new Date(Date.now() - 10800000),
      vulnerabilities: 5,
      score: 58,
      status: 'completed',
    },
  ];

  // File upload handlers
  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    handleFiles(files);
    // Clear the input to ensure it can be used again and prevent controlled/uncontrolled issues
    event.target.value = '';
  }, []);

  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    const files = Array.from(event.dataTransfer.files);
    handleFiles(files);
  }, []);

  const handleFiles = useCallback((files: File[]) => {
    files.forEach(file => {
      const reader = new FileReader();
      reader.onload = e => {
        const newFile: UploadedFile = {
          id: Math.random().toString(36).substr(2, 9),
          name: file.name,
          size: file.size,
          type: file.type,
          content: e.target?.result as string,
          lastModified: file.lastModified,
          isContract: file.name.endsWith('.sol') || file.name.endsWith('.vy'),
        };
        setUploadedFiles(prev => [...prev, newFile]);
      };
      reader.readAsText(file);
    });

    // Reset file input to prevent controlled/uncontrolled warnings
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  const removeFile = useCallback((fileId: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    setSelectedFiles(prev => prev.filter(id => id !== fileId));
  }, []);

  const toggleFileSelection = useCallback((fileId: string) => {
    setSelectedFiles(prev =>
      prev.includes(fileId) ? prev.filter(id => id !== fileId) : [...prev, fileId],
    );
  }, []);

  const selectAllContracts = useCallback(() => {
    const contractFiles = uploadedFiles.filter(f => f.isContract).map(f => f.id);
    setSelectedFiles(contractFiles);
  }, [uploadedFiles]);

  const clearSelection = useCallback(() => {
    setSelectedFiles([]);
  }, []);

  // Plugin management functions
  const enableAllPlugins = useCallback(
    (scanType: 'quickScan' | 'deepScan') => {
      setEnabledPlugins(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(pluginId => {
          updated[pluginId] = { ...updated[pluginId], [scanType]: true };
        });
        return updated;
      });
      toast.success(`All plugins enabled for ${scanType.replace('Scan', ' scan')}`);
    },
    [toast],
  );

  const disableAllPlugins = useCallback(
    (scanType: 'quickScan' | 'deepScan') => {
      setEnabledPlugins(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(pluginId => {
          updated[pluginId] = { ...updated[pluginId], [scanType]: false };
        });
        return updated;
      });
      toast.warning(`All plugins disabled for ${scanType.replace('Scan', ' scan')}`);
    },
    [toast],
  );

  const resetPluginsToDefault = useCallback(() => {
    setEnabledPlugins({
      mythx: { quickScan: true, deepScan: true },
      slither: { quickScan: true, deepScan: true },
      manticore: { quickScan: false, deepScan: true },
      mythril: { quickScan: true, deepScan: true },
      customAI: { quickScan: false, deepScan: true },
    });
    toast.info('Plugin settings reset to defaults');
  }, [toast]);

  // Scan handlers
  const startScan = useCallback(
    async (scanType: 'quick' | 'deep' = 'quick') => {
      if (scanMode === 'address' && !contractAddress.trim()) {
        toast.error('Please enter a contract address');
        return;
      }

      if (scanMode === 'files' && selectedFiles.length === 0) {
        toast.error('Please select files to scan');
        return;
      }

      // Check if any plugins are enabled for the scan type
      const activePlugins = Object.entries(enabledPlugins).filter(([_, config]) =>
        scanType === 'quick' ? config.quickScan : config.deepScan,
      );

      if (activePlugins.length === 0) {
        toast.error(
          `No plugins enabled for ${scanType} scan. Please enable plugins in the Plugin Manager.`,
        );
        return;
      }

      setIsScanning(true);
      setScanProgress(0);
      setShowResults(false);

      // Map frontend plugin IDs to backend plugin IDs
      const backendPluginIds = activePlugins
        .map(([frontendId]) => pluginIdMapping[frontendId])
        .filter(Boolean); // Remove any undefined mappings

      // Show which plugins are being used
      const pluginNames = activePlugins
        .map(([name]) => name.charAt(0).toUpperCase() + name.slice(1))
        .join(', ');
      toast.info(`Starting ${scanType} scan with: ${pluginNames}`);

      try {
        // Prepare scan request
        const scanRequest = {
          target: contractAddress.trim(),
          plugins: backendPluginIds,
          enable_simulation: scanType === 'deep', // Enable simulation for deep scans
        };

        // Start the actual scan via API
        const response = await ScannerAPI.startScan(scanRequest);
        toast.success(`Scan started successfully: ${response.scan_id}`);

        // Poll for scan status
        const pollInterval = setInterval(async () => {
          try {
            const status = await ScannerAPI.getScanStatus(response.scan_id);

            // Update progress based on status
            if (status.status === 'running') {
              setScanProgress(prev => Math.min(prev + Math.random() * 10, 90));
            } else if (status.status === 'completed') {
              clearInterval(pollInterval);
              setScanProgress(100);
              setIsScanning(false);

              // Process and display results
              if (status.findings && status.findings.length > 0) {
                const processedResults = status.findings.map(
                  (finding: any, index: number) => ({
                    id: `finding_${index}`,
                    name: finding.title || finding.name || 'Unknown Vulnerability',
                    severity: finding.severity || 'medium',
                    description: finding.description || 'No description available',
                    location: finding.location || 'Unknown location',
                    confidence: finding.confidence || 50,
                    recommendation:
                      finding.recommendation || 'Review and fix the issue',
                    detectedBy: finding.plugin || 'Unknown',
                    scanType: scanType,
                  }),
                );

                setScanResults(processedResults);
                setShowResults(true);
                setShowResultsPopup(true);
                toast.success(
                  `${
                    scanType.charAt(0).toUpperCase() + scanType.slice(1)
                  } scan completed with ${processedResults.length} findings`,
                );
              } else {
                setScanResults([]);
                setShowResults(true);
                toast.success('Scan completed - No vulnerabilities found!');
              }

              // Add to scan history
              const newScan = {
                id: response.scan_id,
                address: scanMode === 'address' ? contractAddress : 'Multiple Files',
                timestamp: new Date(),
                vulnerabilities: status.findings?.length || 0,
                score: Math.max(100 - (status.findings?.length || 0) * 10, 0),
                status: 'completed',
                scanType: scanType,
                pluginsUsed: activePlugins.map(([name]) => name),
              };
              setScanHistory(prev => [newScan, ...prev]);
            } else if (status.status === 'failed') {
              clearInterval(pollInterval);
              setIsScanning(false);
              setScanProgress(0);
              toast.error(`Scan failed: ${status.error || 'Unknown error'}`);
            }
          } catch (error) {
            console.error('Error polling scan status:', error);
            // Continue polling in case of temporary network issues
          }
        }, 2000); // Poll every 2 seconds

        // Timeout after 5 minutes
        setTimeout(() => {
          clearInterval(pollInterval);
          if (isScanning) {
            setIsScanning(false);
            toast.error('Scan timeout - please try again');
          }
        }, 300000);
      } catch (error) {
        setIsScanning(false);
        setScanProgress(0);
        console.error('Scan error:', error);
        toast.error(
          `Failed to start scan: ${
            error instanceof Error ? error.message : 'Unknown error'
          }`,
        );
      }
    },
    [
      contractAddress,
      selectedFiles,
      scanMode,
      toast,
      enabledPlugins,
      pluginIdMapping,
      isScanning,
    ],
  );

  const stopScan = useCallback(() => {
    setIsScanning(false);
    setScanProgress(0);
    toast.info('Scan stopped');
  }, [toast]);

  const exportResults = useCallback(() => {
    if (scanResults.length === 0) {
      toast.error('No results to export');
      return;
    }

    const exportData = {
      timestamp: new Date().toISOString(),
      scanTarget: scanMode === 'address' ? contractAddress : 'Multiple Files',
      results: scanResults,
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scan-results-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    toast.success('Results exported successfully');
  }, [scanResults, scanMode, contractAddress, toast]);

  // Initialize data
  useEffect(() => {
    setScanHistory(mockScanHistory);
  }, []);

  return (
    <>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        style={{
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #000000 0%, #001a1a 50%, #000000 100%)',
          color: '#ffffff',
          padding: '20px',
          position: 'relative',
        }}
      >
        {/* Background Effects */}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            background:
              'radial-gradient(circle at 50% 50%, rgba(0, 255, 136, 0.1) 0%, transparent 50%)',
            pointerEvents: 'none',
          }}
        />

        {/* Header */}
        <ScrollReveal>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '32px',
              padding: '24px',
              backgroundColor: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(10px)',
              border: '1px solid rgba(0, 255, 136, 0.3)',
              borderRadius: '16px',
              boxShadow: '0 0 30px rgba(0, 255, 136, 0.2)',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <motion.div
                animate={{
                  rotateY: [0, 360],
                  scale: [1, 1.1, 1],
                }}
                transition={{
                  rotateY: { duration: 4, repeat: Infinity, ease: 'linear' },
                  scale: { duration: 2, repeat: Infinity, ease: 'easeInOut' },
                }}
                className="p-3 rounded-2xl bg-gradient-to-r from-cyan-600 to-green-600"
                style={{
                  boxShadow: '0 0 30px rgba(0, 255, 136, 0.5)',
                }}
              >
                <Search size={24} />
              </motion.div>
              <div>
                <h1
                  style={{
                    fontSize: '32px',
                    fontWeight: '700',
                    color: '#00ff88',
                    margin: '0',
                    letterSpacing: '2px',
                    textShadow: '0 0 20px rgba(0, 255, 136, 0.6)',
                  }}
                >
                  VULNERABILITY SCANNER
                </h1>
                <p
                  style={{
                    fontSize: '14px',
                    color: '#999999',
                    margin: '0',
                    letterSpacing: '1px',
                  }}
                >
                  Scan & Strike - Advanced Smart Contract Security Analysis
                </p>
              </div>
            </div>

            {/* Live Status */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <motion.div
                className="pulse-dot"
                style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  backgroundColor: isScanning ? '#ffaa00' : '#00ff88',
                  color: isScanning ? '#ffaa00' : '#00ff88',
                }}
              />
              <span
                style={{
                  color: '#cccccc',
                  fontSize: '14px',
                  fontWeight: '500',
                }}
              >
                {isScanning ? 'SCANNING...' : 'READY'}
              </span>
            </div>
          </div>
        </ScrollReveal>

        {/* Stats Dashboard */}
        <ScrollReveal delay={0.1}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '16px',
              marginBottom: '32px',
            }}
          >
            {[
              {
                label: 'Total Scans',
                value: stats.totalScans,
                icon: Activity,
                color: '#00ff88',
              },
              {
                label: 'Vulnerabilities',
                value: stats.vulnerabilitiesFound,
                icon: AlertTriangle,
                color: '#ff4444',
              },
              {
                label: 'Contracts Analyzed',
                value: stats.contractsAnalyzed,
                icon: FileCode,
                color: '#00ffff',
              },
              {
                label: 'Average Score',
                value: stats.averageScore,
                icon: BarChart3,
                color: '#ffaa00',
                suffix: '%',
              },
            ].map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: 0.1 * index }}
                whileHover={{ scale: 1.05, y: -5 }}
                style={{
                  backgroundColor: 'rgba(0, 0, 0, 0.6)',
                  backdropFilter: 'blur(10px)',
                  border: `1px solid ${stat.color}30`,
                  borderRadius: '16px',
                  padding: '20px',
                  boxShadow: `0 0 20px ${stat.color}20`,
                  position: 'relative',
                  overflow: 'hidden',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    top: 0,
                    right: 0,
                    bottom: 0,
                    left: 0,
                    background: `linear-gradient(135deg, ${stat.color}05, transparent)`,
                  }}
                />
                <div
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '8px',
                    position: 'relative',
                  }}
                >
                  <div
                    style={{
                      width: '36px',
                      height: '36px',
                      borderRadius: '10px',
                      backgroundColor: `${stat.color}20`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      border: `1px solid ${stat.color}60`,
                    }}
                  >
                    <stat.icon size={18} color={stat.color} />
                  </div>
                  <div style={{ flex: 1 }}>
                    <motion.div
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
                      style={{
                        fontSize: '24px',
                        fontWeight: '700',
                        color: stat.color,
                        lineHeight: 1,
                      }}
                    >
                      <LiveCounter
                        value={stat.value}
                        suffix={stat.suffix}
                        decimals={stat.suffix === '%' ? 1 : 0}
                        duration={2000}
                      />
                    </motion.div>
                    <div
                      style={{
                        fontSize: '12px',
                        color: '#999999',
                        textTransform: 'uppercase',
                        letterSpacing: '1px',
                        marginTop: '4px',
                      }}
                    >
                      {stat.label}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </ScrollReveal>

        {/* Tab Navigation */}
        <ScrollReveal delay={0.15}>
          <div
            style={{
              display: 'flex',
              justifyContent: 'center',
              marginBottom: '32px',
            }}
          >
            <div
              style={{
                display: 'flex',
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                border: '1px solid rgba(0, 255, 136, 0.3)',
                borderRadius: '16px',
                padding: '6px',
                backdropFilter: 'blur(20px)',
                boxShadow: '0 0 30px rgba(0, 255, 136, 0.2)',
              }}
            >
              {[
                {
                  id: 'scanner',
                  label: 'Security Scanner',
                  icon: Shield,
                  color: '#00ff88',
                },
                {
                  id: 'honeypot',
                  label: 'Honeypot Detector',
                  icon: Target,
                  color: '#ff4444',
                },
                {
                  id: 'bytecode',
                  label: 'Bytecode Matcher',
                  icon: Binary,
                  color: '#9333ea',
                },
                {
                  id: 'simulations',
                  label: 'Simulation Engine',
                  icon: Activity,
                  color: '#00ffff',
                },
                {
                  id: 'plugins',
                  label: 'Plugin Manager',
                  icon: Package,
                  color: '#ff6b35',
                },
              ].map(tab => (
                <motion.button
                  key={tab.id}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() =>
                    setActiveTab(tab.id as 'scanner' | 'simulations' | 'plugins')
                  }
                  style={{
                    padding: '14px 28px',
                    borderRadius: '12px',
                    border: 'none',
                    fontSize: '15px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    fontFamily: 'inherit',
                    backgroundColor:
                      activeTab === tab.id ? `${tab.color}20` : 'transparent',
                    color: activeTab === tab.id ? tab.color : '#cccccc',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    transition: 'all 0.3s ease',
                    boxShadow:
                      activeTab === tab.id ? `0 0 20px ${tab.color}30` : 'none',
                    position: 'relative',
                    overflow: 'hidden',
                  }}
                >
                  {activeTab === tab.id && (
                    <motion.div
                      layoutId="activeTab"
                      style={{
                        position: 'absolute',
                        inset: 0,
                        background: `linear-gradient(135deg, ${tab.color}15, ${tab.color}05)`,
                        borderRadius: '12px',
                      }}
                    />
                  )}
                  <tab.icon size={18} />
                  <span style={{ position: 'relative', zIndex: 1 }}>{tab.label}</span>
                </motion.button>
              ))}
            </div>
          </div>
        </ScrollReveal>

        {/* Tab Content */}
        <AnimatePresence mode="wait">
          {activeTab === 'scanner' && (
            <motion.div
              key="scanner"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Scan Mode Toggle */}
              <ScrollReveal delay={0.2}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'center',
                    marginBottom: '32px',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      backgroundColor: 'rgba(0, 0, 0, 0.6)',
                      border: '1px solid rgba(0, 255, 136, 0.3)',
                      borderRadius: '12px',
                      padding: '4px',
                      backdropFilter: 'blur(10px)',
                    }}
                  >
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setScanMode('address')}
                      style={{
                        padding: '12px 24px',
                        borderRadius: '8px',
                        border: 'none',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        fontFamily: 'inherit',
                        backgroundColor:
                          scanMode === 'address'
                            ? 'rgba(0, 255, 136, 0.2)'
                            : 'transparent',
                        color: scanMode === 'address' ? '#00ff88' : '#cccccc',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <Hash size={16} />
                      Contract Address
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setScanMode('files')}
                      style={{
                        padding: '12px 24px',
                        borderRadius: '8px',
                        border: 'none',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        fontFamily: 'inherit',
                        backgroundColor:
                          scanMode === 'files'
                            ? 'rgba(0, 255, 136, 0.2)'
                            : 'transparent',
                        color: scanMode === 'files' ? '#00ff88' : '#cccccc',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <Upload size={16} />
                      File Upload
                    </motion.button>
                  </div>
                </div>
              </ScrollReveal>

              {/* Scanner Content */}
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: scanMode === 'files' ? '1fr 1fr' : '1fr',
                  gap: '32px',
                  marginBottom: '32px',
                }}
              >
                {/* Scanner Configuration */}
                <ScrollReveal delay={0.3}>
                  <div
                    style={{
                      backgroundColor: 'rgba(0, 0, 0, 0.6)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(0, 255, 255, 0.3)',
                      borderRadius: '16px',
                      padding: '24px',
                      boxShadow: '0 0 20px rgba(0, 255, 255, 0.1)',
                    }}
                  >
                    <h2
                      style={{
                        fontSize: '20px',
                        fontWeight: '600',
                        color: '#00ffff',
                        margin: '0 0 24px 0',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <Target size={20} />
                      {scanMode === 'address' ? 'Target Configuration' : 'File Upload'}
                    </h2>

                    {scanMode === 'address' ? (
                      <div style={{ marginBottom: '24px' }}>
                        <label
                          style={{
                            display: 'block',
                            fontSize: '14px',
                            color: '#cccccc',
                            marginBottom: '8px',
                            fontWeight: '500',
                          }}
                        >
                          Contract Address
                        </label>
                        <input
                          type="text"
                          placeholder="0x742d35Cc6431C8BF3240C39B6969E3C77e1345eF"
                          value={contractAddress || ''}
                          onChange={e => setContractAddress(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '12px 16px',
                            backgroundColor: '#000000',
                            border: '1px solid rgba(0, 255, 255, 0.3)',
                            borderRadius: '8px',
                            color: '#ffffff',
                            fontSize: '14px',
                            fontFamily: 'monospace',
                            outline: 'none',
                          }}
                        />
                      </div>
                    ) : (
                      <div>
                        {/* File Upload Area */}
                        <motion.div
                          onDragOver={handleDragOver}
                          onDragLeave={handleDragLeave}
                          onDrop={handleDrop}
                          whileHover={{ scale: 1.02 }}
                          style={{
                            border: isDragOver
                              ? '2px dashed #00ff88'
                              : '2px dashed rgba(0, 255, 136, 0.3)',
                            borderRadius: '12px',
                            padding: '32px',
                            textAlign: 'center',
                            backgroundColor: isDragOver
                              ? 'rgba(0, 255, 136, 0.1)'
                              : 'rgba(0, 0, 0, 0.4)',
                            cursor: 'pointer',
                            marginBottom: '16px',
                          }}
                          className={isDragOver ? 'drag-over' : ''}
                          onClick={() => fileInputRef.current?.click()}
                        >
                          <Upload
                            size={48}
                            color={isDragOver ? '#00ff88' : '#666666'}
                            style={{ marginBottom: '16px' }}
                          />
                          <h3
                            style={{
                              fontSize: '18px',
                              color: isDragOver ? '#00ff88' : '#cccccc',
                              margin: '0 0 8px 0',
                              fontWeight: '600',
                            }}
                          >
                            Drop files here or click to browse
                          </h3>
                          <p
                            style={{
                              fontSize: '14px',
                              color: '#999999',
                              margin: '0 0 8px 0',
                            }}
                          >
                            Supports .sol, .vy, .cairo, .move, .js, .ts files and .zip
                            projects
                          </p>
                          <p
                            style={{
                              fontSize: '12px',
                              color: '#666666',
                              margin: '0',
                            }}
                          >
                            Maximum file size: 10MB
                          </p>
                        </motion.div>

                        <input
                          ref={fileInputRef}
                          type="file"
                          multiple
                          accept=".sol,.vy,.cairo,.move,.js,.ts,.rs,.zip,.json"
                          onChange={handleFileSelect}
                          style={{ display: 'none' }}
                        />
                      </div>
                    )}

                    {/* Control Buttons */}
                    <div
                      style={{
                        display: 'flex',
                        gap: '12px',
                        marginTop: '24px',
                      }}
                    >
                      {!isScanning ? (
                        <>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => startScan('quick')}
                            style={{
                              flex: 1,
                              padding: '12px 20px',
                              backgroundColor: 'rgba(0, 255, 136, 0.2)',
                              border: '1px solid rgba(0, 255, 136, 0.3)',
                              borderRadius: '8px',
                              color: '#00ff88',
                              fontSize: '14px',
                              fontWeight: '600',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                            }}
                          >
                            <Zap size={16} />
                            Quick Scan
                          </motion.button>
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => startScan('deep')}
                            style={{
                              flex: 1,
                              padding: '12px 20px',
                              backgroundColor: 'rgba(0, 255, 255, 0.2)',
                              border: '1px solid rgba(0, 255, 255, 0.3)',
                              borderRadius: '8px',
                              color: '#00ffff',
                              fontSize: '14px',
                              fontWeight: '600',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                            }}
                          >
                            <Target size={16} />
                            Deep Scan
                          </motion.button>
                        </>
                      ) : (
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.95 }}
                          onClick={stopScan}
                          style={{
                            flex: 1,
                            padding: '12px 24px',
                            backgroundColor: 'rgba(255, 68, 68, 0.2)',
                            border: '1px solid rgba(255, 68, 68, 0.3)',
                            borderRadius: '8px',
                            color: '#ff4444',
                            fontSize: '14px',
                            fontWeight: '600',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            gap: '8px',
                          }}
                        >
                          <Pause size={16} />
                          Stop Scan
                        </motion.button>
                      )}

                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={exportResults}
                        disabled={scanResults.length === 0}
                        style={{
                          padding: '12px 24px',
                          backgroundColor: 'rgba(0, 255, 255, 0.2)',
                          border: '1px solid rgba(0, 255, 255, 0.3)',
                          borderRadius: '8px',
                          color: '#00ffff',
                          fontSize: '14px',
                          fontWeight: '600',
                          cursor: scanResults.length > 0 ? 'pointer' : 'not-allowed',
                          opacity: scanResults.length > 0 ? 1 : 0.5,
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                        }}
                      >
                        <Download size={16} />
                        Export
                      </motion.button>
                    </div>

                    {/* Progress Bar */}
                    {isScanning && (
                      <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        style={{ marginTop: '16px' }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            marginBottom: '8px',
                            fontSize: '12px',
                            color: '#cccccc',
                          }}
                        >
                          <span>Scanning Progress</span>
                          <span>{Math.round(scanProgress)}%</span>
                        </div>
                        <div
                          style={{
                            width: '100%',
                            height: '8px',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            borderRadius: '4px',
                            overflow: 'hidden',
                          }}
                        >
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${scanProgress}%` }}
                            style={{
                              height: '100%',
                              backgroundColor: '#00ff88',
                              borderRadius: '4px',
                            }}
                          />
                        </div>
                      </motion.div>
                    )}
                  </div>
                </ScrollReveal>

                {/* File Management (only shown in files mode) */}
                {scanMode === 'files' && (
                  <ScrollReveal delay={0.4}>
                    <div
                      style={{
                        backgroundColor: 'rgba(0, 0, 0, 0.6)',
                        backdropFilter: 'blur(10px)',
                        border: '1px solid rgba(255, 170, 0, 0.3)',
                        borderRadius: '16px',
                        padding: '24px',
                        boxShadow: '0 0 20px rgba(255, 170, 0, 0.1)',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          marginBottom: '20px',
                        }}
                      >
                        <h2
                          style={{
                            fontSize: '20px',
                            fontWeight: '600',
                            color: '#ffaa00',
                            margin: '0',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                          }}
                        >
                          <FolderOpen size={20} />
                          File Management
                        </h2>

                        {uploadedFiles.length > 0 && (
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={selectAllContracts}
                              style={{
                                padding: '8px 16px',
                                backgroundColor: 'rgba(0, 255, 136, 0.2)',
                                border: '1px solid rgba(0, 255, 136, 0.3)',
                                borderRadius: '6px',
                                color: '#00ff88',
                                fontSize: '12px',
                                fontWeight: '600',
                                cursor: 'pointer',
                              }}
                            >
                              Select All
                            </motion.button>
                            <motion.button
                              whileHover={{ scale: 1.05 }}
                              whileTap={{ scale: 0.95 }}
                              onClick={clearSelection}
                              style={{
                                padding: '8px 16px',
                                backgroundColor: 'rgba(255, 68, 68, 0.2)',
                                border: '1px solid rgba(255, 68, 68, 0.3)',
                                borderRadius: '6px',
                                color: '#ff4444',
                                fontSize: '12px',
                                fontWeight: '600',
                                cursor: 'pointer',
                              }}
                            >
                              Clear
                            </motion.button>
                          </div>
                        )}
                      </div>

                      {/* File List */}
                      <div
                        style={{
                          maxHeight: '300px',
                          overflowY: 'auto',
                          marginBottom: '16px',
                        }}
                      >
                        {uploadedFiles.length === 0 ? (
                          <div
                            style={{
                              textAlign: 'center',
                              padding: '40px',
                              color: '#666666',
                            }}
                          >
                            <FileCode size={48} style={{ marginBottom: '16px' }} />
                            <p>No files uploaded yet</p>
                          </div>
                        ) : (
                          <div style={{ display: 'grid', gap: '8px' }}>
                            {uploadedFiles.map((file, index) => (
                              <motion.div
                                key={file.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{
                                  duration: 0.3,
                                  delay: index * 0.1,
                                }}
                                style={{
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '12px',
                                  padding: '12px',
                                  backgroundColor: selectedFiles.includes(file.id)
                                    ? 'rgba(0, 255, 136, 0.1)'
                                    : 'rgba(0, 0, 0, 0.4)',
                                  border: selectedFiles.includes(file.id)
                                    ? '1px solid rgba(0, 255, 136, 0.3)'
                                    : '1px solid rgba(255, 255, 255, 0.1)',
                                  borderRadius: '8px',
                                  cursor: 'pointer',
                                }}
                                onClick={() => toggleFileSelection(file.id)}
                              >
                                <input
                                  type="checkbox"
                                  checked={selectedFiles.includes(file.id)}
                                  onChange={() => toggleFileSelection(file.id)}
                                  style={{ margin: '0' }}
                                />
                                <div
                                  style={{
                                    width: '32px',
                                    height: '32px',
                                    borderRadius: '6px',
                                    backgroundColor: file.isContract
                                      ? 'rgba(0, 255, 136, 0.2)'
                                      : 'rgba(100, 100, 100, 0.2)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                  }}
                                >
                                  {file.isContract ? (
                                    <Shield size={16} color="#00ff88" />
                                  ) : (
                                    <File size={16} color="#999999" />
                                  )}
                                </div>
                                <div style={{ flex: 1, minWidth: 0 }}>
                                  <div
                                    style={{
                                      fontSize: '14px',
                                      fontWeight: '500',
                                      color: '#ffffff',
                                      marginBottom: '2px',
                                      overflow: 'hidden',
                                      textOverflow: 'ellipsis',
                                      whiteSpace: 'nowrap',
                                    }}
                                  >
                                    {file.name}
                                  </div>
                                  <div
                                    style={{
                                      fontSize: '12px',
                                      color: '#999999',
                                    }}
                                  >
                                    {(file.size / 1024).toFixed(1)} KB
                                    {file.isContract && (
                                      <span
                                        style={{
                                          marginLeft: '8px',
                                          padding: '2px 6px',
                                          backgroundColor: 'rgba(0, 255, 136, 0.2)',
                                          borderRadius: '4px',
                                          fontSize: '10px',
                                          color: '#00ff88',
                                        }}
                                      >
                                        CONTRACT
                                      </span>
                                    )}
                                  </div>
                                </div>
                                <motion.button
                                  whileHover={{ scale: 1.1 }}
                                  whileTap={{ scale: 0.9 }}
                                  onClick={e => {
                                    e.stopPropagation();
                                    removeFile(file.id);
                                  }}
                                  style={{
                                    padding: '4px',
                                    backgroundColor: 'rgba(255, 68, 68, 0.2)',
                                    border: '1px solid rgba(255, 68, 68, 0.3)',
                                    borderRadius: '4px',
                                    color: '#ff4444',
                                    cursor: 'pointer',
                                  }}
                                >
                                  <Trash2 size={12} />
                                </motion.button>
                              </motion.div>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  </ScrollReveal>
                )}
              </div>

              {/* Results Section */}
              {showResults && scanResults.length > 0 && (
                <ScrollReveal delay={0.5}>
                  <div
                    style={{
                      backgroundColor: 'rgba(0, 0, 0, 0.6)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 68, 68, 0.3)',
                      borderRadius: '16px',
                      padding: '24px',
                      marginBottom: '32px',
                      boxShadow: '0 0 20px rgba(255, 68, 68, 0.1)',
                    }}
                  >
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '20px',
                      }}
                    >
                      <h2
                        style={{
                          fontSize: '20px',
                          fontWeight: '600',
                          color: '#ff4444',
                          margin: '0',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                        }}
                      >
                        <AlertTriangle size={20} />
                        Scan Results
                      </h2>

                      {/* Plugins Used Summary */}
                      {scanResults.length > 0 && scanResults[0].scanType && (
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px',
                          }}
                        >
                          <span style={{ fontSize: '12px', color: '#cccccc' }}>
                            {scanResults[0].scanType?.charAt(0).toUpperCase() +
                              scanResults[0].scanType?.slice(1)}{' '}
                            scan with:
                          </span>
                          <div style={{ display: 'flex', gap: '4px' }}>
                            {Array.from(
                              new Set(
                                scanResults.map(r => r.detectedBy).filter(Boolean),
                              ),
                            ).map((plugin, idx) => (
                              <span
                                key={idx}
                                style={{
                                  fontSize: '10px',
                                  backgroundColor: 'rgba(255, 107, 53, 0.2)',
                                  color: '#ff6b35',
                                  padding: '2px 6px',
                                  borderRadius: '4px',
                                  textTransform: 'capitalize',
                                }}
                              >
                                {plugin}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>

                    <div style={{ display: 'grid', gap: '12px' }}>
                      {scanResults.map((result, index) => (
                        <motion.div
                          key={result.id}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          whileHover={{ scale: 1.02 }}
                          onClick={() => setSelectedVulnerability(result)}
                          style={{
                            padding: '16px',
                            backgroundColor: 'rgba(0, 0, 0, 0.6)',
                            border: `1px solid ${
                              result.severity === 'high'
                                ? '#ff4444'
                                : result.severity === 'medium'
                                ? '#ffaa00'
                                : '#00ff88'
                            }30`,
                            borderRadius: '8px',
                            cursor: 'pointer',
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'flex-start',
                              marginBottom: '8px',
                            }}
                          >
                            <h3
                              style={{
                                fontSize: '16px',
                                fontWeight: '600',
                                color: '#ffffff',
                                margin: '0',
                              }}
                            >
                              {result.name}
                            </h3>
                            <span
                              style={{
                                padding: '4px 8px',
                                borderRadius: '4px',
                                fontSize: '12px',
                                fontWeight: '600',
                                textTransform: 'uppercase',
                                backgroundColor:
                                  result.severity === 'high'
                                    ? 'rgba(255, 68, 68, 0.2)'
                                    : result.severity === 'medium'
                                    ? 'rgba(255, 170, 0, 0.2)'
                                    : 'rgba(0, 255, 136, 0.2)',
                                color:
                                  result.severity === 'high'
                                    ? '#ff4444'
                                    : result.severity === 'medium'
                                    ? '#ffaa00'
                                    : '#00ff88',
                              }}
                            >
                              {result.severity}
                            </span>
                          </div>
                          <p
                            style={{
                              fontSize: '14px',
                              color: '#cccccc',
                              margin: '0 0 8px 0',
                              lineHeight: 1.4,
                            }}
                          >
                            {result.description}
                          </p>
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              fontSize: '12px',
                              color: '#999999',
                            }}
                          >
                            <span>Location: {result.location}</span>
                            <div
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                              }}
                            >
                              {result.detectedBy && (
                                <span
                                  style={{
                                    backgroundColor: 'rgba(255, 107, 53, 0.2)',
                                    color: '#ff6b35',
                                    padding: '2px 6px',
                                    borderRadius: '4px',
                                    fontSize: '10px',
                                    textTransform: 'capitalize',
                                  }}
                                >
                                  {result.detectedBy}
                                </span>
                              )}
                              <span>Confidence: {result.confidence}%</span>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </ScrollReveal>
              )}

              {/* Scan History */}
              {scanHistory.length > 0 && (
                <ScrollReveal delay={0.6}>
                  <div
                    style={{
                      backgroundColor: 'rgba(0, 0, 0, 0.6)',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(100, 100, 100, 0.3)',
                      borderRadius: '16px',
                      padding: '24px',
                      boxShadow: '0 0 20px rgba(100, 100, 100, 0.1)',
                    }}
                  >
                    <h2
                      style={{
                        fontSize: '20px',
                        fontWeight: '600',
                        color: '#cccccc',
                        margin: '0 0 20px 0',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <Clock size={20} />
                      Recent Scans
                    </h2>

                    <div style={{ overflowX: 'auto' }}>
                      <table
                        style={{
                          width: '100%',
                          borderCollapse: 'collapse',
                          fontSize: '14px',
                        }}
                      >
                        <thead>
                          <tr>
                            <th
                              style={{
                                padding: '12px',
                                textAlign: 'left',
                                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                                color: '#cccccc',
                                fontWeight: '600',
                              }}
                            >
                              Target
                            </th>
                            <th
                              style={{
                                padding: '12px',
                                textAlign: 'left',
                                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                                color: '#cccccc',
                                fontWeight: '600',
                              }}
                            >
                              Issues Found
                            </th>
                            <th
                              style={{
                                padding: '12px',
                                textAlign: 'left',
                                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                                color: '#cccccc',
                                fontWeight: '600',
                              }}
                            >
                              Score
                            </th>
                            <th
                              style={{
                                padding: '12px',
                                textAlign: 'left',
                                borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
                                color: '#cccccc',
                                fontWeight: '600',
                              }}
                            >
                              Date
                            </th>
                          </tr>
                        </thead>
                        <tbody>
                          {scanHistory.map((scan, index) => (
                            <motion.tr
                              key={scan.id}
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              transition={{ duration: 0.3, delay: index * 0.1 }}
                              style={{
                                borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                              }}
                            >
                              <td style={{ padding: '12px', color: '#ffffff' }}>
                                <div
                                  style={{
                                    fontFamily: 'monospace',
                                    fontSize: '12px',
                                    maxWidth: '200px',
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                  }}
                                >
                                  {scan.address}
                                </div>
                              </td>
                              <td style={{ padding: '12px', color: '#ff4444' }}>
                                {scan.vulnerabilities}
                              </td>
                              <td style={{ padding: '12px' }}>
                                <span
                                  style={{
                                    color:
                                      scan.score >= 80
                                        ? '#00ff88'
                                        : scan.score >= 60
                                        ? '#ffaa00'
                                        : '#ff4444',
                                    fontWeight: '600',
                                  }}
                                >
                                  {scan.score}%
                                </span>
                              </td>
                              <td style={{ padding: '12px', color: '#999999' }}>
                                {new Date(scan.timestamp).toLocaleString()}
                              </td>
                            </motion.tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </ScrollReveal>
              )}
            </motion.div>
          )}

          {activeTab === 'simulations' && (
            <motion.div
              key="simulations"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Simulation Engine Content */}
              <ScrollReveal delay={0.2}>
                <div
                  style={{
                    backgroundColor: 'rgba(0, 0, 0, 0.6)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(0, 255, 255, 0.3)',
                    borderRadius: '16px',
                    padding: '24px',
                    marginBottom: '24px',
                    boxShadow: '0 0 30px rgba(0, 255, 255, 0.2)',
                  }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '24px',
                    }}
                  >
                    <div>
                      <h2
                        style={{
                          fontSize: '24px',
                          fontWeight: '700',
                          color: '#00ffff',
                          margin: '0 0 8px 0',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                        }}
                      >
                        <Activity size={24} />
                        Simulation Engine
                      </h2>
                      <p
                        style={{
                          fontSize: '14px',
                          color: '#999999',
                          margin: '0',
                        }}
                      >
                        Advanced blockchain simulation and testing environment
                      </p>
                    </div>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setIsCreatingSimulation(true)}
                      style={{
                        padding: '12px 24px',
                        backgroundColor: 'rgba(0, 255, 255, 0.2)',
                        border: '1px solid rgba(0, 255, 255, 0.3)',
                        borderRadius: '12px',
                        color: '#00ffff',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <Plus size={16} />
                      New Simulation
                    </motion.button>
                  </div>

                  {/* Simulation Stats */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                      gap: '16px',
                      marginBottom: '32px',
                    }}
                  >
                    {[
                      {
                        label: 'Total Simulations',
                        value: simulationStats.totalSimulations,
                        icon: Activity,
                        color: '#00ffff',
                      },
                      {
                        label: 'Active Environments',
                        value: simulationStats.activeEnvironments,
                        icon: Cpu,
                        color: '#00ff88',
                      },
                      {
                        label: 'Tests Completed',
                        value: simulationStats.completedTests,
                        icon: CheckCircle,
                        color: '#ffaa00',
                      },
                      {
                        label: 'AI Analysis Runs',
                        value: simulationStats.aiAnalysisRuns,
                        icon: TrendingUp,
                        color: '#ff4444',
                      },
                    ].map((stat, index) => (
                      <motion.div
                        key={stat.label}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3, delay: 0.1 * index }}
                        whileHover={{ scale: 1.05, y: -5 }}
                        style={{
                          backgroundColor: 'rgba(0, 0, 0, 0.4)',
                          backdropFilter: 'blur(10px)',
                          border: `1px solid ${stat.color}30`,
                          borderRadius: '12px',
                          padding: '16px',
                          boxShadow: `0 0 20px ${stat.color}20`,
                          position: 'relative',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            position: 'absolute',
                            top: 0,
                            right: 0,
                            bottom: 0,
                            left: 0,
                            background: `linear-gradient(135deg, ${stat.color}05, transparent)`,
                          }}
                        />
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            position: 'relative',
                          }}
                        >
                          <div
                            style={{
                              width: '32px',
                              height: '32px',
                              borderRadius: '8px',
                              backgroundColor: `${stat.color}20`,
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              border: `1px solid ${stat.color}60`,
                            }}
                          >
                            <stat.icon size={16} color={stat.color} />
                          </div>
                          <div style={{ flex: 1 }}>
                            <div
                              style={{
                                fontSize: '20px',
                                fontWeight: '700',
                                color: stat.color,
                                lineHeight: 1,
                              }}
                            >
                              <LiveCounter value={stat.value} duration={2000} />
                            </div>
                            <div
                              style={{
                                fontSize: '11px',
                                color: '#999999',
                                textTransform: 'uppercase',
                                letterSpacing: '1px',
                                marginTop: '4px',
                              }}
                            >
                              {stat.label}
                            </div>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>

                  {/* Environment & Scenario Controls */}
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr',
                      gap: '24px',
                      marginBottom: '24px',
                    }}
                  >
                    {/* Environment Management */}
                    <div
                      style={{
                        backgroundColor: 'rgba(0, 0, 0, 0.4)',
                        border: '1px solid rgba(0, 255, 136, 0.3)',
                        borderRadius: '12px',
                        padding: '20px',
                      }}
                    >
                      <h3
                        style={{
                          fontSize: '16px',
                          fontWeight: '600',
                          color: '#00ff88',
                          margin: '0 0 16px 0',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                        }}
                      >
                        <Cpu size={16} />
                        Environment Control
                      </h3>

                      <div style={{ marginBottom: '16px' }}>
                        <label
                          style={{
                            display: 'block',
                            fontSize: '12px',
                            color: '#cccccc',
                            marginBottom: '8px',
                            fontWeight: '500',
                          }}
                        >
                          Environment Type
                        </label>
                        <select
                          value={environmentType || 'mainnet_fork'}
                          onChange={e => setEnvironmentType(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '10px 12px',
                            backgroundColor: 'rgba(0, 0, 0, 0.6)',
                            border: '1px solid rgba(0, 255, 136, 0.3)',
                            borderRadius: '8px',
                            color: '#ffffff',
                            fontSize: '13px',
                            outline: 'none',
                          }}
                        >
                          <option value="mainnet_fork">Mainnet Fork</option>
                          <option value="custom_network">Custom Network</option>
                          <option value="historical">Historical Recreation</option>
                          <option value="testnet">Testnet Environment</option>
                        </select>
                      </div>

                      <div style={{ marginBottom: '16px' }}>
                        <label
                          style={{
                            display: 'block',
                            fontSize: '12px',
                            color: '#cccccc',
                            marginBottom: '8px',
                            fontWeight: '500',
                          }}
                        >
                          Network
                        </label>
                        <select
                          value={networkType || 'ethereum'}
                          onChange={e => setNetworkType(e.target.value)}
                          style={{
                            width: '100%',
                            padding: '10px 12px',
                            backgroundColor: 'rgba(0, 0, 0, 0.6)',
                            border: '1px solid rgba(0, 255, 136, 0.3)',
                            borderRadius: '8px',
                            color: '#ffffff',
                            fontSize: '13px',
                            outline: 'none',
                          }}
                        >
                          <option value="ethereum">Ethereum</option>
                          <option value="polygon">Polygon</option>
                          <option value="bsc">Binance Smart Chain</option>
                          <option value="avalanche">Avalanche</option>
                          <option value="arbitrum">Arbitrum</option>
                        </select>
                      </div>

                      <div style={{ marginBottom: '16px' }}>
                        <label
                          style={{
                            display: 'block',
                            fontSize: '12px',
                            color: '#cccccc',
                            marginBottom: '8px',
                            fontWeight: '500',
                          }}
                        >
                          Fork Block Number
                        </label>
                        <input
                          type="number"
                          value={forkBlockNumber || ''}
                          onChange={e => setForkBlockNumber(e.target.value)}
                          placeholder="18500000"
                          style={{
                            width: '100%',
                            padding: '10px 12px',
                            backgroundColor: 'rgba(0, 0, 0, 0.6)',
                            border: '1px solid rgba(0, 255, 136, 0.3)',
                            borderRadius: '8px',
                            color: '#ffffff',
                            fontSize: '13px',
                            fontFamily: 'monospace',
                            outline: 'none',
                          }}
                        />
                      </div>

                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        style={{
                          width: '100%',
                          padding: '12px',
                          backgroundColor: 'rgba(0, 255, 136, 0.2)',
                          border: '1px solid rgba(0, 255, 136, 0.3)',
                          borderRadius: '8px',
                          color: '#00ff88',
                          fontSize: '14px',
                          fontWeight: '600',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                        }}
                      >
                        <Play size={16} />
                        Create Environment
                      </motion.button>
                    </div>

                    {/* Simulation Scenarios */}
                    <div
                      style={{
                        backgroundColor: 'rgba(0, 0, 0, 0.4)',
                        border: '1px solid rgba(255, 170, 0, 0.3)',
                        borderRadius: '12px',
                        padding: '20px',
                      }}
                    >
                      <h3
                        style={{
                          fontSize: '16px',
                          fontWeight: '600',
                          color: '#ffaa00',
                          margin: '0 0 16px 0',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                        }}
                      >
                        <Target size={16} />
                        Scenario Builder
                      </h3>

                      <div
                        style={{
                          display: 'grid',
                          gridTemplateColumns: '1fr 1fr',
                          gap: '8px',
                          marginBottom: '16px',
                        }}
                      >
                        {[
                          { name: 'Flash Loan Attack', color: '#ff4444' },
                          { name: 'Reentrancy Test', color: '#ff6600' },
                          { name: 'Oracle Manipulation', color: '#ffaa00' },
                          { name: 'Governance Attack', color: '#00ffff' },
                          { name: 'MEV Simulation', color: '#9966ff' },
                          { name: 'Custom Scenario', color: '#00ff88' },
                        ].map((scenario, index) => (
                          <motion.button
                            key={scenario.name}
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            style={{
                              padding: '8px 12px',
                              backgroundColor: `${scenario.color}20`,
                              border: `1px solid ${scenario.color}30`,
                              borderRadius: '6px',
                              color: scenario.color,
                              fontSize: '11px',
                              fontWeight: '600',
                              cursor: 'pointer',
                              textAlign: 'center',
                            }}
                          >
                            {scenario.name}
                          </motion.button>
                        ))}
                      </div>

                      <div style={{ marginBottom: '16px' }}>
                        <label
                          style={{
                            display: 'block',
                            fontSize: '12px',
                            color: '#cccccc',
                            marginBottom: '8px',
                            fontWeight: '500',
                          }}
                        >
                          Target Contract
                        </label>
                        <input
                          type="text"
                          value={targetContract || ''}
                          onChange={e => setTargetContract(e.target.value)}
                          placeholder="0x... or contract name"
                          style={{
                            width: '100%',
                            padding: '10px 12px',
                            backgroundColor: 'rgba(0, 0, 0, 0.6)',
                            border: '1px solid rgba(255, 170, 0, 0.3)',
                            borderRadius: '8px',
                            color: '#ffffff',
                            fontSize: '13px',
                            fontFamily: 'monospace',
                            outline: 'none',
                          }}
                        />
                      </div>

                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        style={{
                          width: '100%',
                          padding: '12px',
                          backgroundColor: 'rgba(255, 170, 0, 0.2)',
                          border: '1px solid rgba(255, 170, 0, 0.3)',
                          borderRadius: '8px',
                          color: '#ffaa00',
                          fontSize: '14px',
                          fontWeight: '600',
                          cursor: 'pointer',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          gap: '8px',
                        }}
                      >
                        <Zap size={16} />
                        Start Simulation
                      </motion.button>
                    </div>
                  </div>

                  {/* Active Simulations */}
                  <div
                    style={{
                      backgroundColor: 'rgba(0, 0, 0, 0.4)',
                      border: '1px solid rgba(255, 68, 68, 0.3)',
                      borderRadius: '12px',
                      padding: '20px',
                      marginBottom: '24px',
                    }}
                  >
                    <h3
                      style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#ff4444',
                        margin: '0 0 16px 0',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <Activity size={16} />
                      Active Simulations
                    </h3>

                    <div style={{ display: 'grid', gap: '12px' }}>
                      {[
                        {
                          id: 'sim_001',
                          name: 'Flash Loan Attack on Uniswap V3',
                          status: 'running',
                          progress: 67,
                          startTime: '2 minutes ago',
                          type: 'Security Test',
                          environment: 'Ethereum Mainnet Fork',
                        },
                        {
                          id: 'sim_002',
                          name: 'Reentrancy Vulnerability Analysis',
                          status: 'completed',
                          progress: 100,
                          startTime: '15 minutes ago',
                          type: 'Vulnerability Test',
                          environment: 'Custom Network',
                        },
                        {
                          id: 'sim_003',
                          name: 'Oracle Price Manipulation',
                          status: 'queued',
                          progress: 0,
                          startTime: 'Pending',
                          type: 'Economic Test',
                          environment: 'Polygon Fork',
                        },
                      ].map((sim, index) => (
                        <motion.div
                          key={sim.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          style={{
                            padding: '16px',
                            backgroundColor: 'rgba(0, 0, 0, 0.6)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            borderRadius: '8px',
                            display: 'grid',
                            gridTemplateColumns: '1fr auto',
                            gap: '16px',
                            alignItems: 'center',
                          }}
                        >
                          <div>
                            <div
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '12px',
                                marginBottom: '8px',
                              }}
                            >
                              <h4
                                style={{
                                  fontSize: '14px',
                                  fontWeight: '600',
                                  color: '#ffffff',
                                  margin: '0',
                                }}
                              >
                                {sim.name}
                              </h4>
                              <span
                                style={{
                                  padding: '2px 8px',
                                  borderRadius: '4px',
                                  fontSize: '10px',
                                  fontWeight: '600',
                                  textTransform: 'uppercase',
                                  backgroundColor:
                                    sim.status === 'running'
                                      ? 'rgba(255, 170, 0, 0.2)'
                                      : sim.status === 'completed'
                                      ? 'rgba(0, 255, 136, 0.2)'
                                      : 'rgba(100, 100, 100, 0.2)',
                                  color:
                                    sim.status === 'running'
                                      ? '#ffaa00'
                                      : sim.status === 'completed'
                                      ? '#00ff88'
                                      : '#999999',
                                }}
                              >
                                {sim.status}
                              </span>
                            </div>
                            <div
                              style={{
                                display: 'flex',
                                gap: '16px',
                                fontSize: '12px',
                                color: '#999999',
                              }}
                            >
                              <span>Type: {sim.type}</span>
                              <span>Environment: {sim.environment}</span>
                              <span>Started: {sim.startTime}</span>
                            </div>
                            {sim.status === 'running' && (
                              <div
                                style={{
                                  marginTop: '8px',
                                  width: '100%',
                                  height: '4px',
                                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                  borderRadius: '2px',
                                  overflow: 'hidden',
                                }}
                              >
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${sim.progress}%` }}
                                  style={{
                                    height: '100%',
                                    backgroundColor: '#ffaa00',
                                    borderRadius: '2px',
                                  }}
                                />
                              </div>
                            )}
                          </div>
                          <div style={{ display: 'flex', gap: '8px' }}>
                            {sim.status === 'running' && (
                              <motion.button
                                whileHover={{ scale: 1.1 }}
                                whileTap={{ scale: 0.9 }}
                                style={{
                                  padding: '6px',
                                  backgroundColor: 'rgba(255, 68, 68, 0.2)',
                                  border: '1px solid rgba(255, 68, 68, 0.3)',
                                  borderRadius: '6px',
                                  color: '#ff4444',
                                  cursor: 'pointer',
                                }}
                              >
                                <Pause size={12} />
                              </motion.button>
                            )}
                            <motion.button
                              whileHover={{ scale: 1.1 }}
                              whileTap={{ scale: 0.9 }}
                              style={{
                                padding: '6px',
                                backgroundColor: 'rgba(0, 255, 255, 0.2)',
                                border: '1px solid rgba(0, 255, 255, 0.3)',
                                borderRadius: '6px',
                                color: '#00ffff',
                                cursor: 'pointer',
                              }}
                            >
                              <Eye size={12} />
                            </motion.button>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>

                  {/* AI Analysis Results */}
                  <div
                    style={{
                      backgroundColor: 'rgba(0, 0, 0, 0.4)',
                      border: '1px solid rgba(153, 102, 255, 0.3)',
                      borderRadius: '12px',
                      padding: '20px',
                    }}
                  >
                    <h3
                      style={{
                        fontSize: '16px',
                        fontWeight: '600',
                        color: '#9966ff',
                        margin: '0 0 16px 0',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <TrendingUp size={16} />
                      AI Analysis & Insights
                    </h3>

                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '16px',
                      }}
                    >
                      <div
                        style={{
                          padding: '16px',
                          backgroundColor: 'rgba(153, 102, 255, 0.1)',
                          border: '1px solid rgba(153, 102, 255, 0.2)',
                          borderRadius: '8px',
                        }}
                      >
                        <h4
                          style={{
                            fontSize: '14px',
                            fontWeight: '600',
                            color: '#9966ff',
                            margin: '0 0 12px 0',
                          }}
                        >
                          Model Performance
                        </h4>
                        <div style={{ fontSize: '12px', color: '#cccccc' }}>
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              marginBottom: '6px',
                            }}
                          >
                            <span>Exploit Detection Accuracy:</span>
                            <span style={{ color: '#00ff88' }}>94.7%</span>
                          </div>
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              marginBottom: '6px',
                            }}
                          >
                            <span>False Positive Rate:</span>
                            <span style={{ color: '#ffaa00' }}>2.1%</span>
                          </div>
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                            }}
                          >
                            <span>Pattern Recognition:</span>
                            <span style={{ color: '#00ffff' }}>87.3%</span>
                          </div>
                        </div>
                      </div>

                      <div
                        style={{
                          padding: '16px',
                          backgroundColor: 'rgba(0, 255, 136, 0.1)',
                          border: '1px solid rgba(0, 255, 136, 0.2)',
                          borderRadius: '8px',
                        }}
                      >
                        <h4
                          style={{
                            fontSize: '14px',
                            fontWeight: '600',
                            color: '#00ff88',
                            margin: '0 0 12px 0',
                          }}
                        >
                          Recent Discoveries
                        </h4>
                        <div style={{ fontSize: '12px', color: '#cccccc' }}>
                          <div style={{ marginBottom: '6px' }}>
                            • Novel reentrancy pattern detected
                          </div>
                          <div style={{ marginBottom: '6px' }}>
                            • Flash loan vulnerability in DeFi protocol
                          </div>
                          <div>• Oracle manipulation attack vector</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </ScrollReveal>
            </motion.div>
          )}

          {activeTab === 'plugins' && (
            <motion.div
              key="plugins"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Plugin Manager Header */}
              <ScrollReveal delay={0.1}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    marginBottom: '32px',
                    padding: '24px',
                    background:
                      'linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(0, 0, 0, 0.2) 100%)',
                    border: '1px solid rgba(255, 107, 53, 0.3)',
                    borderRadius: '16px',
                    backdropFilter: 'blur(20px)',
                  }}
                >
                  <div>
                    <h3
                      style={{
                        fontSize: '24px',
                        fontWeight: '700',
                        color: '#ff6b35',
                        marginBottom: '8px',
                        fontFamily: "'JetBrains Mono', monospace",
                      }}
                    >
                      Plugin Management System
                    </h3>
                    <p style={{ color: '#cccccc', fontSize: '14px' }}>
                      Configure security analysis plugins for enhanced scanning
                      capabilities
                    </p>
                  </div>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => enableAllPlugins('quickScan')}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: 'rgba(0, 255, 136, 0.2)',
                        color: '#00ff88',
                        border: '1px solid rgba(0, 255, 136, 0.3)',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <Zap size={12} />
                      All Quick
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => enableAllPlugins('deepScan')}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: 'rgba(0, 255, 255, 0.2)',
                        color: '#00ffff',
                        border: '1px solid rgba(0, 255, 255, 0.3)',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <Target size={12} />
                      All Deep
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={resetPluginsToDefault}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: 'rgba(255, 255, 255, 0.1)',
                        color: '#cccccc',
                        border: '1px solid rgba(255, 255, 255, 0.2)',
                        borderRadius: '6px',
                        fontSize: '12px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                      }}
                    >
                      <RefreshCw size={12} />
                      Reset
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setShowPluginInstall(!showPluginInstall)}
                      style={{
                        padding: '12px 24px',
                        backgroundColor: '#ff6b35',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '14px',
                        fontWeight: '600',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <Plus size={16} />
                      Install Plugin
                    </motion.button>
                  </div>
                </div>
              </ScrollReveal>

              {/* Plugin Installation Panel */}
              <AnimatePresence>
                {showPluginInstall && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                    style={{ marginBottom: '32px' }}
                  >
                    <ScrollReveal delay={0.2}>
                      <div
                        style={{
                          padding: '24px',
                          background:
                            'linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(42, 42, 42, 0.4) 100%)',
                          border: '1px solid rgba(255, 107, 53, 0.2)',
                          borderRadius: '16px',
                          backdropFilter: 'blur(20px)',
                        }}
                      >
                        <h4
                          style={{
                            fontSize: '18px',
                            fontWeight: '600',
                            color: '#ff6b35',
                            marginBottom: '16px',
                          }}
                        >
                          Dynamic Plugin Installation
                        </h4>

                        {/* Installation Source Selector */}
                        <div
                          style={{
                            display: 'flex',
                            gap: '8px',
                            marginBottom: '16px',
                          }}
                        >
                          {[
                            {
                              id: 'marketplace',
                              label: 'Marketplace',
                              icon: '🏪',
                            },
                            { id: 'git', label: 'Git Repository', icon: '🔗' },
                            { id: 'docker', label: 'Docker Image', icon: '🐳' },
                            { id: 'upload', label: 'File Upload', icon: '📁' },
                          ].map(source => (
                            <motion.button
                              key={source.id}
                              whileHover={{ scale: 1.02 }}
                              onClick={() => setPluginInstallSource(source.id as any)}
                              style={{
                                padding: '8px 16px',
                                backgroundColor:
                                  pluginInstallSource === source.id
                                    ? '#ff6b35'
                                    : 'rgba(255, 107, 53, 0.1)',
                                color:
                                  pluginInstallSource === source.id
                                    ? 'white'
                                    : '#ff6b35',
                                border: `1px solid ${
                                  pluginInstallSource === source.id
                                    ? '#ff6b35'
                                    : 'rgba(255, 107, 53, 0.3)'
                                }`,
                                borderRadius: '6px',
                                fontSize: '12px',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '4px',
                              }}
                            >
                              <span>{source.icon}</span>
                              {source.label}
                            </motion.button>
                          ))}
                        </div>

                        {/* URL Input */}
                        <div
                          style={{
                            display: 'flex',
                            gap: '12px',
                            alignItems: 'center',
                          }}
                        >
                          <input
                            type="text"
                            value={pluginUrl || ''}
                            onChange={e => setPluginUrl(e.target.value)}
                            placeholder={
                              pluginInstallSource === 'marketplace'
                                ? 'Search marketplace...'
                                : pluginInstallSource === 'git'
                                ? 'https://github.com/user/plugin.git'
                                : pluginInstallSource === 'docker'
                                ? 'registry/plugin:latest'
                                : 'Select file...'
                            }
                            style={{
                              flex: 1,
                              padding: '12px 16px',
                              backgroundColor: 'rgba(0, 0, 0, 0.4)',
                              border: '1px solid rgba(255, 107, 53, 0.3)',
                              borderRadius: '8px',
                              color: 'white',
                              fontSize: '14px',
                              outline: 'none',
                            }}
                          />
                          <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => {
                              setIsInstallingPlugin(true);
                              setTimeout(() => {
                                setIsInstallingPlugin(false);
                                toast.success('Plugin installed successfully');
                                setShowPluginInstall(false);
                              }, 2000);
                            }}
                            disabled={isInstallingPlugin || !pluginUrl}
                            style={{
                              padding: '12px 24px',
                              backgroundColor: '#ff6b35',
                              color: 'white',
                              border: 'none',
                              borderRadius: '8px',
                              fontSize: '14px',
                              fontWeight: '600',
                              cursor: isInstallingPlugin ? 'not-allowed' : 'pointer',
                              opacity: isInstallingPlugin || !pluginUrl ? 0.6 : 1,
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                            }}
                          >
                            {isInstallingPlugin ? (
                              <>
                                <Loader2 size={16} className="animate-spin" />
                                Installing...
                              </>
                            ) : (
                              <>
                                <Download size={16} />
                                Install
                              </>
                            )}
                          </motion.button>
                        </div>
                      </div>
                    </ScrollReveal>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Core Security Plugins */}
              <ScrollReveal delay={0.3}>
                <div style={{ marginBottom: '32px' }}>
                  <h4
                    style={{
                      fontSize: '18px',
                      fontWeight: '600',
                      color: '#ff6b35',
                      marginBottom: '16px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                  >
                    <Shield size={20} />
                    Core Security Plugins
                  </h4>

                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                      gap: '16px',
                    }}
                  >
                    {[
                      {
                        id: 'mythx',
                        name: 'MythX',
                        description:
                          'Professional smart contract security analysis platform',
                        category: 'Static Analysis',
                        status: 'official',
                        icon: '⚡',
                        capabilities: [
                          'Vulnerability Detection',
                          'Gas Optimization',
                          'Best Practices',
                        ],
                      },
                      {
                        id: 'slither',
                        name: 'Slither',
                        description: 'Static analysis framework for Solidity contracts',
                        category: 'Static Analysis',
                        status: 'open-source',
                        icon: '🐍',
                        capabilities: [
                          'Code Quality',
                          'Security Issues',
                          'Code Understanding',
                        ],
                      },
                      {
                        id: 'manticore',
                        name: 'Manticore',
                        description:
                          'Symbolic execution tool for analysis of binaries and smart contracts',
                        category: 'Symbolic Execution',
                        status: 'research',
                        icon: '🔬',
                        capabilities: [
                          'Deep Analysis',
                          'Symbolic Execution',
                          'Property Verification',
                        ],
                      },
                      {
                        id: 'mythril',
                        name: 'Mythril',
                        description:
                          'Security analysis tool for Ethereum smart contracts',
                        category: 'Static/Dynamic',
                        status: 'open-source',
                        icon: '🛡️',
                        capabilities: [
                          'Vulnerability Scanning',
                          'Symbolic Analysis',
                          'Integration Ready',
                        ],
                      },
                      {
                        id: 'customAI',
                        name: 'Custom AI',
                        description:
                          'Advanced AI-powered vulnerability detection and analysis',
                        category: 'AI/ML',
                        status: 'experimental',
                        icon: '🤖',
                        capabilities: [
                          'AI Detection',
                          'Pattern Recognition',
                          'Adaptive Learning',
                        ],
                      },
                    ].map(plugin => (
                      <motion.div
                        key={plugin.id}
                        whileHover={{ scale: 1.02 }}
                        style={{
                          padding: '20px',
                          background:
                            'linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(42, 42, 42, 0.4) 100%)',
                          border: '1px solid rgba(255, 107, 53, 0.2)',
                          borderRadius: '12px',
                          backdropFilter: 'blur(20px)',
                        }}
                      >
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'flex-start',
                            marginBottom: '12px',
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                            }}
                          >
                            <span style={{ fontSize: '20px' }}>{plugin.icon}</span>
                            <div>
                              <h5
                                style={{
                                  fontSize: '16px',
                                  fontWeight: '600',
                                  color: 'white',
                                  margin: 0,
                                }}
                              >
                                {plugin.name}
                              </h5>
                              <span
                                style={{
                                  fontSize: '11px',
                                  color:
                                    plugin.status === 'official'
                                      ? '#00ff88'
                                      : plugin.status === 'experimental'
                                      ? '#ffaa00'
                                      : '#00ffff',
                                  textTransform: 'uppercase',
                                  fontWeight: '500',
                                }}
                              >
                                {plugin.status}
                              </span>
                            </div>
                          </div>
                          <span
                            style={{
                              fontSize: '10px',
                              color: '#cccccc',
                              backgroundColor: 'rgba(255, 255, 255, 0.1)',
                              padding: '2px 6px',
                              borderRadius: '4px',
                            }}
                          >
                            {plugin.category}
                          </span>
                        </div>

                        <p
                          style={{
                            fontSize: '13px',
                            color: '#cccccc',
                            marginBottom: '12px',
                            lineHeight: '1.4',
                          }}
                        >
                          {plugin.description}
                        </p>

                        <div style={{ marginBottom: '16px' }}>
                          <div
                            style={{
                              fontSize: '11px',
                              color: '#999',
                              marginBottom: '6px',
                            }}
                          >
                            Capabilities:
                          </div>
                          <div
                            style={{
                              display: 'flex',
                              flexWrap: 'wrap',
                              gap: '4px',
                            }}
                          >
                            {plugin.capabilities.map((cap, idx) => (
                              <span
                                key={idx}
                                style={{
                                  fontSize: '10px',
                                  color: '#ff6b35',
                                  backgroundColor: 'rgba(255, 107, 53, 0.1)',
                                  padding: '2px 6px',
                                  borderRadius: '4px',
                                  border: '1px solid rgba(255, 107, 53, 0.2)',
                                }}
                              >
                                {cap}
                              </span>
                            ))}
                          </div>
                        </div>

                        {/* Quick Scan / Deep Scan Toggles */}
                        <div
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                            }}
                          >
                            <Zap size={14} style={{ color: '#00ff88' }} />
                            <span style={{ fontSize: '12px', color: '#cccccc' }}>
                              Quick Scan
                            </span>
                            <Switch
                              checked={enabledPlugins[plugin.id]?.quickScan || false}
                              onCheckedChange={checked => {
                                setEnabledPlugins(prev => ({
                                  ...prev,
                                  [plugin.id]: {
                                    ...prev[plugin.id],
                                    quickScan: checked,
                                  },
                                }));
                              }}
                            />
                          </div>
                          <div
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                            }}
                          >
                            <Target size={14} style={{ color: '#00ffff' }} />
                            <span style={{ fontSize: '12px', color: '#cccccc' }}>
                              Deep Scan
                            </span>
                            <Switch
                              checked={enabledPlugins[plugin.id]?.deepScan || false}
                              onCheckedChange={checked => {
                                setEnabledPlugins(prev => ({
                                  ...prev,
                                  [plugin.id]: {
                                    ...prev[plugin.id],
                                    deepScan: checked,
                                  },
                                }));
                              }}
                            />
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </ScrollReveal>

              {/* Custom Plugins Section */}
              <ScrollReveal delay={0.4}>
                <div>
                  <h4
                    style={{
                      fontSize: '18px',
                      fontWeight: '600',
                      color: '#ff6b35',
                      marginBottom: '16px',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                    }}
                  >
                    <Code size={20} />
                    Custom Plugins ({customPlugins.length})
                  </h4>

                  {customPlugins.length === 0 ? (
                    <div
                      style={{
                        padding: '40px',
                        textAlign: 'center',
                        background:
                          'linear-gradient(135deg, rgba(0, 0, 0, 0.4) 0%, rgba(42, 42, 42, 0.2) 100%)',
                        border: '2px dashed rgba(255, 107, 53, 0.3)',
                        borderRadius: '12px',
                        color: '#cccccc',
                      }}
                    >
                      <Package
                        size={32}
                        style={{ margin: '0 auto 12px', opacity: 0.5 }}
                      />
                      <p style={{ fontSize: '14px', marginBottom: '8px' }}>
                        No custom plugins installed
                      </p>
                      <p style={{ fontSize: '12px', opacity: 0.7 }}>
                        Install plugins from marketplace, Git repos, Docker images, or
                        file uploads
                      </p>
                    </div>
                  ) : (
                    <div
                      style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                        gap: '16px',
                      }}
                    >
                      {customPlugins.map((plugin, idx) => (
                        <motion.div
                          key={idx}
                          whileHover={{ scale: 1.02 }}
                          style={{
                            padding: '16px',
                            background:
                              'linear-gradient(135deg, rgba(0, 0, 0, 0.6) 0%, rgba(42, 42, 42, 0.4) 100%)',
                            border: '1px solid rgba(255, 107, 53, 0.2)',
                            borderRadius: '12px',
                            backdropFilter: 'blur(20px)',
                          }}
                        >
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              marginBottom: '8px',
                            }}
                          >
                            <span
                              style={{
                                fontSize: '14px',
                                fontWeight: '600',
                                color: 'white',
                              }}
                            >
                              {plugin.name}
                            </span>
                            <motion.button
                              whileHover={{ scale: 1.1 }}
                              style={{
                                padding: '4px',
                                backgroundColor: 'rgba(255, 107, 53, 0.2)',
                                border: '1px solid rgba(255, 107, 53, 0.3)',
                                borderRadius: '4px',
                                color: '#ff6b35',
                                cursor: 'pointer',
                              }}
                            >
                              <Trash2 size={12} />
                            </motion.button>
                          </div>
                          <p
                            style={{
                              fontSize: '12px',
                              color: '#cccccc',
                              marginBottom: '12px',
                            }}
                          >
                            {plugin.description}
                          </p>
                          <div
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                            }}
                          >
                            <div
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                              }}
                            >
                              <span style={{ fontSize: '11px', color: '#cccccc' }}>
                                Quick
                              </span>
                              <Switch />
                            </div>
                            <div
                              style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '8px',
                              }}
                            >
                              <span style={{ fontSize: '11px', color: '#cccccc' }}>
                                Deep
                              </span>
                              <Switch />
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </div>
              </ScrollReveal>

              {/* Plugin Stats */}
              <ScrollReveal delay={0.5}>
                <div style={{ marginTop: '32px' }}>
                  <div
                    style={{
                      display: 'grid',
                      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                      gap: '16px',
                      padding: '20px',
                      background:
                        'linear-gradient(135deg, rgba(255, 107, 53, 0.05) 0%, rgba(0, 0, 0, 0.2) 100%)',
                      border: '1px solid rgba(255, 107, 53, 0.2)',
                      borderRadius: '12px',
                    }}
                  >
                    {[
                      {
                        label: 'Active Plugins',
                        value: Object.values(enabledPlugins).filter(
                          p => p.quickScan || p.deepScan,
                        ).length,
                        color: '#00ff88',
                      },
                      {
                        label: 'Quick Scan Enabled',
                        value: Object.values(enabledPlugins).filter(p => p.quickScan)
                          .length,
                        color: '#00ffff',
                      },
                      {
                        label: 'Deep Scan Enabled',
                        value: Object.values(enabledPlugins).filter(p => p.deepScan)
                          .length,
                        color: '#ff6b35',
                      },
                      {
                        label: 'Custom Plugins',
                        value: customPlugins.length,
                        color: '#ffaa00',
                      },
                    ].map((stat, idx) => (
                      <div key={idx} style={{ textAlign: 'center' }}>
                        <div
                          style={{
                            fontSize: '24px',
                            fontWeight: '700',
                            color: stat.color,
                            marginBottom: '4px',
                          }}
                        >
                          <LiveCounter value={stat.value} duration={1000} />
                        </div>
                        <div
                          style={{
                            fontSize: '12px',
                            color: '#cccccc',
                            textTransform: 'uppercase',
                            letterSpacing: '0.5px',
                          }}
                        >
                          {stat.label}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </ScrollReveal>
            </motion.div>
          )}

          {activeTab === 'honeypot' && (
            <motion.div
              key="honeypot"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Honeypot Detector Header */}
              <ScrollReveal delay={0.1}>
                <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: 'spring', stiffness: 300 }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #ff444420, #ff444410)',
                      border: '2px solid #ff444440',
                      marginBottom: '20px',
                    }}
                  >
                    <Target size={36} style={{ color: '#ff4444' }} />
                  </motion.div>
                  <h2
                    style={{
                      fontSize: '32px',
                      fontWeight: '700',
                      color: '#ffffff',
                      marginBottom: '8px',
                    }}
                  >
                    Honeypot Detector
                  </h2>
                  <p
                    style={{
                      fontSize: '16px',
                      color: '#cccccc',
                      maxWidth: '600px',
                      margin: '0 auto',
                    }}
                  >
                    Advanced threat detection system monitoring for honeypot contracts
                    and malicious patterns
                  </p>
                </div>
              </ScrollReveal>

              {/* Honeypot Stats */}
              <ScrollReveal delay={0.2}>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '20px',
                    marginBottom: '40px',
                  }}
                >
                  {[
                    {
                      label: 'Total Detections',
                      value: honeypotStats.totalDetections,
                      color: '#ff4444',
                      icon: Target,
                    },
                    {
                      label: 'Active Threats',
                      value: honeypotStats.activeThreats,
                      color: '#ff6b35',
                      icon: AlertTriangle,
                    },
                    {
                      label: 'Success Rate',
                      value: honeypotStats.successRate,
                      suffix: '%',
                      color: '#00ff88',
                      icon: CheckCircle,
                    },
                    {
                      label: 'Avg Response',
                      value: honeypotStats.avgResponseTime,
                      suffix: 's',
                      color: '#00ffff',
                      icon: Timer,
                    },
                    {
                      label: 'Contracts Monitored',
                      value: honeypotStats.contractsMonitored,
                      color: '#9333ea',
                      icon: Eye,
                    },
                    {
                      label: 'Daily Blocks',
                      value: honeypotStats.dailyBlocks,
                      color: '#ffaa00',
                      icon: Database,
                    },
                  ].map((stat, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                      style={{
                        padding: '20px',
                        background: `linear-gradient(135deg, ${stat.color}15, rgba(0, 0, 0, 0.2))`,
                        border: `1px solid ${stat.color}30`,
                        borderRadius: '12px',
                        textAlign: 'center',
                      }}
                    >
                      <stat.icon
                        size={24}
                        style={{ color: stat.color, marginBottom: '8px' }}
                      />
                      <div
                        style={{
                          fontSize: '24px',
                          fontWeight: '700',
                          color: stat.color,
                          marginBottom: '4px',
                        }}
                      >
                        <LiveCounter
                          value={stat.value}
                          suffix={stat.suffix || ''}
                          duration={1500}
                        />
                      </div>
                      <div
                        style={{
                          fontSize: '12px',
                          color: '#cccccc',
                          textTransform: 'uppercase',
                        }}
                      >
                        {stat.label}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </ScrollReveal>

              {/* Live Detection Toggle */}
              <ScrollReveal delay={0.4}>
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '30px',
                    padding: '16px',
                    background: 'rgba(255, 68, 68, 0.1)',
                    border: '1px solid rgba(255, 68, 68, 0.3)',
                    borderRadius: '12px',
                    maxWidth: '300px',
                    margin: '0 auto 30px',
                  }}
                >
                  <Radar size={20} style={{ color: '#ff4444' }} />
                  <Label style={{ color: '#ffffff', fontWeight: '500' }}>
                    Live Detection
                  </Label>
                  <Switch
                    checked={isHoneypotLive}
                    onCheckedChange={setIsHoneypotLive}
                  />
                  {isHoneypotLive && (
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 2, repeat: Infinity }}
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        backgroundColor: '#ff4444',
                      }}
                    />
                  )}
                </div>
              </ScrollReveal>

              {/* Contract Input */}
              <ScrollReveal delay={0.5}>
                <div style={{ marginBottom: '30px' }}>
                  <div
                    style={{
                      background:
                        'linear-gradient(135deg, rgba(255, 68, 68, 0.1), rgba(0, 0, 0, 0.2))',
                      border: '1px solid rgba(255, 68, 68, 0.3)',
                      borderRadius: '12px',
                      padding: '24px',
                    }}
                  >
                    <h3
                      style={{
                        color: '#ff4444',
                        marginBottom: '16px',
                        fontSize: '18px',
                        fontWeight: '600',
                      }}
                    >
                      Analyze Contract for Honeypot Patterns
                    </h3>
                    <div
                      style={{
                        display: 'flex',
                        gap: '12px',
                        alignItems: 'center',
                      }}
                    >
                      <input
                        type="text"
                        placeholder="Enter contract address (0x...)"
                        style={{
                          flex: 1,
                          padding: '12px',
                          background: 'rgba(0, 0, 0, 0.5)',
                          border: '1px solid rgba(255, 68, 68, 0.3)',
                          borderRadius: '8px',
                          color: '#ffffff',
                          fontSize: '14px',
                        }}
                      />
                      <Button
                        style={{
                          background: 'linear-gradient(135deg, #ff4444, #ff6b35)',
                          border: 'none',
                          padding: '12px 24px',
                        }}
                      >
                        <Target size={16} />
                        Scan for Threats
                      </Button>
                    </div>
                  </div>
                </div>
              </ScrollReveal>

              {/* Recent Detections */}
              <ScrollReveal delay={0.6}>
                <div
                  style={{
                    background:
                      'linear-gradient(135deg, rgba(255, 68, 68, 0.05), rgba(0, 0, 0, 0.2))',
                    border: '1px solid rgba(255, 68, 68, 0.2)',
                    borderRadius: '12px',
                    padding: '24px',
                  }}
                >
                  <h3
                    style={{
                      color: '#ff4444',
                      marginBottom: '20px',
                      fontSize: '18px',
                      fontWeight: '600',
                    }}
                  >
                    Recent Threat Detections
                  </h3>
                  <div
                    style={{
                      fontSize: '14px',
                      color: '#cccccc',
                      textAlign: 'center',
                      padding: '40px',
                    }}
                  >
                    Live monitoring active - threat events will appear here
                  </div>
                </div>
              </ScrollReveal>
            </motion.div>
          )}

          {activeTab === 'bytecode' && (
            <motion.div
              key="bytecode"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              transition={{ duration: 0.3 }}
            >
              {/* Bytecode Matcher Header */}
              <ScrollReveal delay={0.1}>
                <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: 'spring', stiffness: 300 }}
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: 'linear-gradient(135deg, #9333ea20, #9333ea10)',
                      border: '2px solid #9333ea40',
                      marginBottom: '20px',
                    }}
                  >
                    <Binary size={36} style={{ color: '#9333ea' }} />
                  </motion.div>
                  <h2
                    style={{
                      fontSize: '32px',
                      fontWeight: '700',
                      color: '#ffffff',
                      marginBottom: '8px',
                    }}
                  >
                    Bytecode Matcher
                  </h2>
                  <p
                    style={{
                      fontSize: '16px',
                      color: '#cccccc',
                      maxWidth: '600px',
                      margin: '0 auto',
                    }}
                  >
                    Advanced bytecode analysis and similarity matching against known
                    threat patterns
                  </p>
                </div>
              </ScrollReveal>

              {/* Bytecode Stats */}
              <ScrollReveal delay={0.2}>
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '20px',
                    marginBottom: '40px',
                  }}
                >
                  {[
                    {
                      label: 'Total Scans',
                      value: bytecodeStats.totalScans,
                      color: '#9333ea',
                      icon: Binary,
                    },
                    {
                      label: 'Threats Detected',
                      value: bytecodeStats.threatsDetected,
                      color: '#ff4444',
                      icon: AlertTriangle,
                    },
                    {
                      label: 'False Positives',
                      value: bytecodeStats.falsePositives,
                      color: '#ffaa00',
                      icon: Flag,
                    },
                    {
                      label: 'Avg Similarity',
                      value: bytecodeStats.avgSimilarity,
                      suffix: '%',
                      color: '#00ff88',
                      icon: GitCompare,
                    },
                  ].map((stat, index) => (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.3 + index * 0.1 }}
                      style={{
                        padding: '20px',
                        background: `linear-gradient(135deg, ${stat.color}15, rgba(0, 0, 0, 0.2))`,
                        border: `1px solid ${stat.color}30`,
                        borderRadius: '12px',
                        textAlign: 'center',
                      }}
                    >
                      <stat.icon
                        size={24}
                        style={{ color: stat.color, marginBottom: '8px' }}
                      />
                      <div
                        style={{
                          fontSize: '24px',
                          fontWeight: '700',
                          color: stat.color,
                          marginBottom: '4px',
                        }}
                      >
                        <LiveCounter
                          value={stat.value}
                          suffix={stat.suffix || ''}
                          duration={1500}
                        />
                      </div>
                      <div
                        style={{
                          fontSize: '12px',
                          color: '#cccccc',
                          textTransform: 'uppercase',
                        }}
                      >
                        {stat.label}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </ScrollReveal>

              {/* Bytecode Input */}
              <ScrollReveal delay={0.4}>
                <div style={{ marginBottom: '30px' }}>
                  <div
                    style={{
                      background:
                        'linear-gradient(135deg, rgba(147, 51, 234, 0.1), rgba(0, 0, 0, 0.2))',
                      border: '1px solid rgba(147, 51, 234, 0.3)',
                      borderRadius: '12px',
                      padding: '24px',
                    }}
                  >
                    <h3
                      style={{
                        color: '#9333ea',
                        marginBottom: '16px',
                        fontSize: '18px',
                        fontWeight: '600',
                      }}
                    >
                      Analyze Bytecode Similarity
                    </h3>
                    <div style={{ marginBottom: '16px' }}>
                      <textarea
                        placeholder="Enter bytecode or paste contract address..."
                        style={{
                          width: '100%',
                          height: '120px',
                          padding: '12px',
                          background: 'rgba(0, 0, 0, 0.5)',
                          border: '1px solid rgba(147, 51, 234, 0.3)',
                          borderRadius: '8px',
                          color: '#ffffff',
                          fontSize: '14px',
                          fontFamily: 'monospace',
                          resize: 'vertical',
                        }}
                      />
                    </div>
                    <div
                      style={{
                        display: 'flex',
                        gap: '12px',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                      }}
                    >
                      <div style={{ display: 'flex', gap: '12px' }}>
                        <Button variant="outline" style={{ padding: '8px 16px' }}>
                          <Upload size={16} />
                          Upload File
                        </Button>
                        <Button variant="outline" style={{ padding: '8px 16px' }}>
                          <FileCode size={16} />
                          Load Example
                        </Button>
                      </div>
                      <Button
                        style={{
                          background: 'linear-gradient(135deg, #9333ea, #7c3aed)',
                          border: 'none',
                          padding: '12px 24px',
                        }}
                      >
                        <Search size={16} />
                        Analyze Similarity
                      </Button>
                    </div>
                  </div>
                </div>
              </ScrollReveal>

              {/* Analysis Results */}
              <ScrollReveal delay={0.5}>
                <div
                  style={{
                    background:
                      'linear-gradient(135deg, rgba(147, 51, 234, 0.05), rgba(0, 0, 0, 0.2))',
                    border: '1px solid rgba(147, 51, 234, 0.2)',
                    borderRadius: '12px',
                    padding: '24px',
                  }}
                >
                  <h3
                    style={{
                      color: '#9333ea',
                      marginBottom: '20px',
                      fontSize: '18px',
                      fontWeight: '600',
                    }}
                  >
                    Similarity Analysis Results
                  </h3>
                  <div
                    style={{
                      fontSize: '14px',
                      color: '#cccccc',
                      textAlign: 'center',
                      padding: '40px',
                    }}
                  >
                    Upload bytecode or enter contract address to see similarity matches
                  </div>
                </div>
              </ScrollReveal>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </>
  );
};

export default SmartContractScanner;
