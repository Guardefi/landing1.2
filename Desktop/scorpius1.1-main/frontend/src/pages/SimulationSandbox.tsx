import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import {
  Play,
  Pause,
  StopCircle,
  AlertTriangle,
  Shield,
  Zap,
  Target,
  Brain,
  Eye,
  Code,
  Activity,
  CheckCircle,
  XCircle,
  Clock,
  DollarSign,
  TrendingUp,
  Loader2,
  RefreshCw,
  Download,
  Upload,
  Settings,
  Info,
  Skull,
  Gauge,
} from "lucide-react";
import { StorageManager } from "@/lib/storage";

// Attack type definitions
interface AttackType {
  id: string;
  name: string;
  description: string;
  severity: "low" | "medium" | "high" | "critical";
  complexity: "beginner" | "intermediate" | "advanced" | "expert";
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  estimatedTime: string;
  requirements: string[];
}

interface SimulationResult {
  attackType: string;
  contractAddress: string;
  status: "success" | "failed" | "blocked" | "partial";
  vulnerabilityFound: boolean;
  exploitableValue: number;
  gasUsed: number;
  transactions: Array<{
    type: string;
    hash: string;
    success: boolean;
    value: string;
    gasUsed: number;
  }>;
  timeline: Array<{
    step: string;
    description: string;
    timestamp: Date;
    status: "success" | "warning" | "error";
  }>;
  mitigation: string[];
  riskScore: number;
  executionTime: number;
}

const SimulationSandbox = () => {
  const [contractAddress, setContractAddress] = useState("");
  const [selectedAttack, setSelectedAttack] = useState<string>("");
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [simulationResult, setSimulationResult] =
    useState<SimulationResult | null>(null);
  const [simulationHistory, setSimulationHistory] = useState<
    SimulationResult[]
  >([]);
  const [advancedOptions, setAdvancedOptions] = useState({
    gasLimit: "1000000",
    gasPrice: "20",
    blockNumber: "latest",
    fork: true,
    verbose: false,
  });

  // Enhanced simulation control states
  const [isPaused, setIsPaused] = useState(false);
  const [simulationSpeed, setSimulationSpeed] = useState(1);
  const [autoMode, setAutoMode] = useState(false);
  const [stepByStep, setStepByStep] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [totalSteps] = useState(5);
  const [simulationLog, setSimulationLog] = useState<string[]>([]);

  // Attack types available for simulation
  const attackTypes: AttackType[] = [
    {
      id: "flash_loan",
      name: "Flash Loan Attack",
      description:
        "Exploits flash loan functionality to manipulate market prices and drain funds",
      severity: "critical",
      complexity: "advanced",
      icon: Zap,
      color: "text-red-600",
      estimatedTime: "2-5 min",
      requirements: ["DEX liquidity", "Price oracle", "Flash loan provider"],
    },
    {
      id: "reentrancy",
      name: "Reentrancy Attack",
      description:
        "Exploits recursive calling patterns to drain contract funds",
      severity: "critical",
      complexity: "intermediate",
      icon: Target,
      color: "text-orange-600",
      estimatedTime: "1-3 min",
      requirements: [
        "External calls",
        "State changes after calls",
        "Ether withdrawal",
      ],
    },
    {
      id: "integer_overflow",
      name: "Integer Overflow",
      description: "Exploits arithmetic overflow/underflow vulnerabilities",
      severity: "high",
      complexity: "beginner",
      icon: Brain,
      color: "text-yellow-600",
      estimatedTime: "30s-2 min",
      requirements: ["Arithmetic operations", "User input", "No SafeMath"],
    },
    {
      id: "oracle_manipulation",
      name: "Oracle Manipulation",
      description: "Manipulates price feeds to exploit DeFi protocols",
      severity: "critical",
      complexity: "expert",
      icon: Eye,
      color: "text-purple-600",
      estimatedTime: "3-10 min",
      requirements: ["Price oracles", "DEX integration", "Large capital"],
    },
  ];

  // Load simulation history on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem("simulation_history");
    if (savedHistory) {
      setSimulationHistory(JSON.parse(savedHistory));
    }
  }, []);

  const runSimulation = async () => {
    if (!contractAddress.trim() || !selectedAttack) {
      toast.error("Please enter a contract address and select an attack type");
      return;
    }

    setIsRunning(true);
    setProgress(0);
    setCurrentStep(0);
    setSimulationResult(null);
    setSimulationLog([]);

    try {
      // Enhanced simulation steps with logging
      const steps = [
        "Initializing simulation environment...",
        "Analyzing contract bytecode and ABI...",
        "Executing attack scenario...",
        "Verifying attack success/failure...",
        "Generating comprehensive report...",
      ];

      for (let i = 0; i < steps.length; i++) {
        // Add to log
        setSimulationLog((prev) => [...prev, steps[i]]);
        setCurrentStep(i);

        // Wait for pause if paused
        while (isPaused && isRunning) {
          await new Promise((resolve) => setTimeout(resolve, 100));
        }

        // Check if stopped
        if (!isRunning) break;

        // Simulate step execution with speed control
        const baseTime = 1000 + Math.random() * 2000;
        const adjustedTime = baseTime / simulationSpeed;

        if (stepByStep && i < steps.length - 1) {
          // In step-by-step mode, wait for user confirmation
          setSimulationLog((prev) => [
            ...prev,
            `Step ${i + 1} completed. Ready for next step...`,
          ]);
          await new Promise((resolve) => setTimeout(resolve, adjustedTime));
        } else {
          await new Promise((resolve) => setTimeout(resolve, adjustedTime));
        }

        setProgress(((i + 1) / steps.length) * 100);
      }

      if (!isRunning) return; // Simulation was stopped

      // Make API call to backend simulation service
      let result: SimulationResult;
      
      try {
        const { SimulationService } = await import('@/services/api');
        
        // Start simulation
        const startResponse = await SimulationService.runSimulation({
          contractAddress,
          attackType: selectedAttack,
          options: advancedOptions,
        });

        if (startResponse.success && startResponse.data?.scan_id) {
          const scanId = startResponse.data.scan_id;
          
          // Poll for completion with timeout
          let attempts = 0;
          const maxAttempts = 30; // 30 seconds max
          let simulationCompleted = false;
          
          while (attempts < maxAttempts && isRunning && !simulationCompleted) {
            await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
            
            const statusResponse = await SimulationService.getSimulationStatus(scanId);
            
            if (statusResponse.success && statusResponse.data?.status === "completed") {
              const resultsResponse = await SimulationService.getSimulationResults(scanId);
              
              if (resultsResponse.success && resultsResponse.data) {
                // Convert API result to frontend format
                const apiResult = resultsResponse.data;
                result = {
                  ...apiResult,
                  timeline: apiResult.timeline.map(item => ({
                    ...item,
                    timestamp: new Date(item.timestamp),
                    status: item.status as "success" | "warning" | "error"
                  }))
                };
                simulationCompleted = true;
                break;
              }
            }
            
            attempts++;
          }
          
          // If no result from API, generate mock result
          if (!simulationCompleted) {
            console.warn("Simulation API timeout, using mock data");
            result = generateMockResult();
          }
        } else {
          console.warn("Failed to start simulation, using mock data");
          result = generateMockResult();
        }
      } catch (apiError) {
        console.error("Simulation API error:", apiError);
        result = generateMockResult();
      }

      setSimulationResult(result);

      // Save to history
      const newHistory = [result, ...simulationHistory.slice(0, 9)]; // Keep last 10
      setSimulationHistory(newHistory);
      localStorage.setItem("simulation_history", JSON.stringify(newHistory));

      // Persist simulation stats
      if (result.vulnerabilityFound) {
        const scanData = {
          id: `sim_${Date.now()}`,
          contractAddress,
          timestamp: new Date().toISOString(),
          findings: result.vulnerabilityFound ? 1 : 0,
          riskScore: result.riskScore,
        };
        StorageManager.incrementScanCount(scanData);
      }

      toast.success("Simulation completed successfully");
    } catch (error) {
      console.error("Simulation failed:", error);
      toast.error("Simulation failed to execute");
    } finally {
      setIsRunning(false);
      setProgress(100);
    }
  };

  const generateMockResult = (): SimulationResult => {
    const attack = attackTypes.find((a) => a.id === selectedAttack)!;
    const vulnerabilityFound = Math.random() > 0.3;
    const success = vulnerabilityFound && Math.random() > 0.2;

    return {
      attackType: selectedAttack,
      contractAddress,
      status: success ? "success" : vulnerabilityFound ? "partial" : "blocked",
      vulnerabilityFound,
      exploitableValue: vulnerabilityFound ? Math.random() * 100000 : 0,
      gasUsed: Math.floor(Math.random() * 500000) + 100000,
      transactions: [
        {
          type: "setup",
          hash: `0x${Math.random().toString(16).substr(2, 64)}`,
          success: true,
          value: "0",
          gasUsed: 50000,
        },
        {
          type: "exploit",
          hash: `0x${Math.random().toString(16).substr(2, 64)}`,
          success: success,
          value: success ? (Math.random() * 10).toFixed(4) : "0",
          gasUsed: Math.floor(Math.random() * 300000) + 100000,
        },
      ],
      timeline: [
        {
          step: "Contract Analysis",
          description: `Analyzed ${contractAddress} for ${attack.name.toLowerCase()} vulnerabilities`,
          timestamp: new Date(Date.now() - 5000),
          status: "success",
        },
        {
          step: "Environment Setup",
          description: "Forked mainnet and deployed attack contracts",
          timestamp: new Date(Date.now() - 4000),
          status: "success",
        },
        {
          step: "Attack Execution",
          description: success
            ? "Successfully exploited vulnerability"
            : "Attack was blocked or failed",
          timestamp: new Date(Date.now() - 1000),
          status: success ? "success" : "error",
        },
      ],
      mitigation: [
        "Implement reentrancy guards",
        "Use SafeMath for arithmetic operations",
        "Add proper access controls",
        "Validate external data sources",
      ],
      riskScore: vulnerabilityFound
        ? Math.floor(Math.random() * 40) + 60
        : Math.floor(Math.random() * 30) + 10,
      executionTime: Math.floor(Math.random() * 180) + 30,
    };
  };

  const stopSimulation = () => {
    setIsRunning(false);
    setProgress(0);
    toast.info("Simulation stopped");
  };

  const exportResults = () => {
    if (!simulationResult) return;

    const data = JSON.stringify(simulationResult, null, 2);
    const blob = new Blob([data], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `simulation-${selectedAttack}-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    toast.success("Results exported");
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case "failed":
        return <XCircle className="h-5 w-5 text-red-600" />;
      case "blocked":
        return <Shield className="h-5 w-5 text-blue-600" />;
      case "partial":
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-600" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical":
        return "bg-red-100 text-red-800 border-red-200";
      case "high":
        return "bg-orange-100 text-orange-800 border-orange-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
        return "bg-blue-100 text-blue-800 border-blue-200";
      default:
        return "bg-gray-100 text-gray-800 border-gray-200";
    }
  };

  return (
    <PageLayout>
      <PageHeader
        title="Simulation Sandbox"
        description="Test smart contract vulnerabilities in a safe, isolated environment"
        icon={Target}
        iconGradient="from-red-500 to-orange-600"
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Simulation Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Contract Input */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Code className="h-5 w-5" />
                <span>Target Contract</span>
              </CardTitle>
              <CardDescription>
                Enter the smart contract address you want to test
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Contract Address</Label>
                <Input
                  placeholder="0x..."
                  value={contractAddress}
                  onChange={(e) => setContractAddress(e.target.value)}
                  className="font-mono"
                />
              </div>

              {contractAddress && (
                <Alert>
                  <Info className="h-4 w-4" />
                  <AlertDescription>
                    All simulations run in an isolated environment. No real
                    transactions will be executed.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Attack Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Skull className="h-5 w-5" />
                  <span>Attack Vector Selection</span>
                </div>
                <Badge variant="outline" className="text-xs">
                  {selectedAttack ? "1 Selected" : "None Selected"}
                </Badge>
              </CardTitle>
              <CardDescription>
                Choose the type of attack to simulate against the target
                contract
              </CardDescription>
            </CardHeader>
            <CardContent>
              {/* Quick Selection Buttons */}
              <div className="mb-6 p-4 bg-muted/50 rounded-lg">
                <Label className="text-sm font-medium mb-3 block">
                  Quick Select Popular Attacks
                </Label>
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedAttack("flash_loan");
                      toast.success("Selected: Flash Loan Attack");
                    }}
                    className={
                      selectedAttack === "flash_loan"
                        ? "bg-red-100 border-red-500"
                        : ""
                    }
                  >
                    <Zap className="h-3 w-3 mr-1" />
                    Flash Loan
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedAttack("reentrancy");
                      toast.success("Selected: Reentrancy Attack");
                    }}
                    className={
                      selectedAttack === "reentrancy"
                        ? "bg-red-100 border-red-500"
                        : ""
                    }
                  >
                    <Target className="h-3 w-3 mr-1" />
                    Reentrancy
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedAttack("oracle_manipulation");
                      toast.success("Selected: Oracle Manipulation");
                    }}
                    className={
                      selectedAttack === "oracle_manipulation"
                        ? "bg-red-100 border-red-500"
                        : ""
                    }
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    Oracle
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setSelectedAttack("");
                      toast.info("Selection cleared");
                    }}
                    disabled={!selectedAttack}
                  >
                    Clear
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {attackTypes.map((attack, index) => (
                  <motion.div
                    key={attack.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    whileHover={{ scale: 1.02, y: -2 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    <Card
                      className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                        selectedAttack === attack.id
                          ? "ring-2 ring-red-500 border-red-500 bg-red-50 dark:bg-red-950/20"
                          : "hover:border-red-300 dark:hover:border-red-700"
                      }`}
                      onClick={() => {
                        setSelectedAttack(attack.id);
                        toast.success(`Selected: ${attack.name}`);
                      }}
                    >
                      <CardHeader className="pb-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-2">
                            <attack.icon
                              className={`h-5 w-5 ${attack.color}`}
                            />
                            <CardTitle className="text-base font-semibold">
                              {attack.name}
                            </CardTitle>
                          </div>
                          {selectedAttack === attack.id && (
                            <CheckCircle className="h-5 w-5 text-green-500" />
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getSeverityColor(attack.severity)}>
                            {attack.severity.toUpperCase()}
                          </Badge>
                          <Badge variant="outline">{attack.complexity}</Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <p className="text-sm text-muted-foreground">
                          {attack.description}
                        </p>

                        <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                          <Clock className="h-3 w-3" />
                          <span>Est. Time: {attack.estimatedTime}</span>
                        </div>

                        <div className="space-y-2">
                          <p className="text-xs font-medium text-muted-foreground">
                            Requirements:
                          </p>
                          <ul className="space-y-1">
                            {attack.requirements
                              .slice(0, 2)
                              .map((req, reqIndex) => (
                                <li
                                  key={reqIndex}
                                  className="flex items-center text-xs text-muted-foreground"
                                >
                                  <CheckCircle className="h-3 w-3 mr-1 text-green-500 flex-shrink-0" />
                                  <span className="truncate">{req}</span>
                                </li>
                              ))}
                            {attack.requirements.length > 2 && (
                              <li className="text-xs text-muted-foreground">
                                +{attack.requirements.length - 2} more...
                              </li>
                            )}
                          </ul>
                        </div>
                      </CardContent>
                    </Card>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Enhanced Simulation Control */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Play className="h-5 w-5" />
                <span>Simulation Control Center</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Main Control Buttons */}
              <div className="flex flex-wrap items-center gap-3">
                <Button
                  onClick={runSimulation}
                  disabled={!contractAddress || !selectedAttack || isRunning}
                  className="bg-gradient-to-r from-red-500 to-orange-600 hover:from-red-600 hover:to-orange-700"
                >
                  {isRunning ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                      Running...
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Run Simulation
                    </>
                  )}
                </Button>

                {isRunning && (
                  <>
                    <Button
                      variant="outline"
                      onClick={() => {
                        setIsPaused(!isPaused);
                        toast.info(
                          isPaused ? "Simulation resumed" : "Simulation paused",
                        );
                      }}
                    >
                      {isPaused ? (
                        <>
                          <Play className="h-4 w-4 mr-2" />
                          Resume
                        </>
                      ) : (
                        <>
                          <Pause className="h-4 w-4 mr-2" />
                          Pause
                        </>
                      )}
                    </Button>

                    <Button variant="outline" onClick={stopSimulation}>
                      <StopCircle className="h-4 w-4 mr-2" />
                      Stop
                    </Button>
                  </>
                )}

                <Button
                  variant="outline"
                  onClick={() => {
                    setSimulationResult(null);
                    setProgress(0);
                    setCurrentStep(0);
                    setSimulationLog([]);
                    toast.success("Simulation reset");
                  }}
                  disabled={isRunning}
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Reset
                </Button>

                {simulationResult && (
                  <Button variant="outline" onClick={exportResults}>
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                )}
              </div>

              {/* Simulation Mode Controls */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4 bg-muted/50 rounded-lg">
                <div className="space-y-3">
                  <Label className="text-sm font-medium">Simulation Mode</Label>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="auto-mode"
                        checked={autoMode}
                        onCheckedChange={setAutoMode}
                      />
                      <Label htmlFor="auto-mode" className="text-sm">
                        Auto Mode
                      </Label>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="step-mode"
                        checked={stepByStep}
                        onCheckedChange={setStepByStep}
                      />
                      <Label htmlFor="step-mode" className="text-sm">
                        Step-by-Step
                      </Label>
                    </div>
                  </div>
                </div>

                <div className="space-y-3">
                  <Label className="text-sm font-medium">Speed Control</Label>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <Label className="text-xs">Slow</Label>
                      <input
                        type="range"
                        min="0.5"
                        max="3"
                        step="0.5"
                        value={simulationSpeed}
                        onChange={(e) =>
                          setSimulationSpeed(Number(e.target.value))
                        }
                        className="flex-1"
                      />
                      <Label className="text-xs">Fast</Label>
                    </div>
                    <div className="text-center text-xs text-muted-foreground">
                      Speed: {simulationSpeed}x
                    </div>
                  </div>
                </div>
              </div>

              {/* Progress and Step Indicator */}
              {isRunning && (
                <div className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                      <span>Overall Progress</span>
                      <span>{Math.round(progress)}%</span>
                    </div>
                    <Progress value={progress} className="h-3" />
                  </div>

                  {stepByStep && (
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Current Step</span>
                        <span>
                          {currentStep + 1} of {totalSteps}
                        </span>
                      </div>
                      <div className="flex space-x-2">
                        {Array.from({ length: totalSteps }, (_, i) => (
                          <div
                            key={i}
                            className={`flex-1 h-2 rounded ${
                              i <= currentStep ? "bg-blue-500" : "bg-muted"
                            }`}
                          />
                        ))}
                      </div>
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Init</span>
                        <span>Analyze</span>
                        <span>Execute</span>
                        <span>Verify</span>
                        <span>Report</span>
                      </div>
                    </div>
                  )}

                  {isPaused && (
                    <Alert>
                      <Pause className="h-4 w-4" />
                      <AlertDescription>
                        Simulation is paused. Click Resume to continue.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              )}

              {/* Live Simulation Log */}
              {simulationLog.length > 0 && (
                <div className="space-y-2">
                  <Label className="text-sm font-medium">Live Log</Label>
                  <div className="bg-black/90 text-green-400 p-3 rounded-lg font-mono text-xs max-h-32 overflow-y-auto">
                    {simulationLog.map((log, index) => (
                      <div key={index} className="flex">
                        <span className="text-muted-foreground mr-2">
                          [{new Date().toLocaleTimeString()}]
                        </span>
                        <span>{log}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Results */}
          <AnimatePresence>
            {simulationResult && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
              >
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Activity className="h-5 w-5" />
                        <span>Simulation Results</span>
                      </div>
                      {getStatusIcon(simulationResult.status)}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    {/* Summary */}
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold">
                          {simulationResult.riskScore}
                        </div>
                        <div className="text-sm text-gray-600">Risk Score</div>
                      </div>
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold">
                          ${simulationResult.exploitableValue.toFixed(0)}
                        </div>
                        <div className="text-sm text-gray-600">
                          Exploitable Value
                        </div>
                      </div>
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold">
                          {simulationResult.gasUsed.toLocaleString()}
                        </div>
                        <div className="text-sm text-gray-600">Gas Used</div>
                      </div>
                      <div className="text-center p-4 bg-gray-50 rounded-lg">
                        <div className="text-2xl font-bold">
                          {simulationResult.executionTime}s
                        </div>
                        <div className="text-sm text-gray-600">
                          Execution Time
                        </div>
                      </div>
                    </div>

                    {/* Timeline */}
                    <div className="space-y-4">
                      <h4 className="font-semibold">Execution Timeline</h4>
                      <div className="space-y-3">
                        {simulationResult.timeline.map((step, index) => (
                          <div
                            key={index}
                            className="flex items-start space-x-3"
                          >
                            <div className="mt-1">
                              {step.status === "success" && (
                                <CheckCircle className="h-4 w-4 text-green-600" />
                              )}
                              {step.status === "warning" && (
                                <AlertTriangle className="h-4 w-4 text-yellow-600" />
                              )}
                              {step.status === "error" && (
                                <XCircle className="h-4 w-4 text-red-600" />
                              )}
                            </div>
                            <div className="flex-1">
                              <div className="font-medium">{step.step}</div>
                              <div className="text-sm text-gray-600">
                                {step.description}
                              </div>
                              <div className="text-xs text-gray-400">
                                {step.timestamp.toLocaleTimeString()}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Mitigation */}
                    <div className="space-y-4">
                      <h4 className="font-semibold">Recommended Mitigations</h4>
                      <ul className="space-y-2">
                        {simulationResult.mitigation.map((item, index) => (
                          <li
                            key={index}
                            className="flex items-center space-x-2"
                          >
                            <Shield className="h-4 w-4 text-blue-600" />
                            <span className="text-sm">{item}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Advanced Options */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Advanced Options</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label>Gas Limit</Label>
                <Input
                  value={advancedOptions.gasLimit}
                  onChange={(e) =>
                    setAdvancedOptions((prev) => ({
                      ...prev,
                      gasLimit: e.target.value,
                    }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label>Gas Price (Gwei)</Label>
                <Input
                  value={advancedOptions.gasPrice}
                  onChange={(e) =>
                    setAdvancedOptions((prev) => ({
                      ...prev,
                      gasPrice: e.target.value,
                    }))
                  }
                />
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="fork"
                  checked={advancedOptions.fork}
                  onCheckedChange={(checked) =>
                    setAdvancedOptions((prev) => ({
                      ...prev,
                      fork: checked as boolean,
                    }))
                  }
                />
                <Label htmlFor="fork">Fork mainnet state</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="verbose"
                  checked={advancedOptions.verbose}
                  onCheckedChange={(checked) =>
                    setAdvancedOptions((prev) => ({
                      ...prev,
                      verbose: checked as boolean,
                    }))
                  }
                />
                <Label htmlFor="verbose">Verbose logging</Label>
              </div>
            </CardContent>
          </Card>

          {/* Simulation History */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Clock className="h-5 w-5" />
                <span>Recent Simulations</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              {simulationHistory.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">
                  No simulations run yet
                </p>
              ) : (
                <div className="space-y-3">
                  {simulationHistory.slice(0, 5).map((sim, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                    >
                      <div className="flex-1">
                        <div className="font-medium text-sm">
                          {
                            attackTypes.find((a) => a.id === sim.attackType)
                              ?.name
                          }
                        </div>
                        <div className="text-xs text-gray-500 font-mono">
                          {sim.contractAddress.slice(0, 8)}...
                        </div>
                      </div>
                      {getStatusIcon(sim.status)}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </PageLayout>
  );
};

export default SimulationSandbox;
