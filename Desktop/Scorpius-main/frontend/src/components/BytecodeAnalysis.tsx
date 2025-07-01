import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { usePersistedStats } from "@/hooks/usePersistedStats";
import {
  Binary,
  Upload,
  Search,
  Eye,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Download,
  FileCode,
  Cpu,
  Target,
  GitCompare,
  Flag,
  Shield,
  Activity,
  Hash,
  Layers,
  TrendingUp,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ThreatMatch {
  id: string;
  contractName: string;
  similarity: number;
  threatLevel: "low" | "medium" | "high" | "critical";
  contractAddress: string;
  matchedFunctions: string[];
  opcodeFamily: string[];
  description: string;
  firstSeen: Date;
  lastSeen: Date;
  reportCount: number;
}

interface BytecodeAnalysis {
  contractAddress: string;
  bytecodeSize: number;
  uniqueOpcodes: number;
  functionCount: number;
  complexity: number;
  gasOptimization: number;
  securityScore: number;
  decompiled: boolean;
}

export const BytecodeAnalysis = () => {
  const [contractInput, setContractInput] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<BytecodeAnalysis | null>(null);
  const [threatMatches, setThreatMatches] = useState<ThreatMatch[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<ThreatMatch | null>(null);
  const [uploadedCode, setUploadedCode] = useState("");
  const [showDiff, setShowDiff] = useState(false);
  const { stats: persistedStats } = usePersistedStats();
  const [stats, setStats] = useState({
    totalScans: persistedStats.scanStats.totalScans,
    threatsDetected: persistedStats.scanStats.threatsDetected,
    falsePositives: 0,
    avgSimilarity: 0,
  });

  // Mock threat database
  const mockThreats: ThreatMatch[] = [
    {
      id: "1",
      contractName: "HoneyPot_V3",
      similarity: 94.8,
      threatLevel: "critical",
      contractAddress: "0x742d35Cc6431C8BF3240C39B6969E3C77e1345eF",
      matchedFunctions: ["withdraw", "balanceOf", "_transfer"],
      opcodeFamily: ["SELFDESTRUCT", "DELEGATECALL", "CALL"],
      description:
        "Advanced honeypot with reentrancy trap and balance manipulation",
      firstSeen: new Date("2023-10-15"),
      lastSeen: new Date("2024-01-20"),
      reportCount: 47,
    },
    {
      id: "2",
      contractName: "FakeToken_Clone",
      similarity: 87.3,
      threatLevel: "high",
      contractAddress: "0x9F8b2C4D5E6A7B8C9D0E1F2A3B4C5D6E7F8A9B0C",
      matchedFunctions: ["transfer", "approve", "mint"],
      opcodeFamily: ["SSTORE", "SLOAD", "MSTORE"],
      description: "Malicious token contract with hidden ownership backdoor",
      firstSeen: new Date("2023-11-22"),
      lastSeen: new Date("2024-01-18"),
      reportCount: 23,
    },
    {
      id: "3",
      contractName: "RugPull_Pattern",
      similarity: 76.2,
      threatLevel: "high",
      contractAddress: "0x7E8F9A0B1C2D3E4F5A6B7C8D9E0F1A2B3C4D5E6F",
      matchedFunctions: ["removeLiquidity", "emergencyWithdraw"],
      opcodeFamily: ["CALL", "STATICCALL", "RETURN"],
      description:
        "Contract pattern associated with liquidity removal exploits",
      firstSeen: new Date("2023-12-01"),
      lastSeen: new Date("2024-01-15"),
      reportCount: 31,
    },
    {
      id: "4",
      contractName: "Phishing_Proxy",
      similarity: 68.9,
      threatLevel: "medium",
      contractAddress: "0x3B2C1A9E8F7D6C5B4A3E2D1C9B8A7F6E5D4C3B2A",
      matchedFunctions: ["fallback", "receive"],
      opcodeFamily: ["DELEGATECALL", "CALLDATALOAD"],
      description: "Proxy contract with suspicious delegation patterns",
      firstSeen: new Date("2023-09-30"),
      lastSeen: new Date("2024-01-10"),
      reportCount: 12,
    },
  ];

  const analyzeContract = async () => {
    if (!contractInput.trim()) return;

    setIsAnalyzing(true);
    setThreatMatches([]);
    setAnalysis(null);

    try {
      // Make real API call to bytecode analysis service
      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/scanner/bytecode/analyze`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            contractAddress: contractInput,
          }),
        },
      );

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          setAnalysis(data.data.analysis);
          setThreatMatches(data.data.threats || []);
        } else {
          throw new Error(data.error || "Analysis failed");
        }
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      console.error("Bytecode analysis failed:", error);

      // Show error message to user
      setAnalysis({
        contractAddress: contractInput,
        bytecodeSize: 0,
        uniqueOpcodes: 0,
        functionCount: 0,
        complexity: 0,
        gasOptimization: 0,
        securityScore: 0,
        decompiled: false,
        error: error instanceof Error ? error.message : "Analysis failed",
      });
      setThreatMatches([]);
    }

    setIsAnalyzing(false);

    setStats((prev) => ({
      ...prev,
      totalScans: prev.totalScans + 1,
    }));
  };

  const getThreatColor = (level: string) => {
    switch (level) {
      case "critical":
        return "#ff0040";
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

  const getSimilarityColor = (similarity: number) => {
    if (similarity >= 90) return "#ff0040";
    if (similarity >= 75) return "#ff4444";
    if (similarity >= 50) return "#ffaa00";
    if (similarity >= 25) return "#00ffff";
    return "#00ff88";
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "#00ff88";
    if (score >= 60) return "#ffaa00";
    return "#ff4444";
  };

  const formatAddress = (address: string) => {
    return `${address.slice(0, 6)}...${address.slice(-4)}`;
  };

  return (
    <div className="space-y-6">
      {/* Analysis Input */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
      >
        <Card className="glass border border-purple-400/30">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2 text-purple-400">
              <Binary className="h-5 w-5" />
              <span>Bytecode Analysis</span>
            </CardTitle>
            <CardDescription>
              Analyze smart contract bytecode for similarity matching and threat
              detection
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Contract Input */}
              <div>
                <Label className="text-gray-300 mb-2 block">
                  Contract Address or Bytecode
                </Label>
                <Input
                  value={contractInput}
                  onChange={(e) => setContractInput(e.target.value)}
                  placeholder="0x... or paste bytecode"
                  className="glass border-purple-400/50 text-white placeholder-gray-500 focus:border-purple-400 font-mono"
                />

                <div className="flex gap-3 mt-4">
                  <Button
                    onClick={analyzeContract}
                    disabled={isAnalyzing || !contractInput.trim()}
                    className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 glow-purple"
                  >
                    {isAnalyzing ? (
                      <>
                        <motion.div
                          animate={{ rotate: 360 }}
                          transition={{
                            duration: 1,
                            repeat: Infinity,
                            ease: "linear",
                          }}
                        >
                          <Cpu className="h-4 w-4 mr-2" />
                        </motion.div>
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Search className="h-4 w-4 mr-2" />
                        Analyze Contract
                      </>
                    )}
                  </Button>

                  <Button
                    variant="outline"
                    className="border-purple-400/50 text-purple-400 hover:bg-purple-500/10"
                  >
                    <Upload className="h-4 w-4 mr-2" />
                    Upload File
                  </Button>
                </div>
              </div>

              {/* Code Upload */}
              <div>
                <Label className="text-gray-300 mb-2 block">
                  Or Upload Source Code
                </Label>
                <textarea
                  value={uploadedCode}
                  onChange={(e) => setUploadedCode(e.target.value)}
                  placeholder="// Paste your Solidity code here..."
                  className="w-full h-32 glass border border-purple-400/50 rounded-lg text-white placeholder-gray-500 focus:border-purple-400 focus:outline-none p-3 font-mono text-sm resize-none"
                />
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Analysis Results */}
      <AnimatePresence>
        {analysis && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.5 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-6"
          >
            {/* Contract Metrics */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
            >
              <Card className="glass border border-cyan-400/30">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-cyan-400">
                    <FileCode className="h-5 w-5" />
                    <span>Contract Metrics</span>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {[
                    {
                      label: "Bytecode Size",
                      value: `${analysis.bytecodeSize.toLocaleString()} bytes`,
                      icon: FileCode,
                    },
                    {
                      label: "Unique Opcodes",
                      value: analysis.uniqueOpcodes.toString(),
                      icon: Hash,
                    },
                    {
                      label: "Functions",
                      value: analysis.functionCount.toString(),
                      icon: Layers,
                    },
                    {
                      label: "Decompiled",
                      value: analysis.decompiled ? "Yes" : "No",
                      icon: Eye,
                    },
                  ].map((metric) => (
                    <div
                      key={metric.label}
                      className="flex items-center space-x-3 p-3 glass border border-gray-600/30 rounded-lg"
                    >
                      <div className="p-2 rounded-lg bg-cyan-500/20 border border-cyan-400/30">
                        <metric.icon className="h-4 w-4 text-cyan-400" />
                      </div>
                      <div className="flex-1">
                        <div className="text-sm text-gray-400">
                          {metric.label}
                        </div>
                        <div className="text-white font-medium font-mono">
                          {metric.value}
                        </div>
                      </div>
                    </div>
                  ))}

                  {/* Score Bars */}
                  <div className="space-y-4 pt-4">
                    {[
                      {
                        label: "Complexity",
                        value: analysis.complexity,
                        color: "#ffaa00",
                      },
                      {
                        label: "Gas Optimization",
                        value: analysis.gasOptimization,
                        color: "#00ff88",
                      },
                      {
                        label: "Security Score",
                        value: analysis.securityScore,
                        color: getScoreColor(analysis.securityScore),
                      },
                    ].map((score) => (
                      <div key={score.label}>
                        <div className="flex justify-between mb-2 text-sm">
                          <span className="text-gray-400">{score.label}</span>
                          <span className="text-white font-mono">
                            {score.value}%
                          </span>
                        </div>
                        <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                          <motion.div
                            initial={{ width: "0%" }}
                            animate={{ width: `${score.value}%` }}
                            transition={{ duration: 1, delay: 0.3 }}
                            className="h-full rounded-full"
                            style={{
                              backgroundColor: score.color,
                              boxShadow: `0 0 10px ${score.color}`,
                            }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </motion.div>

            {/* Threat Matches */}
            <div className="lg:col-span-2">
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <Card className="glass border border-red-400/30">
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2 text-red-400">
                      <AlertTriangle className="h-5 w-5" />
                      <span>Threat Matches</span>
                      <Badge
                        variant="outline"
                        className="border-red-400 text-red-400"
                      >
                        {threatMatches.length} found
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {threatMatches.map((threat, index) => (
                        <motion.div
                          key={threat.id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ duration: 0.3, delay: index * 0.1 }}
                          className="p-4 glass border border-gray-600/30 rounded-lg hover:border-red-400/50 transition-all cursor-pointer"
                          onClick={() => setSelectedMatch(threat)}
                        >
                          <div className="flex justify-between items-start mb-3">
                            <div>
                              <div className="font-medium text-white mb-1">
                                {threat.contractName}
                              </div>
                              <div className="text-sm text-gray-400 mb-2">
                                {formatAddress(threat.contractAddress)}
                              </div>
                              <div className="flex gap-2 flex-wrap">
                                {threat.matchedFunctions
                                  .slice(0, 2)
                                  .map((func) => (
                                    <Badge
                                      key={func}
                                      variant="outline"
                                      className="border-cyan-400/50 text-cyan-400 text-xs"
                                    >
                                      {func}()
                                    </Badge>
                                  ))}
                              </div>
                            </div>
                            <Badge
                              variant="outline"
                              className={`border-${
                                threat.threatLevel === "critical"
                                  ? "red"
                                  : threat.threatLevel === "high"
                                    ? "orange"
                                    : threat.threatLevel === "medium"
                                      ? "amber"
                                      : "green"
                              }-400 text-${
                                threat.threatLevel === "critical"
                                  ? "red"
                                  : threat.threatLevel === "high"
                                    ? "orange"
                                    : threat.threatLevel === "medium"
                                      ? "amber"
                                      : "green"
                              }-400`}
                            >
                              {threat.threatLevel}
                            </Badge>
                          </div>

                          {/* Similarity Bar */}
                          <div>
                            <div className="flex justify-between mb-1 text-sm">
                              <span className="text-gray-400">Similarity</span>
                              <span className="text-white font-mono">
                                {threat.similarity.toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full h-1.5 bg-gray-800 rounded-full overflow-hidden">
                              <motion.div
                                initial={{ width: "0%" }}
                                animate={{ width: `${threat.similarity}%` }}
                                transition={{
                                  duration: 0.8,
                                  delay: index * 0.2,
                                }}
                                className="h-full rounded-full"
                                style={{
                                  backgroundColor: getSimilarityColor(
                                    threat.similarity,
                                  ),
                                  boxShadow: `0 0 8px ${getSimilarityColor(
                                    threat.similarity,
                                  )}`,
                                }}
                              />
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Selected Threat Details Modal */}
      <AnimatePresence>
        {selectedMatch && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setSelectedMatch(null)}
          >
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 25 }}
              onClick={(e) => e.stopPropagation()}
              className="bg-black border-2 border-red-400/50 rounded-2xl p-8 max-w-4xl w-full max-h-[80vh] overflow-y-auto glass"
            >
              <div className="flex justify-between items-center mb-6">
                <h3 className="text-xl font-bold text-red-400 flex items-center space-x-2">
                  <AlertTriangle className="h-6 w-6" />
                  <span>Threat Analysis: {selectedMatch.contractName}</span>
                </h3>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setSelectedMatch(null)}
                  className="text-gray-400 hover:text-white"
                >
                  <XCircle className="h-5 w-5" />
                </Button>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-6">
                <div>
                  <h4 className="text-red-400 mb-4 font-semibold">
                    Threat Details
                  </h4>
                  <div className="space-y-3">
                    {[
                      {
                        label: "Contract Name",
                        value: selectedMatch.contractName,
                      },
                      {
                        label: "Contract Address",
                        value: selectedMatch.contractAddress,
                      },
                      {
                        label: "Threat Level",
                        value: selectedMatch.threatLevel.toUpperCase(),
                      },
                      {
                        label: "Similarity Score",
                        value: `${selectedMatch.similarity.toFixed(2)}%`,
                      },
                      {
                        label: "Report Count",
                        value: selectedMatch.reportCount.toString(),
                      },
                      {
                        label: "First Seen",
                        value: selectedMatch.firstSeen.toLocaleDateString(),
                      },
                      {
                        label: "Last Seen",
                        value: selectedMatch.lastSeen.toLocaleDateString(),
                      },
                    ].map((item) => (
                      <div key={item.label}>
                        <div className="text-sm text-gray-400 mb-1">
                          {item.label}
                        </div>
                        <div className="text-sm font-mono text-white bg-gray-900/50 p-2 rounded border border-gray-700">
                          {item.value}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-cyan-400 mb-4 font-semibold">
                    Technical Analysis
                  </h4>

                  <div className="mb-4">
                    <div className="text-sm text-gray-400 mb-2">
                      Matched Functions
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {selectedMatch.matchedFunctions.map((func) => (
                        <Badge
                          key={func}
                          variant="outline"
                          className="border-cyan-400/50 text-cyan-400 font-mono"
                        >
                          {func}()
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div className="mb-4">
                    <div className="text-sm text-gray-400 mb-2">
                      Opcode Families
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {selectedMatch.opcodeFamily.map((opcode) => (
                        <Badge
                          key={opcode}
                          variant="outline"
                          className="border-amber-400/50 text-amber-400 font-mono"
                        >
                          {opcode}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  <div>
                    <div className="text-sm text-gray-400 mb-2">
                      Similarity Breakdown
                    </div>
                    <div className="relative w-full h-6 bg-gray-800 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-1000"
                        style={{
                          width: `${selectedMatch.similarity}%`,
                          backgroundColor: getSimilarityColor(
                            selectedMatch.similarity,
                          ),
                          boxShadow: `0 0 15px ${getSimilarityColor(
                            selectedMatch.similarity,
                          )}`,
                        }}
                      />
                      <div className="absolute inset-0 flex items-center justify-center text-sm font-bold text-black font-mono">
                        {selectedMatch.similarity.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="p-4 glass border border-red-400/30 rounded-lg mb-6">
                <div className="flex items-center space-x-2 mb-2">
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                  <span className="font-semibold text-red-400">
                    Threat Description
                  </span>
                </div>
                <p className="text-gray-300 text-sm leading-relaxed">
                  {selectedMatch.description}
                </p>
              </div>

              <div className="flex gap-3 flex-wrap">
                <Button className="bg-gradient-to-r from-red-600 to-red-700 hover:from-red-500 hover:to-red-600">
                  <Flag className="h-4 w-4 mr-2" />
                  Flag as Threat
                </Button>
                <Button
                  variant="outline"
                  className="border-green-400/50 text-green-400 hover:bg-green-500/10"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Report False Positive
                </Button>
                <Button
                  variant="outline"
                  className="border-cyan-400/50 text-cyan-400 hover:bg-cyan-500/10"
                >
                  <GitCompare className="h-4 w-4 mr-2" />
                  View Diff
                </Button>
                <Button
                  variant="outline"
                  className="border-amber-400/50 text-amber-400 hover:bg-amber-500/10"
                >
                  <Download className="h-4 w-4 mr-2" />
                  Export Report
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
