import { useState, useEffect, useCallback } from "react";
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
import { Progress } from "@/components/ui/progress";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { LiveCounter } from "@/components/ui/live-counter";
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import { useTradingEngine } from "@/hooks";
import {
  ErrorBoundary,
  ModuleLoadingWrapper,
  ConnectionStatus,
} from "@/components/ui/error-boundary";
import {
  TrendingUp,
  Brain,
  Shield,
  Zap,
  Activity,
  RefreshCw,
  Play,
  Pause,
  Settings,
  DollarSign,
  PieChart,
  BarChart3,
  Bot,
  Target,
  Clock,
  Eye,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Loader2,
  Circle,
  Wifi,
  WifiOff,
  Network,
  TrendingDown,
  ExternalLink,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import { Link } from "react-router-dom";

interface DeployedBot {
  id: string;
  name: string;
  strategy: string;
  status: "active" | "idle" | "processing" | "error";
  position: { x: number; y: number };
  profit: number;
  trades: number;
  gasUsed: number;
  color: string;
}

interface SimulatedTransaction {
  id: string;
  fromBot: string;
  toBot?: string;
  type: "frontrun" | "backrun" | "arbitrage" | "liquidation" | "jit" | "oracle";
  amount: number;
  gas: number;
  success: boolean;
  timestamp: Date;
  path: { x: number; y: number }[];
}

const TradingAI = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  // Real-time API integration
  const {
    bots,
    metrics,
    isConnected,
    error: tradingError,
    startBot,
    stopBot,
    createBot,
  } = useTradingEngine();

  // Enhanced bot tracking for visualization (using real bot data + visualization positions)
  const [deployedBots, setDeployedBots] = useState<DeployedBot[]>([
    {
      id: "bot1",
      name: "ARB-Alpha",
      strategy: "arbitrage",
      status: "active",
      position: { x: 15, y: 20 },
      profit: 12.7,
      trades: 156,
      gasUsed: 2.1,
      color: "#00ff88",
    },
    {
      id: "bot2",
      name: "MEV-Delta",
      strategy: "mev_protection",
      status: "processing",
      position: { x: 35, y: 60 },
      profit: 8.4,
      trades: 89,
      gasUsed: 3.8,
      color: "#ff4444",
    },
    {
      id: "bot3",
      name: "LIQ-Beta",
      strategy: "liquidation",
      status: "active",
      position: { x: 65, y: 30 },
      profit: 15.2,
      trades: 34,
      gasUsed: 1.9,
      color: "#00ffff",
    },
    {
      id: "bot4",
      name: "FL-Gamma",
      strategy: "flashloan",
      status: "idle",
      position: { x: 80, y: 70 },
      profit: 22.1,
      trades: 67,
      gasUsed: 4.2,
      color: "#ffaa00",
    },
    {
      id: "bot5",
      name: "JIT-Theta",
      strategy: "jit_liquidity",
      status: "active",
      position: { x: 25, y: 80 },
      profit: 18.6,
      trades: 112,
      gasUsed: 2.8,
      color: "#ff88ff",
    },
  ]);

  // Transaction simulation
  const [transactions, setTransactions] = useState<SimulatedTransaction[]>([]);

  const tradingStrategies = [
    {
      id: "arbitrage",
      name: "Cross-DEX Arbitrage",
      description: "Exploit price differences between DEXs",
      status: "active",
      allocation: 25,
      pnl: 12847,
      trades24h: 156,
      winRate: 94.2,
      gasUsed: 2.1,
      riskLevel: "Medium",
    },
    {
      id: "mev_protection",
      name: "MEV Protection Engine",
      description: "Shield transactions from MEV attacks",
      status: "active",
      allocation: 30,
      pnl: 8239,
      protected: 156,
      saved: 23451,
      riskLevel: "Low",
    },
    {
      id: "liquidation",
      name: "Liquidation Hunter",
      description: "Monitor and execute liquidations",
      status: "active",
      allocation: 20,
      pnl: 15200,
      trades24h: 34,
      successRate: 98.1,
      riskLevel: "Low",
    },
    {
      id: "flashloan",
      name: "Flash Loan Arbitrage",
      description: "Zero-capital arbitrage opportunities",
      status: "paused",
      allocation: 15,
      pnl: 22100,
      trades24h: 67,
      successRate: 91.3,
      riskLevel: "High",
    },
    {
      id: "jit_liquidity",
      name: "JIT Liquidity Provider",
      description: "Just-in-time liquidity provisioning",
      status: "active",
      allocation: 10,
      pnl: 18600,
      trades24h: 112,
      apr: 18.9,
      riskLevel: "Medium",
    },
  ];

  const [activeStrategies, setActiveStrategies] = useState<Set<string>>(
    new Set(["arbitrage", "mev_protection", "liquidation", "jit_liquidity"]),
  );

  const [mevStats, setMevStats] = useState({
    totalProfit: 86.3,
    totalTrades: 501,
    avgSuccessRate: 92.8,
    gasEfficiency: 2.5,
    protectionLevel: 98.2,
    attacksPrevented: 1247,
    valueSaved: 45892,
  });

  const [recentTrades, setRecentTrades] = useState([
    {
      id: 1,
      strategy: "arbitrage",
      token: "WETH/USDC",
      profit: 2.34,
      gas: 0.012,
      timestamp: new Date(Date.now() - 1000 * 60 * 5),
      success: true,
    },
    {
      id: 2,
      strategy: "liquidation",
      token: "AAVE/ETH",
      profit: 5.67,
      gas: 0.008,
      timestamp: new Date(Date.now() - 1000 * 60 * 12),
      success: true,
    },
    {
      id: 3,
      strategy: "flashloan",
      token: "UNI/WETH",
      profit: 1.89,
      gas: 0.021,
      timestamp: new Date(Date.now() - 1000 * 60 * 18),
      success: false,
    },
    {
      id: 4,
      strategy: "jit_liquidity",
      token: "CRV/WETH",
      profit: 3.12,
      gas: 0.015,
      timestamp: new Date(Date.now() - 1000 * 60 * 25),
      success: true,
    },
  ]);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Generate mock transaction data
  const generateMockTransaction = useCallback((): SimulatedTransaction => {
    const activeBots = deployedBots.filter(
      (bot) => bot.status === "active" || bot.status === "processing",
    );
    if (activeBots.length === 0) return {} as SimulatedTransaction;

    const fromBot = activeBots[Math.floor(Math.random() * activeBots.length)];
    const types: SimulatedTransaction["type"][] = [
      "frontrun",
      "backrun",
      "arbitrage",
      "liquidation",
      "jit",
      "oracle",
    ];
    const type = types[Math.floor(Math.random() * types.length)];

    const toBot =
      Math.random() > 0.7
        ? activeBots[Math.floor(Math.random() * activeBots.length)]
        : undefined;

    return {
      id: `tx_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      fromBot: fromBot.id,
      toBot: toBot?.id,
      type,
      amount: Math.random() * 10,
      gas: Math.random() * 0.05,
      success: Math.random() > 0.1,
      timestamp: new Date(),
      path: toBot ? [fromBot.position, toBot.position] : [fromBot.position],
    };
  }, [deployedBots]);

  // Simulate real-time updates
  useEffect(() => {
    if (!isLive) return;

    const interval = setInterval(() => {
      // Update bot statuses
      setDeployedBots((prev) =>
        prev.map((bot) => {
          const shouldUpdate = Math.random() > 0.7;
          if (!shouldUpdate) return bot;

          const statuses: DeployedBot["status"][] = [
            "active",
            "idle",
            "processing",
          ];
          const newStatus =
            statuses[Math.floor(Math.random() * statuses.length)];

          return {
            ...bot,
            status: newStatus,
            profit: bot.profit + Math.random() * 2,
            trades: bot.trades + Math.floor(Math.random() * 3),
          };
        }),
      );

      // Generate transactions
      if (Math.random() > 0.4) {
        const newTx = generateMockTransaction();
        if (newTx.id) {
          setTransactions((prev) => [...prev.slice(-20), newTx]);
        }
      }

      // Update MEV stats
      setMevStats((prev) => ({
        ...prev,
        totalProfit: prev.totalProfit + Math.random() * 2,
        totalTrades: prev.totalTrades + Math.floor(Math.random() * 3),
        attacksPrevented: prev.attacksPrevented + (Math.random() > 0.8 ? 1 : 0),
        valueSaved: prev.valueSaved + Math.random() * 100,
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, [isLive, generateMockTransaction]);

  const toggleStrategy = (strategyId: string) => {
    setActiveStrategies((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(strategyId)) {
        newSet.delete(strategyId);
      } else {
        newSet.add(strategyId);
      }
      return newSet;
    });
  };

  const getRiskColor = (riskLevel: string) => {
    switch (riskLevel) {
      case "Low":
        return "#00ff88";
      case "Medium":
        return "#ffaa00";
      case "High":
        return "#ff4444";
      default:
        return "#999999";
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "#00ff88";
      case "processing":
        return "#ffaa00";
      case "idle":
        return "#00ffff";
      case "paused":
        return "#999999";
      case "error":
        return "#ff4444";
      default:
        return "#999999";
    }
  };

  const getBotStatusIcon = (status: DeployedBot["status"]) => {
    switch (status) {
      case "active":
        return <Wifi size={12} />;
      case "processing":
        return <Loader2 size={12} className="animate-spin" />;
      case "idle":
        return <Circle size={12} />;
      case "error":
        return <WifiOff size={12} />;
      default:
        return <Circle size={12} />;
    }
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
    <PageLayout variant="trading">
      <PageHeader
        title="AI Trading Engine"
        description="Advanced algorithmic trading with machine learning"
        icon={Brain}
        iconGradient="from-green-500 to-emerald-600"
        borderColor="border-green-400/30"
      />
      {/* Enhanced Trading Stats */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
      >
        {[
          {
            label: "Total Profit",
            value: mevStats.totalProfit,
            icon: DollarSign,
            color: "text-green-600",
            suffix: " ETH",
          },
          {
            label: "Active Trades",
            value: mevStats.totalTrades,
            icon: Activity,
            color: "text-blue-600",
          },
          {
            label: "Success Rate",
            value: mevStats.avgSuccessRate,
            icon: TrendingUp,
            color: "text-emerald-600",
            suffix: "%",
          },
          {
            label: "MEV Protected",
            value: mevStats.protectionLevel,
            icon: Shield,
            color: "text-purple-600",
            suffix: "%",
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

      {/* Bot Network Visualization */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="bg-background/80 backdrop-blur border rounded-xl p-6 mb-8 shadow-lg relative overflow-hidden"
      >
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold flex items-center space-x-2">
            <Network className="h-5 w-5" />
            <span>Deployed Bot Network</span>
          </h2>
          <div className="flex items-center gap-4 text-sm">
            <span className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              Active ({deployedBots.filter((b) => b.status === "active").length}
              )
            </span>
            <span className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-yellow-500" />
              Processing (
              {deployedBots.filter((b) => b.status === "processing").length})
            </span>
            <span className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-500" />
              Idle ({deployedBots.filter((b) => b.status === "idle").length})
            </span>
          </div>
        </div>

        {/* Network Grid Background */}
        <div className="absolute inset-6 opacity-20 pointer-events-none">
          <div
            className="w-full h-96"
            style={{
              backgroundImage: `
                  linear-gradient(rgba(34, 197, 94, 0.2) 1px, transparent 1px),
                  linear-gradient(90deg, rgba(34, 197, 94, 0.2) 1px, transparent 1px)
                `,
              backgroundSize: "40px 40px",
            }}
          />
        </div>

        {/* Bot Network */}
        <div className="relative h-96 w-full">
          {deployedBots.map((bot) => (
            <motion.div
              key={bot.id}
              className={bot.status === "active" ? "animate-pulse" : ""}
              style={{
                position: "absolute",
                left: `${bot.position.x}%`,
                top: `${bot.position.y}%`,
                transform: "translate(-50%, -50%)",
              }}
              whileHover={{ scale: 1.1, zIndex: 10 }}
              animate={{
                boxShadow: `0 0 ${
                  bot.status === "active" ? "30px" : "15px"
                } ${getStatusColor(bot.status)}30`,
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                repeatType: "reverse",
              }}
            >
              <div
                className="w-16 h-16 bg-background/90 backdrop-blur border-2 rounded-xl flex flex-col items-center justify-center cursor-pointer shadow-lg"
                style={{
                  borderColor: getStatusColor(bot.status),
                }}
              >
                <div className="flex items-center justify-center mb-1">
                  <Bot size={16} color={getStatusColor(bot.status)} />
                  {getBotStatusIcon(bot.status)}
                </div>
                <div className="text-xs font-semibold text-center leading-tight">
                  {bot.name}
                </div>
                <div
                  className="text-xs font-medium uppercase"
                  style={{ color: getStatusColor(bot.status) }}
                >
                  {bot.status}
                </div>

                {/* Bot hover info */}
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileHover={{ opacity: 1, scale: 1 }}
                  className="absolute top-20 left-1/2 transform -translateX-1/2 bg-background/95 backdrop-blur border rounded-lg p-3 min-w-32 z-20 pointer-events-none shadow-xl"
                >
                  <div className="text-sm font-semibold mb-2">
                    {bot.strategy.replace("_", " ").toUpperCase()}
                  </div>
                  <div className="space-y-1 text-xs">
                    <div className="text-green-600">
                      Profit: ${bot.profit.toFixed(2)} ETH
                    </div>
                    <div className="text-cyan-600">Trades: {bot.trades}</div>
                    <div className="text-amber-600">
                      Gas: {bot.gasUsed.toFixed(2)} ETH
                    </div>
                  </div>
                </motion.div>
              </div>
            </motion.div>
          ))}

          {/* Transaction Flow Lines */}
          <AnimatePresence>
            {transactions.slice(-5).map((tx) => {
              const fromBot = deployedBots.find((b) => b.id === tx.fromBot);
              const toBot = tx.toBot
                ? deployedBots.find((b) => b.id === tx.toBot)
                : null;

              if (!fromBot) return null;

              return (
                <motion.div
                  key={tx.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: [0, 1, 0] }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 3 }}
                  className="absolute inset-0 pointer-events-none"
                >
                  {toBot ? (
                    <svg className="absolute inset-0 w-full h-full">
                      <motion.line
                        x1={`${fromBot.position.x}%`}
                        y1={`${fromBot.position.y}%`}
                        x2={`${toBot.position.x}%`}
                        y2={`${toBot.position.y}%`}
                        stroke={tx.success ? "#00ff88" : "#ff4444"}
                        strokeWidth="2"
                        strokeDasharray="5,5"
                        opacity={0.7}
                        initial={{ pathLength: 0 }}
                        animate={{ pathLength: [0, 1, 0] }}
                        transition={{ duration: 2 }}
                      />
                    </svg>
                  ) : (
                    <motion.div
                      className="absolute w-5 h-5 rounded-full"
                      style={{
                        left: `${fromBot.position.x}%`,
                        top: `${fromBot.position.y}%`,
                        transform: "translate(-50%, -50%)",
                        backgroundColor: tx.success ? "#00ff88" : "#ff4444",
                        opacity: 0.6,
                      }}
                      animate={{ scale: [0, 3, 0], opacity: [0.6, 0, 0] }}
                      transition={{ duration: 2 }}
                    />
                  )}
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>

        {/* Live Statistics */}
        <div className="absolute bottom-4 right-4 flex gap-4 text-sm">
          <div className="text-green-600">
            Live Txs:{" "}
            {
              transactions.filter(
                (tx) => Date.now() - tx.timestamp.getTime() < 5000,
              ).length
            }
          </div>
          <div className="text-amber-600">
            Success Rate:{" "}
            {(
              (transactions.filter((tx) => tx.success).length /
                Math.max(transactions.length, 1)) *
              100
            ).toFixed(1)}
            %
          </div>
        </div>
      </motion.div>

      {/* Strategy Management Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.6 }}
        className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8"
      >
        {/* Enhanced Strategy Manager */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Settings className="h-5 w-5" />
              <span>Strategy Management</span>
            </CardTitle>
            <CardDescription>
              Configure and monitor AI trading strategies
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {tradingStrategies.map((strategy, index) => (
                <motion.div
                  key={strategy.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.1 * index }}
                  whileHover={{ scale: 1.02, y: -2 }}
                  onClick={() => toggleStrategy(strategy.id)}
                  className={`p-4 border rounded-lg cursor-pointer transition-all ${
                    activeStrategies.has(strategy.id)
                      ? "bg-green-500/10 border-green-500/50"
                      : "bg-background border-border hover:bg-muted/50"
                  }`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="font-semibold text-sm">{strategy.name}</h3>
                      <p className="text-xs text-muted-foreground">
                        {strategy.description}
                      </p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge
                        variant="outline"
                        style={{
                          backgroundColor: `${getRiskColor(strategy.riskLevel)}20`,
                          color: getRiskColor(strategy.riskLevel),
                          borderColor: `${getRiskColor(strategy.riskLevel)}40`,
                        }}
                      >
                        {strategy.riskLevel}
                      </Badge>
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{
                          backgroundColor: getStatusColor(strategy.status),
                          boxShadow: `0 0 8px ${getStatusColor(strategy.status)}`,
                        }}
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-3 text-xs">
                    <div>
                      <div className="font-bold text-green-600">
                        ${(strategy.pnl / 1000).toFixed(1)}K
                      </div>
                      <div className="text-muted-foreground">P&L</div>
                    </div>
                    <div>
                      <div className="font-bold text-cyan-600">
                        {strategy.trades24h || strategy.protected || "N/A"}
                      </div>
                      <div className="text-muted-foreground">
                        {strategy.trades24h ? "Trades" : "Protected"}
                      </div>
                    </div>
                  </div>

                  <div className="flex justify-between items-center text-xs">
                    <span className="text-muted-foreground">
                      Allocation: {strategy.allocation}%
                    </span>
                    {activeStrategies.has(strategy.id) && (
                      <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                    )}
                  </div>

                  <Progress value={strategy.allocation} className="h-1 mt-2" />
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Enhanced MEV Protection Panel */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5" />
              <span>MEV Protection</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="text-center">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.8 }}
                className="text-4xl font-bold text-emerald-600 mb-2"
              >
                <LiveCounter
                  value={mevStats.protectionLevel}
                  suffix="%"
                  decimals={1}
                  duration={2000}
                />
              </motion.div>
              <div className="text-sm text-muted-foreground">
                Protection Level
              </div>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm">Attacks Prevented</span>
                <span className="font-bold">
                  <LiveCounter
                    value={mevStats.attacksPrevented}
                    duration={2000}
                  />
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Value Saved</span>
                <span className="font-bold text-green-600">
                  $
                  <LiveCounter
                    value={mevStats.valueSaved}
                    decimals={0}
                    duration={2000}
                  />
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Success Rate</span>
                <span className="font-bold">
                  <LiveCounter
                    value={mevStats.avgSuccessRate}
                    suffix="%"
                    decimals={1}
                    duration={2000}
                  />
                </span>
              </div>
            </div>

            <div className="space-y-3">
              <div className="text-sm font-medium">Protection Methods</div>
              <div className="space-y-2">
                {[
                  "Private Mempool",
                  "Flashloan Protection",
                  "Sandwich Prevention",
                  "JIT Liquidity Guard",
                ].map((method) => (
                  <div
                    key={method}
                    className="flex justify-between items-center text-xs"
                  >
                    <span>{method}</span>
                    <Badge variant="secondary" className="text-xs">
                      Active
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Recent Trades */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 1.0 }}
      >
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center space-x-2">
                  <Clock className="h-5 w-5" />
                  <span>Live Trading Activity</span>
                </CardTitle>
                <CardDescription>
                  Real-time trade execution and performance
                </CardDescription>
              </div>
              <Button variant="outline" size="sm">
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-semibold">
                      Strategy
                    </th>
                    <th className="text-left py-3 px-4 font-semibold">
                      Token Pair
                    </th>
                    <th className="text-right py-3 px-4 font-semibold">
                      Profit
                    </th>
                    <th className="text-right py-3 px-4 font-semibold">
                      Gas Used
                    </th>
                    <th className="text-center py-3 px-4 font-semibold">
                      Status
                    </th>
                    <th className="text-right py-3 px-4 font-semibold">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {recentTrades.map((trade, index) => (
                    <motion.tr
                      key={trade.id}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: 0.1 * index }}
                      whileHover={{ backgroundColor: "rgba(0, 0, 0, 0.02)" }}
                      className="border-b hover:bg-muted/50"
                    >
                      <td className="py-3 px-4">
                        <Badge variant="outline" className="text-xs">
                          {trade.strategy}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 font-mono">{trade.token}</td>
                      <td
                        className={`py-3 px-4 text-right font-semibold ${
                          trade.profit > 0 ? "text-green-600" : "text-red-600"
                        }`}
                      >
                        {trade.profit > 0 ? "+" : ""}${trade.profit.toFixed(3)}{" "}
                        ETH
                      </td>
                      <td className="py-3 px-4 text-right text-red-600">
                        {trade.gas.toFixed(4)} ETH
                      </td>
                      <td className="py-3 px-4 text-center">
                        {trade.success ? (
                          <CheckCircle size={16} className="text-green-500" />
                        ) : (
                          <XCircle size={16} className="text-red-500" />
                        )}
                      </td>
                      <td className="py-3 px-4 text-right text-muted-foreground text-xs">
                        {formatTime(trade.timestamp)}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </PageLayout>
  );
};

export default TradingAI;
