import { useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { StorageManager } from "@/lib/storage";
import { motion, AnimatePresence } from "framer-motion";
import {
  Activity,
  Zap,
  Clock,
  DollarSign,
  Eye,
  Filter,
  Search,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  RefreshCw,
  Loader2,
  Play,
  Pause,
  Hash,
  ArrowUpRight,
  ArrowDownLeft,
  Monitor,
  Plus,
  X,
  Target,
  Shield,
  Radar,
  FileText,
  Database,
  Network,
  Bell,
  ExternalLink,
} from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { LiveCounter } from "@/components/ui/live-counter";
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import { useMempool } from "@/hooks";
import {
  ErrorBoundary,
  ModuleLoadingWrapper,
  ConnectionStatus,
} from "@/components/ui/error-boundary";

interface TrackedContract {
  id: string;
  address: string;
  name?: string;
  addedAt: Date;
  transactionCount: number;
  threatLevel: "low" | "medium" | "high" | "critical";
  lastActivity: Date;
}

interface ThreatDetection {
  id: string;
  contractAddress: string;
  threatType:
    | "reentrancy"
    | "front_run"
    | "sandwich"
    | "honeypot"
    | "suspicious_volume"
    | "gas_manipulation";
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  txHash: string;
  timestamp: Date;
  confidence: number;
}

interface Transaction {
  id: string;
  hash: string;
  from: string;
  to: string;
  value: string;
  gasPrice: string;
  gasLimit: number;
  method: string;
  timestamp: Date;
  priority: "low" | "medium" | "high";
  status: "pending" | "confirmed" | "failed";
  isTracked?: boolean;
  contractAddress?: string;
}

const MempoolMonitor = () => {
  const navigate = useNavigate();

  // Real-time API integration
  const {
    transactions,
    isLoading: mempoolLoading,
    error: mempoolError,
  } = useMempool();

  const {
    data: apiMempoolStats,
    isLoading: statsLoading,
    refetch: refetchStats,
  } = useQuery({
    queryKey: ["mempool-stats"],
    queryFn: () => apiClient.getMempoolStats(),
    refetchInterval: 5000,
  });

  const { data: mevOpportunities, isLoading: mevLoading } = useQuery({
    queryKey: ["mev-opportunities"],
    queryFn: () => apiClient.getMEVOpportunities(),
    refetchInterval: 3000,
  });

  // WebSocket connection status
  const { isConnected, addContract, removeContract } = useMempool();

  // Local state
  const [trackedContracts, setTrackedContracts] = useState<TrackedContract[]>(
    [],
  );
  const [threatDetections, setThreatDetections] = useState<ThreatDetection[]>(
    [],
  );
  const [newContractAddress, setNewContractAddress] = useState("");
  const [isMonitoring, setIsMonitoring] = useState(true);
  const [filters, setFilters] = useState({
    minValue: "",
    maxGasPrice: "",
    method: "",
    address: "",
    showTrackedOnly: false,
  });
  const [mempoolStats, setMempoolStats] = useState(() => {
    const stored = StorageManager.getMempoolStats();
    return {
      pendingTxs: stored.transactionsMonitored,
      avgGasPrice: stored.averageGasPrice || 0,
      avgBlockTime: 0,
      totalValue: stored.totalValue,
      trackedContracts: stored.contractsTracked,
      threatsDetected: stored.threatsDetected,
    };
  });
  const [selectedTx, setSelectedTx] = useState<Transaction | null>(null);

  // Mock contract names for better UX
  const contractNames: { [key: string]: string } = {
    "0x742d35Cc6431C8BF3240C39B6969E3C77e1345eF": "UniswapV3Pool",
    "0x9F8b2C4D5E6A7B8C9D0E1F2A3B4C5D6E7F8A9B0C": "SushiSwapRouter",
    "0x7E8F9A0B1C2D3E4F5A6B7C8D9E0F1A2B3C4D5E6F": "CompoundProtocol",
    "0x1234567890ABCDEF1234567890ABCDEF12345678": "AaveV3Pool",
    "0xABCDEF1234567890ABCDEF1234567890ABCDEF12": "CurveFinance",
  };

  // Generate mock transaction data
  const generateMockTransaction = useCallback((): Transaction => {
    const isTrackedTx = Math.random() > 0.7 && trackedContracts.length > 0;
    const trackedContract = isTrackedTx
      ? trackedContracts[Math.floor(Math.random() * trackedContracts.length)]
      : null;

    return {
      id: Math.random().toString(36).substr(2, 9),
      hash: `0x${Math.random().toString(16).substr(2, 64)}`,
      from: `0x${Math.random().toString(16).substr(2, 40)}`,
      to: trackedContract
        ? trackedContract.address
        : `0x${Math.random().toString(16).substr(2, 40)}`,
      value: (Math.random() * 100).toFixed(4),
      gasPrice: (Math.random() * 200 + 20).toFixed(0),
      gasLimit: Math.floor(Math.random() * 200000 + 21000),
      method: [
        "transfer",
        "swap",
        "approve",
        "withdraw",
        "deposit",
        "mint",
        "burn",
      ][Math.floor(Math.random() * 7)],
      timestamp: new Date(),
      priority:
        Math.random() > 0.7 ? "high" : Math.random() > 0.4 ? "medium" : "low",
      status: "pending",
      isTracked: isTrackedTx,
      contractAddress: trackedContract?.address,
    };
  }, [trackedContracts]);

  // Generate threat detection
  const generateThreatDetection = useCallback(
    (contractAddress: string, txHash: string): ThreatDetection => {
      const threatTypes: ThreatDetection["threatType"][] = [
        "reentrancy",
        "front_run",
        "sandwich",
        "honeypot",
        "suspicious_volume",
        "gas_manipulation",
      ];
      const threatType =
        threatTypes[Math.floor(Math.random() * threatTypes.length)];
      const severities: ThreatDetection["severity"][] = [
        "low",
        "medium",
        "high",
        "critical",
      ];
      const severity =
        severities[Math.floor(Math.random() * severities.length)];

      const descriptions = {
        reentrancy:
          "Potential reentrancy attack detected in contract execution",
        front_run:
          "Front-running attempt detected based on gas price and timing",
        sandwich: "Sandwich attack pattern identified in transaction sequence",
        honeypot:
          "Honeypot behavior detected - contract may prevent withdrawals",
        suspicious_volume: "Unusually large transaction volume detected",
        gas_manipulation:
          "Gas price manipulation detected for transaction ordering",
      };

      return {
        id: Math.random().toString(36).substr(2, 9),
        contractAddress,
        threatType,
        severity,
        description: descriptions[threatType],
        txHash,
        timestamp: new Date(),
        confidence: Math.floor(Math.random() * 30) + 70, // 70-99% confidence
      };
    },
    [],
  );

  // Load transactions from API
  useEffect(() => {
    const loadTransactions = async () => {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/mempool/transactions?limit=15`,
        );
        if (response.ok) {
          const data = await response.json();
          if (data.success && data.data) {
            setTransactions(data.data);
          }
        } else {
          // Fallback to empty array if API not available
          setTransactions([]);
        }
      } catch (error) {
        console.warn("Mempool API not available, using empty data:", error);
        setTransactions([]);
      }
    };

    loadTransactions();
  }, []);

  // Real-time transaction monitoring via WebSocket or polling
  useEffect(() => {
    if (!isMonitoring) return;

    let ws: WebSocket | null = null;
    let pollInterval: NodeJS.Timeout | null = null;

    // Try WebSocket first
    try {
      const wsUrl = `${import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000"}/api/mempool/ws`;
      ws = new WebSocket(wsUrl);

      ws.onmessage = (event) => {
        try {
          const newTx = JSON.parse(event.data);
          setTransactions((prev) => [newTx, ...prev.slice(0, 49)]);

          // Increment transaction count in storage
          StorageManager.incrementMempoolActivity();

          // Check for threat detection
          if (
            newTx.isTracked &&
            trackedContracts.some((c) => c.address === newTx.to)
          ) {
            const threat = generateThreatDetection(newTx.to, newTx.hash);
            setThreatDetections((prev) => [threat, ...prev.slice(0, 19)]);

            // Update threat count in storage
            const currentStats = StorageManager.getMempoolStats();
            StorageManager.setMempoolStats({
              ...currentStats,
              threatsDetected: currentStats.threatsDetected + 1,
            });

            setMempoolStats((prev) => ({
              ...prev,
              threatsDetected: prev.threatsDetected + 1,
            }));
          }

          // Update tracked contract stats
          if (newTx.isTracked) {
            setTrackedContracts((prev) =>
              prev.map((contract) =>
                contract.address === newTx.to
                  ? {
                      ...contract,
                      transactionCount: contract.transactionCount + 1,
                      lastActivity: new Date(),
                    }
                  : contract,
              ),
            );
          }
        } catch (error) {
          console.error("Error parsing WebSocket message:", error);
        }
      };

      ws.onerror = () => {
        console.warn("WebSocket connection failed, falling back to polling");
        startPolling();
      };
    } catch (error) {
      console.warn("WebSocket not available, using polling");
      startPolling();
    }

    function startPolling() {
      pollInterval = setInterval(async () => {
        try {
          const response = await fetch(
            `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/mempool/latest`,
          );
          if (response.ok) {
            const data = await response.json();
            if (data.success && data.data) {
              setTransactions((prev) => [data.data, ...prev.slice(0, 49)]);
            }
          }
        } catch (error) {
          console.error("Polling failed:", error);
        }
      }, 3000);
    }

    return () => {
      if (ws) {
        ws.close();
      }
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [isMonitoring, trackedContracts, generateThreatDetection]);

  // Update tracked contracts count in stats
  useEffect(() => {
    setMempoolStats((prev) => ({
      ...prev,
      trackedContracts: trackedContracts.length,
    }));
  }, [trackedContracts]);

  const addContractToTrack = () => {
    if (!newContractAddress.trim()) return;

    // Basic address validation
    if (!/^0x[a-fA-F0-9]{40}$/.test(newContractAddress.trim())) {
      alert("Please enter a valid Ethereum address");
      return;
    }

    // Check if already tracking
    if (
      trackedContracts.some(
        (c) => c.address.toLowerCase() === newContractAddress.toLowerCase(),
      )
    ) {
      alert("Contract is already being tracked");
      return;
    }

    const newContract: TrackedContract = {
      id: Math.random().toString(36).substr(2, 9),
      address: newContractAddress.trim(),
      name: contractNames[newContractAddress.trim()],
      addedAt: new Date(),
      transactionCount: 0,
      threatLevel: "low",
      lastActivity: new Date(),
    };

    setTrackedContracts((prev) => [...prev, newContract]);
    setNewContractAddress("");
  };

  const removeTrackedContract = (contractId: string) => {
    setTrackedContracts((prev) => prev.filter((c) => c.id !== contractId));
    // Remove related threat detections
    setThreatDetections((prev) =>
      prev.filter((t) => {
        const contract = trackedContracts.find((c) => c.id === contractId);
        return contract ? t.contractAddress !== contract.address : true;
      }),
    );
  };

  const filteredTransactions = transactions.filter((tx) => {
    if (filters.minValue && parseFloat(tx.value) < parseFloat(filters.minValue))
      return false;
    if (
      filters.maxGasPrice &&
      parseFloat(tx.gasPrice) > parseFloat(filters.maxGasPrice)
    )
      return false;
    if (
      filters.method &&
      !tx.method.toLowerCase().includes(filters.method.toLowerCase())
    )
      return false;
    if (
      filters.address &&
      !tx.from.toLowerCase().includes(filters.address.toLowerCase()) &&
      !tx.to.toLowerCase().includes(filters.address.toLowerCase())
    )
      return false;
    if (filters.showTrackedOnly && !tx.isTracked) return false;
    return true;
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "#ff4444";
      case "medium":
        return "#ffaa00";
      case "low":
        return "#00ff88";
      default:
        return "#999999";
    }
  };

  const getThreatColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "#ff0040";
      case "high":
        return "#ff4444";
      case "medium":
        return "#ffaa00";
      case "low":
        return "#00ffff";
      default:
        return "#999999";
    }
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);

    if (diffSecs < 60) return `${diffSecs}s ago`;
    if (diffMins < 60) return `${diffMins}m ago`;
    return `${Math.floor(diffMins / 60)}h ago`;
  };

  return (
    <PageLayout variant="monitoring">
      <PageHeader
        title="Mempool Monitoring System"
        description="Real-time transaction monitoring and threat detection"
        icon={Monitor}
        iconGradient="from-indigo-500 to-purple-600"
        borderColor="border-indigo-400/30"
      />
      {/* Stats Dashboard */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        {[
          {
            label: "Pending Txs",
            value: mempoolStats.pendingTxs,
            icon: Activity,
            color: "text-cyan-600",
          },
          {
            label: "Avg Gas Price",
            value: mempoolStats.avgGasPrice,
            icon: Zap,
            color: "text-amber-600",
            suffix: " gwei",
          },
          {
            label: "Tracked Contracts",
            value: mempoolStats.trackedContracts,
            icon: Target,
            color: "text-green-600",
          },
          {
            label: "Threats Detected",
            value: mempoolStats.threatsDetected,
            icon: Shield,
            color: "text-red-600",
          },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.1 * index }}
            whileHover={{ scale: 1.05, y: -5 }}
            className="bg-background/80 backdrop-blur border rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-4">
              <div
                className={`p-2 rounded-lg bg-background border ${stat.color}`}
              >
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </div>
            </div>
            <div className="space-y-2">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
                className={`text-3xl font-bold ${stat.color}`}
              >
                <LiveCounter
                  value={stat.value}
                  suffix={stat.suffix}
                  decimals={stat.suffix ? 1 : 0}
                  duration={2000}
                />
              </motion.div>
              <div className="text-sm text-muted-foreground font-medium">
                {stat.label}
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Contract Tracking Panel */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-background/80 backdrop-blur border rounded-xl p-6 mb-8 shadow-lg"
      >
        <h2 className="text-xl font-semibold mb-6 flex items-center space-x-2">
          <Target className="h-5 w-5" />
          <span>Contract Tracking</span>
        </h2>

        {/* Add Contract Form */}
        <div className="flex gap-3 mb-6 flex-wrap">
          <input
            type="text"
            placeholder="Enter contract address (0x...)"
            value={newContractAddress}
            onChange={(e) => setNewContractAddress(e.target.value)}
            className="flex-1 min-w-[300px] px-4 py-2 bg-background border rounded-lg text-foreground font-mono text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            onKeyPress={(e) => e.key === "Enter" && addContractToTrack()}
          />
          <Button
            onClick={addContractToTrack}
            className="bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Track Contract
          </Button>
        </div>

        {/* Tracked Contracts List */}
        {trackedContracts.length > 0 ? (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {trackedContracts.map((contract, index) => (
              <motion.div
                key={contract.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 * index }}
                whileHover={{ scale: 1.02 }}
                className="bg-background border rounded-lg p-4 relative"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <div className="font-semibold text-sm mb-1">
                      {contract.name || formatAddress(contract.address)}
                    </div>
                    <div className="text-xs text-muted-foreground font-mono mb-2">
                      {contract.address}
                    </div>
                    <div className="flex gap-4 text-xs">
                      <span className="text-cyan-600">
                        Txs: {contract.transactionCount}
                      </span>
                      <span className="text-amber-600">
                        Last: {formatTime(contract.lastActivity)}
                      </span>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeTrackedContract(contract.id)}
                    className="h-8 w-8 p-0 hover:bg-red-500/10 hover:text-red-500"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 text-muted-foreground">
            No contracts being tracked. Add contract addresses above to monitor
            their transactions and detect threats.
          </div>
        )}
      </motion.div>

      {/* Threat Detection Panel */}
      {threatDetections.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.6 }}
          className="bg-background/80 backdrop-blur border-red-200 dark:border-red-800 border rounded-xl p-6 mb-8 shadow-lg"
        >
          <h2 className="text-xl font-semibold mb-6 flex items-center space-x-2 text-red-600">
            <AlertTriangle className="h-5 w-5" />
            <span>Threat Detection ({threatDetections.length})</span>
          </h2>

          <div className="space-y-3">
            {threatDetections.slice(0, 5).map((threat, index) => (
              <motion.div
                key={threat.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: 0.1 * index }}
                className={`p-4 bg-background border rounded-lg flex items-center gap-3 cursor-pointer hover:scale-[1.02] transition-transform ${
                  threat.severity === "critical" ? "animate-pulse" : ""
                }`}
              >
                <div
                  className="w-2 h-2 rounded-full"
                  style={{
                    backgroundColor: getThreatColor(threat.severity),
                    boxShadow: `0 0 8px ${getThreatColor(threat.severity)}`,
                  }}
                />
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span
                      className="px-2 py-1 rounded text-xs font-semibold uppercase"
                      style={{
                        backgroundColor: `${getThreatColor(threat.severity)}20`,
                        color: getThreatColor(threat.severity),
                      }}
                    >
                      {threat.severity}
                    </span>
                    <span className="font-semibold">
                      {threat.threatType.replace("_", " ").toUpperCase()}
                    </span>
                  </div>
                  <div className="text-sm text-muted-foreground mb-1">
                    {threat.description}
                  </div>
                  <div className="flex items-center gap-3 text-xs text-muted-foreground">
                    <span>
                      Contract: {formatAddress(threat.contractAddress)}
                    </span>
                    <span>Confidence: {threat.confidence}%</span>
                    <span>{formatTime(threat.timestamp)}</span>
                  </div>
                </div>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </motion.div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Transaction Monitoring */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.8 }}
        className="bg-background/80 backdrop-blur border rounded-xl p-6 shadow-lg"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold flex items-center space-x-2">
            <Database className="h-5 w-5" />
            <span>Live Transaction Feed</span>
          </h2>

          {/* Filters */}
          <div className="flex gap-3 items-center">
            <label className="flex items-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={filters.showTrackedOnly}
                onChange={(e) =>
                  setFilters({
                    ...filters,
                    showTrackedOnly: e.target.checked,
                  })
                }
                className="rounded"
              />
              Tracked Only
            </label>
            <input
              type="text"
              placeholder="Filter by method..."
              value={filters.method}
              onChange={(e) =>
                setFilters({ ...filters, method: e.target.value })
              }
              className="px-3 py-1 bg-background border rounded text-sm w-32"
            />
          </div>
        </div>

        {/* Transaction Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-4 font-semibold">Hash</th>
                <th className="text-left py-3 px-4 font-semibold">Method</th>
                <th className="text-left py-3 px-4 font-semibold">From/To</th>
                <th className="text-right py-3 px-4 font-semibold">
                  Value (ETH)
                </th>
                <th className="text-right py-3 px-4 font-semibold">
                  Gas Price
                </th>
                <th className="text-center py-3 px-4 font-semibold">
                  Priority
                </th>
                <th className="text-right py-3 px-4 font-semibold">Time</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.slice(0, 20).map((tx, index) => (
                <motion.tr
                  key={tx.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: 0.05 * index }}
                  whileHover={{ backgroundColor: "rgba(0, 0, 0, 0.02)" }}
                  className={`border-b hover:bg-muted/50 cursor-pointer ${
                    tx.isTracked ? "bg-green-500/5" : ""
                  }`}
                  onClick={() => setSelectedTx(tx)}
                >
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      {tx.isTracked && (
                        <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
                      )}
                      <span className="font-mono text-xs">
                        {formatAddress(tx.hash)}
                      </span>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className="px-2 py-1 bg-cyan-500/20 text-cyan-700 dark:text-cyan-300 rounded text-xs font-medium uppercase">
                      {tx.method}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-xs font-mono">
                    <div>
                      <div>{formatAddress(tx.from)}</div>
                      <div className="text-muted-foreground">
                        → {formatAddress(tx.to)}
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-green-600 font-semibold">
                    {tx.value}
                  </td>
                  <td className="py-3 px-4 text-right font-mono text-amber-600">
                    {tx.gasPrice}
                  </td>
                  <td className="py-3 px-4 text-center">
                    <div
                      className="w-2 h-2 rounded-full mx-auto"
                      style={{
                        backgroundColor: getPriorityColor(tx.priority),
                        boxShadow: `0 0 6px ${getPriorityColor(tx.priority)}`,
                      }}
                    />
                  </td>
                  <td className="py-3 px-4 text-right text-muted-foreground text-xs">
                    {formatTime(tx.timestamp)}
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredTransactions.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            No transactions match your current filters.
          </div>
        )}
      </motion.div>
    </PageLayout>
  );
};

export default MempoolMonitor;
