import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useLocation } from "react-router-dom";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import { LiveCounter } from "@/components/ui/live-counter";
import { PluginConfiguration } from "@/components/PluginConfiguration";
import { BytecodeAnalysis } from "@/components/BytecodeAnalysis";
import WalletScanner from "@/components/WalletScanner";
import {
  useVulnerabilityScanner,
  useScannerResults,
  useHoneypotResults,
  useHoneypotDetector,
} from "@/hooks";
import {
  ErrorBoundary,
  ModuleLoadingWrapper,
  ConnectionStatus,
} from "@/components/ui/error-boundary";
import {
  Search,
  Shield,
  Target,
  Zap,
  Play,
  Pause,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Activity,
  Package,
  Binary,
  FileCode,
  Upload,
  Hash,
  Eye,
  Download,
  BarChart3,
  TrendingUp,
  RefreshCw,
  X,
  Plus,
  Settings,
  Brain,
  Cpu,
  Database,
  Filter,
  Maximize2,
  FileJson,
  Bug,
  Crosshair,
  Radar,
  Network,
  Timer,
} from "lucide-react";

interface ThreatEvent {
  id: string;
  attackerAddress: string;
  contractTriggered: string;
  gasUsed: number;
  timestamp: Date;
  threatScore: number;
  txHash: string;
  calldataSize: number;
  value: number;
  status: "detected" | "analyzing" | "confirmed" | "neutralized";
  attackType: string;
  severity: "low" | "medium" | "high" | "critical";
}

const Scanner = () => {
  const location = useLocation();

  // Determine initial tab based on URL path
  const getInitialTab = ():
    | "scanner"
    | "plugins"
    | "honeypot"
    | "bytecode"
    | "wallet" => {
    const path = location.pathname;
    if (path.includes("honeypot")) return "honeypot";
    if (path.includes("wallet-scanner")) return "wallet";
    if (path.includes("bytecode")) return "bytecode";
    if (path.includes("plugins")) return "plugins";
    return "scanner";
  };

  // Real-time API integration
  const {
    startScan: apiStartScan,
    uploadAndScan,
    scanResult,
    progress: scanProgressPercent,
    isScanning,
    error: scanError,
  } = useVulnerabilityScanner();

  const {
    data: recentScans,
    isLoading: scansLoading,
    error: scansError,
    refetch: refetchScans,
  } = useScannerResults(10);

  const { data: honeypotDetections, isLoading: honeypotLoading } =
    useHoneypotResults();

  const {
    startDetection,
    isDetecting,
    progress: honeypotProgress,
    result: honeypotResult,
    error: honeypotError,
  } = useHoneypotDetector();

  // Local state
  const [contractAddress, setContractAddress] = useState("");
  const [scanMode, setScanMode] = useState<"address" | "files">("address");
  const [activeTab, setActiveTab] = useState<
    "scanner" | "plugins" | "honeypot" | "bytecode" | "wallet"
  >(getInitialTab());
  const [showResults, setShowResults] = useState(false);

  // Honeypot detection states
  const [threatEvents, setThreatEvents] = useState<ThreatEvent[]>([]);
  const [isLiveMonitoring, setIsLiveMonitoring] = useState(true);
  const [selectedThreatEvent, setSelectedThreatEvent] =
    useState<ThreatEvent | null>(null);
  const [threatFilters, setThreatFilters] = useState({
    contract: "",
    gasThreshold: 100000,
    minScore: 0,
    severity: "all",
  });
  const [honeypotStats, setHoneypotStats] = useState({
    totalDetections: 1247,
    activeThreats: 23,
    successRate: 97.3,
    avgResponseTime: 2.1,
    contractsMonitored: 156,
    dailyBlocks: 28947,
  });

  // Handle scan initiation
  const handleScanClick = async (type: "quick" | "deep" = "quick") => {
    if (!contractAddress.trim()) return;

    try {
      const result = await apiStartScan(contractAddress, {
        scanType: type,
        plugins: type === "deep" ? undefined : undefined,
      });

      if (result) {
        setShowResults(true);
      }
    } catch (error) {
      console.error("Scan failed:", error);
    }
  };

  const stopScan = () => {
    setShowResults(false);
  };

  // Handle file upload
  const handleFileUpload = async (
    event: React.ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      const result = await uploadAndScan(file);
      if (result) {
        setShowResults(true);
      }
    } catch (error) {
      console.error("File upload failed:", error);
    }
  };

  // Utility functions
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "border-red-500/50 bg-red-500/10 text-red-400";
      case "high":
        return "border-red-400/50 bg-red-500/10 text-red-400";
      case "medium":
        return "border-amber-400/50 bg-amber-500/10 text-amber-400";
      case "low":
        return "border-green-400/50 bg-green-500/10 text-green-400";
      default:
        return "border-gray-400/50 bg-gray-500/10 text-gray-400";
    }
  };

  const getThreatSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "#dc2626";
      case "high":
        return "#ea580c";
      case "medium":
        return "#d97706";
      case "low":
        return "#65a30d";
      default:
        return "#6b7280";
    }
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  // Calculate scan progress
  const scanProgress = scanProgressPercent ||
    (scanResult?.status === "completed"
      ? 100
      : scanResult?.status === "scanning"
        ? 75
        : scanResult?.status === "pending"
          ? 25
          : 0);

  return (
    <ErrorBoundary>
      <PageLayout>
        <PageHeader
          title="Vulnerability Scanner"
          description="AI-powered smart contract security analysis with real-time threat detection"
          icon={Search}
          action={
            <div className="flex items-center space-x-2">
              <ConnectionStatus
                isConnected={!scanError}
                serviceName="Scanner API"
              />
            </div>
          }
        />

        <div className="space-y-6">
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card className="glass border-cyan-400/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-400/30">
                    <Search className="h-4 w-4 text-cyan-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Total Scans</p>
                    <p className="text-2xl font-bold text-white">
                      <LiveCounter value={recentScans?.length || 0} />
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass border-red-400/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="p-2 rounded-lg bg-red-500/20 border border-red-400/30">
                    <AlertTriangle className="h-4 w-4 text-red-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Vulnerabilities</p>
                    <p className="text-2xl font-bold text-white">
                      <LiveCounter
                        value={scanResult?.vulnerabilities?.length || 0}
                      />
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass border-green-400/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="p-2 rounded-lg bg-green-500/20 border border-green-400/30">
                    <Shield className="h-4 w-4 text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Security Score</p>
                    <p className="text-2xl font-bold text-white">
                      {scanResult?.score || "--"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="glass border-amber-400/20">
              <CardContent className="p-4">
                <div className="flex items-center space-x-2">
                  <div className="p-2 rounded-lg bg-amber-500/20 border border-amber-400/30">
                    <Activity className="h-4 w-4 text-amber-400" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Status</p>
                    <p className="text-lg font-bold text-white">
                      {isScanning ? "Scanning" : "Ready"}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Scanner Interface */}
          <Tabs
            value={activeTab}
            onValueChange={(val)=> setActiveTab(val as any)}
            className="space-y-6"
          >
            <TabsList className="grid w-full grid-cols-5 glass border border-cyan-400/20">
              <TabsTrigger
                value="scanner"
                className="flex items-center space-x-2"
              >
                <Search className="h-4 w-4" />
                <span>Contract Scanner</span>
              </TabsTrigger>
              <TabsTrigger
                value="wallet"
                className="flex items-center space-x-2"
              >
                <Shield className="h-4 w-4" />
                <span>Wallet Scanner</span>
              </TabsTrigger>
              <TabsTrigger
                value="honeypot"
                className="flex items-center space-x-2"
              >
                <Target className="h-4 w-4" />
                <span>Honeypot Detector</span>
              </TabsTrigger>
              <TabsTrigger
                value="bytecode"
                className="flex items-center space-x-2"
              >
                <Binary className="h-4 w-4" />
                <span>Bytecode Analysis</span>
              </TabsTrigger>
              <TabsTrigger
                value="plugins"
                className="flex items-center space-x-2"
              >
                <Package className="h-4 w-4" />
                <span>Plugins</span>
              </TabsTrigger>
            </TabsList>

            {/* Scanner Tab */}
            <TabsContent value="scanner" className="space-y-6">
              <ModuleLoadingWrapper
                loading={scansLoading}
                error={scansError?.message}
                moduleName="Scanner"
                retryAction={refetchScans}
              >
                <Card className="glass border-cyan-400/20">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Search className="h-5 w-5 text-cyan-400" />
                      <span>Smart Contract Scanner</span>
                    </CardTitle>
                    <CardDescription>
                      Enter a contract address or upload Solidity files for
                      comprehensive security analysis
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Scan Mode Toggle */}
                    <div className="flex items-center space-x-4">
                      <Label>Scan Mode:</Label>
                      <div className="flex items-center space-x-2">
                        <Button
                          variant={
                            scanMode === "address" ? "default" : "outline"
                          }
                          size="sm"
                          onClick={() => setScanMode("address")}
                        >
                          Contract Address
                        </Button>
                        <Button
                          variant={scanMode === "files" ? "default" : "outline"}
                          size="sm"
                          onClick={() => setScanMode("files")}
                        >
                          Upload Files
                        </Button>
                      </div>
                    </div>

                    {/* Input Section */}
                    {scanMode === "address" ? (
                      <div className="space-y-4">
                        <div>
                          <Label htmlFor="contract-address">
                            Contract Address
                          </Label>
                          <input
                            id="contract-address"
                            type="text"
                            placeholder="0x..."
                            value={contractAddress}
                            onChange={(e) => setContractAddress(e.target.value)}
                            className="w-full px-4 py-3 mt-2 bg-black/50 border border-cyan-400/30 rounded-lg focus:border-cyan-400 focus:outline-none text-white placeholder-gray-500"
                          />
                        </div>

                        {/* Scan Buttons */}
                        <div className="flex space-x-3">
                          {!isScanning ? (
                            <>
                              <Button
                                onClick={() => handleScanClick("quick")}
                                className="flex-1 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 glow-cyan"
                                disabled={!contractAddress.trim()}
                              >
                                <Zap className="h-4 w-4 mr-2" />
                                Quick Scan
                              </Button>
                              <Button
                                onClick={() => handleScanClick("deep")}
                                variant="outline"
                                className="flex-1 border-cyan-400/50 text-cyan-400 hover:bg-cyan-500/10"
                                disabled={!contractAddress.trim()}
                              >
                                <Target className="h-4 w-4 mr-2" />
                                Deep Scan
                              </Button>
                            </>
                          ) : (
                            <Button
                              onClick={stopScan}
                              variant="outline"
                              className="flex-1 border-red-400/50 text-red-400 hover:bg-red-500/10"
                            >
                              <Pause className="h-4 w-4 mr-2" />
                              Stop Scan
                            </Button>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        <div>
                          <Label>Upload Solidity Files</Label>
                          <div className="mt-2 border-2 border-dashed border-cyan-400/30 rounded-lg p-8 text-center hover:border-cyan-400/50 transition-colors">
                            <Upload className="h-8 w-8 text-cyan-400 mx-auto mb-4" />
                            <p className="text-white mb-2">
                              Drag & drop your .sol files here
                            </p>
                            <p className="text-gray-400 text-sm mb-4">
                              or click to browse
                            </p>
                            <input
                              type="file"
                              accept=".sol,.json"
                              multiple
                              onChange={handleFileUpload}
                              className="hidden"
                              id="file-upload"
                            />
                            <Button
                              asChild
                              variant="outline"
                              className="border-cyan-400/50 text-cyan-400"
                            >
                              <label
                                htmlFor="file-upload"
                                className="cursor-pointer"
                              >
                                Browse Files
                              </label>
                            </Button>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Progress Section */}
                    {isScanning && (
                      <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="space-y-4"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-gray-400">
                            Scanning Progress
                          </span>
                          <span className="text-sm text-cyan-400">
                            {scanProgress}%
                          </span>
                        </div>
                        <Progress value={scanProgress} className="h-2" />
                        <div className="flex items-center space-x-2">
                          <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                          <span className="text-sm text-gray-400">
                            Analyzing contract: {contractAddress}
                          </span>
                        </div>
                      </motion.div>
                    )}

                    {/* Error Display */}
                    {scanError && (
                      <div className="p-4 bg-red-500/10 border border-red-400/30 rounded-lg">
                        <div className="flex items-center space-x-2">
                          <AlertTriangle className="h-4 w-4 text-red-400" />
                          <span className="text-red-400 text-sm">
                            {scanError}
                          </span>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Results Section */}
                {showResults && scanResult && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="space-y-6"
                  >
                    <Card className="glass border-cyan-400/20">
                      <CardHeader>
                        <CardTitle className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <CheckCircle2 className="h-5 w-5 text-green-400" />
                            <span>Scan Results</span>
                          </div>
                          <Badge
                            variant="outline"
                            className="border-cyan-400/50 text-cyan-400"
                          >
                            Score: {scanResult.score}/100
                          </Badge>
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        {scanResult.vulnerabilities &&
                        scanResult.vulnerabilities.length > 0 ? (
                          <div className="space-y-4">
                            {scanResult.vulnerabilities.map((vuln, index) => (
                              <motion.div
                                key={vuln.id}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.1 }}
                                className={`p-4 rounded-lg border ${getSeverityColor(vuln.severity)}`}
                              >
                                <div className="flex items-start justify-between">
                                  <div className="space-y-2">
                                    <div className="flex items-center space-x-2">
                                      <Badge
                                        variant="outline"
                                        className={getSeverityColor(
                                          vuln.severity,
                                        )}
                                      >
                                        {vuln.severity.toUpperCase()}
                                      </Badge>
                                      <h4 className="font-medium text-white">
                                        {vuln.type}
                                      </h4>
                                    </div>
                                    <p className="text-gray-300 text-sm">
                                      {vuln.description}
                                    </p>
                                    {vuln.location && (
                                      <p className="text-xs text-gray-500">
                                        Location: {vuln.location}
                                      </p>
                                    )}
                                    {vuln.recommendation && (
                                      <p className="text-xs text-cyan-400">
                                        Recommendation: {vuln.recommendation}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              </motion.div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-center py-8">
                            <CheckCircle2 className="h-12 w-12 text-green-400 mx-auto mb-4" />
                            <h3 className="text-lg font-medium text-white mb-2">
                              No vulnerabilities found
                            </h3>
                            <p className="text-gray-400">
                              The contract appears to be secure
                            </p>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </motion.div>
                )}
              </ModuleLoadingWrapper>
            </TabsContent>

            {/* Wallet Scanner Tab */}
            <TabsContent value="wallet" className="space-y-6">
              <WalletScanner />
            </TabsContent>

            {/* Honeypot Tab */}
            <TabsContent value="honeypot" className="space-y-6">
              <ModuleLoadingWrapper
                loading={honeypotLoading}
                error={honeypotError?.message}
                moduleName="Honeypot Detector"
              >
                <Card className="glass border-red-400/20">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <Shield className="h-5 w-5 text-red-400" />
                      <span>Honeypot Detection</span>
                    </CardTitle>
                    <CardDescription>
                      Real-time detection of honeypot contracts and malicious
                      patterns
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="space-y-2">
                        <Label>Contract Address:</Label>
                        <div className="flex items-center space-x-2">
                          <input
                            type="text"
                            placeholder="Enter contract address to analyze..."
                            className="flex-1 px-4 py-2 bg-black/50 border border-red-400/30 rounded-lg focus:border-red-400 focus:outline-none text-white placeholder-gray-500"
                            value={contractAddress}
                            onChange={(e) => setContractAddress(e.target.value)}
                            onKeyPress={(e) => {
                              if (e.key === "Enter" && contractAddress.trim()) {
                                startDetection(contractAddress.trim());
                              }
                            }}
                          />
                          <Button
                            onClick={() => {
                              if (contractAddress.trim()) {
                                startDetection(contractAddress.trim());
                              }
                            }}
                            disabled={!contractAddress.trim() || isDetecting}
                            className="bg-red-600 hover:bg-red-700 text-white px-6"
                          >
                            {isDetecting ? (
                              <>
                                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                                Scanning...
                              </>
                            ) : (
                              <>
                                <Search className="w-4 h-4 mr-2" />
                                Scan
                              </>
                            )}
                          </Button>
                        </div>
                      </div>

                      {honeypotResult && (
                        <motion.div
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="p-4 bg-red-500/10 border border-red-400/30 rounded-lg"
                        >
                          <h4 className="font-medium text-white mb-2">
                            Analysis Result
                          </h4>
                          <pre className="text-sm text-gray-300 whitespace-pre-wrap">
                            {JSON.stringify(honeypotResult, null, 2)}
                          </pre>
                        </motion.div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </ModuleLoadingWrapper>
            </TabsContent>

            {/* Bytecode Tab */}
            <TabsContent value="bytecode" className="space-y-6">
              <BytecodeAnalysis />
            </TabsContent>

            {/* Plugins Tab */}
            <TabsContent value="plugins" className="space-y-6">
              <PluginConfiguration />
            </TabsContent>
          </Tabs>
        </div>
      </PageLayout>
    </ErrorBoundary>
  );
};

export default Scanner;
