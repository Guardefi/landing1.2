import { useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
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
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Globe,
  ArrowLeftRight,
  Activity,
  CheckCircle2,
  Send,
  Network,
  Users,
  Zap,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import { NetworkTopology3D } from "@/components/ui/enhanced-3d";
import { ParticleField } from "@/components/ui/particle-effects";
import { apiClient } from "@/lib/api-client";
import { toast } from "sonner";

const BridgeNetwork = () => {
  const [transferForm, setTransferForm] = useState({
    fromChain: "",
    toChain: "",
    amount: "",
    token: "USDC",
  });

  // API Integration for Bridge Data
  const {
    data: bridgeStatus,
    isLoading: statusLoading,
    refetch: refetchStatus,
  } = useQuery({
    queryKey: ["bridge-status"],
    queryFn: () => apiClient.getBridgeStatus(),
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  const {
    data: bridgeTransactions,
    isLoading: transactionsLoading,
    refetch: refetchTransactions,
  } = useQuery({
    queryKey: ["bridge-transactions"],
    queryFn: () => apiClient.getBridgeTransactions(20),
    refetchInterval: 10000,
  });

  // Bridge Transfer Mutation
  const transferMutation = useMutation({
    mutationFn: (data: typeof transferForm) =>
      apiClient.initiateBridgeTransfer(
        data.fromChain,
        data.toChain,
        data.amount,
        data.token,
      ),
    onSuccess: (result) => {
      toast.success("Bridge transfer initiated successfully");
      setTransferForm({
        fromChain: "",
        toChain: "",
        amount: "",
        token: "USDC",
      });
      refetchTransactions();
    },
    onError: (error) => {
      toast.error("Failed to initiate bridge transfer");
      console.error("Bridge transfer error:", error);
    },
  });

  // Quote Mutation
  const quoteMutation = useMutation({
    mutationFn: (data: typeof transferForm) =>
      apiClient.getBridgeQuote(
        data.fromChain,
        data.toChain,
        data.amount,
        data.token,
      ),
    onSuccess: (quote) => {
      toast.success(`Quote: ${quote.estimatedFee} ${quote.feeCurrency}`);
    },
    onError: () => {
      toast.error("Failed to get bridge quote");
    },
  });

  const handleTransfer = () => {
    if (
      !transferForm.fromChain ||
      !transferForm.toChain ||
      !transferForm.amount
    ) {
      toast.error("Please fill in all required fields");
      return;
    }
    transferMutation.mutate(transferForm);
  };

  const handleGetQuote = () => {
    if (
      !transferForm.fromChain ||
      !transferForm.toChain ||
      !transferForm.amount
    ) {
      toast.error("Please fill in all required fields");
      return;
    }
    quoteMutation.mutate(transferForm);
  };

  // Bridge metrics from API
  const bridgeMetrics = bridgeStatus
    ? [
        {
          label: "Total Volume",
          value: bridgeStatus.totalVolume || "$0",
          change: bridgeStatus.volumeChange || "0%",
          period: "24h",
        },
        {
          label: "Active Chains",
          value: bridgeStatus.activeChains?.toString() || "0",
          change: bridgeStatus.newChains ? `+${bridgeStatus.newChains}` : "0",
          period: "new",
        },
        {
          label: "Success Rate",
          value: bridgeStatus.successRate || "0%",
          change: bridgeStatus.successRateChange || "0%",
          period: "7d",
        },
        {
          label: "Avg Time",
          value: bridgeStatus.averageTime || "0min",
          change: bridgeStatus.timeImprovement || "0s",
          period: "improvement",
        },
      ]
    : [];

  // Supported chains from API
  const supportedChains = bridgeStatus?.supportedChains || [
    {
      name: "Ethereum",
      status: "healthy",
      tvl: "$0",
      color: "#627EEA",
      transfers: 0,
    },
    {
      name: "Polygon",
      status: "healthy",
      tvl: "$0",
      color: "#8247E5",
      transfers: 0,
    },
    {
      name: "BSC",
      status: "warning",
      tvl: "$0",
      color: "#F3BA2F",
      transfers: 0,
    },
    {
      name: "Avalanche",
      status: "healthy",
      tvl: "$0",
      color: "#E84142",
      transfers: 0,
    },
    {
      name: "Arbitrum",
      status: "healthy",
      tvl: "$0",
      color: "#28A0F0",
      transfers: 0,
    },
    {
      name: "Optimism",
      status: "healthy",
      tvl: "$0",
      color: "#FF0420",
      transfers: 0,
    },
  ];

  // Active transfers from API or fallback data
  const activeTransfers = bridgeTransactions?.activeTransfers || [
    {
      id: "TX-001",
      route: "ETH → BSC",
      asset: "USDC 10,000",
      progress: 85,
      status: "processing",
      eta: "2 min",
    },
    {
      id: "TX-002",
      route: "MATIC → ETH",
      asset: "WETH 5.5",
      progress: 100,
      status: "completed",
      eta: "Completed",
    },
    {
      id: "TX-003",
      route: "AVAX → BSC",
      asset: "USDT 25,000",
      progress: 45,
      status: "validating",
      eta: "4 min",
    },
    {
      id: "TX-004",
      route: "ETH → POLY",
      asset: "DAI 8,000",
      progress: 15,
      status: "pending",
      eta: "8 min",
    },
  ];

  const validatorStats = [
    { label: "Total Validators", value: 127, change: "+3" },
    { label: "Online", value: 124, percentage: 97.6 },
    { label: "Total Stake", value: "$45.7M", change: "+2.3%" },
    { label: "Consensus Time", value: "2.1s", change: "-0.3s" },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "healthy":
        return "text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20";
      case "warning":
        return "text-amber-600 bg-amber-50 dark:bg-amber-900/20";
      case "error":
        return "text-red-600 bg-red-50 dark:bg-red-900/20";
      default:
        return "text-gray-600 bg-gray-50 dark:bg-gray-900/20";
    }
  };

  const getTransferStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "success";
      case "processing":
        return "default";
      case "validating":
        return "secondary";
      case "pending":
        return "outline";
      case "failed":
        return "destructive";
      default:
        return "secondary";
    }
  };

  return (
    <PageLayout variant="bridge">
      <PageHeader
        title="Cross-Chain Bridge Network"
        description="Multi-chain asset management and cross-chain transfers"
        icon={Globe}
        iconGradient="from-purple-500 to-blue-600"
        borderColor="border-purple-400/30"
      />
      {/* Bridge Status Header */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        {bridgeMetrics.map((metric) => (
          <Card key={metric.label}>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {metric.label}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="text-2xl font-bold">{metric.value}</div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary" className="text-xs">
                    {metric.change}
                  </Badge>
                  <span className="text-xs text-muted-foreground">
                    {metric.period}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Bridge Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Network Visualization */}
        <Card className="lg:col-span-2 lg:row-span-2 relative overflow-hidden">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Network className="h-5 w-5" />
              <span>Cross-Chain Network Map</span>
            </CardTitle>
            <CardDescription>
              Interactive 3D visualization of bridge connections and live
              transfers
            </CardDescription>
          </CardHeader>
          <CardContent className="p-0">
            <div className="relative h-80">
              <ParticleField
                particleCount={40}
                colors={["#8b5cf6", "#3b82f6", "#06b6d4"]}
                className="opacity-50"
              />
              <NetworkTopology3D
                nodes={supportedChains.slice(0, 6).map((chain, index) => ({
                  id: chain.name,
                  name: chain.name,
                  status: chain.status,
                  position: [
                    Math.cos(index * 60 * (Math.PI / 180)) * 3,
                    Math.sin(index * 60 * (Math.PI / 180)) * 3,
                    0,
                  ] as [number, number, number],
                }))}
                connections={[
                  { from: "Ethereum", to: "Polygon", active: true },
                  { from: "Ethereum", to: "BSC", active: false },
                  { from: "Ethereum", to: "Avalanche", active: true },
                  { from: "Polygon", to: "BSC", active: true },
                  { from: "BSC", to: "Avalanche", active: false },
                  { from: "Arbitrum", to: "Optimism", active: true },
                ]}
              />

              {/* Live Transfer Count */}
              <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur rounded-lg p-3 text-xs text-white">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                  <span>
                    Live Transfers:{" "}
                    {
                      activeTransfers.filter((t) => t.status === "processing")
                        .length
                    }
                  </span>
                </div>
              </div>

              {/* Volume Indicator */}
              <div className="absolute top-4 right-4 bg-black/60 backdrop-blur rounded-lg p-3 text-xs text-white">
                <div className="text-center">
                  <div className="text-lg font-bold text-purple-400">$2.3M</div>
                  <div>24h Volume</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Chain Selector */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <ArrowLeftRight className="h-5 w-5" />
              <span>Supported Chains</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {supportedChains.slice(0, 4).map((chain) => (
              <div
                key={chain.name}
                className="flex items-center justify-between p-2 border rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: chain.color }}
                  />
                  <div>
                    <div className="font-medium text-sm">{chain.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {chain.tvl}
                    </div>
                  </div>
                </div>
                <Badge className={getStatusColor(chain.status)}>
                  {chain.status}
                </Badge>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Transfer Interface */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Send className="h-5 w-5" />
              <span>Quick Transfer</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label htmlFor="from-chain" className="text-sm font-medium">
                From Chain
              </label>
              <select
                id="from-chain"
                className="w-full p-2 border rounded-lg bg-background"
              >
                <option>Ethereum</option>
                <option>Polygon</option>
                <option>BSC</option>
              </select>
            </div>
            <div className="space-y-2">
              <label htmlFor="to-chain" className="text-sm font-medium">
                To Chain
              </label>
              <select
                id="to-chain"
                className="w-full p-2 border rounded-lg bg-background"
              >
                <option>Polygon</option>
                <option>BSC</option>
                <option>Avalanche</option>
              </select>
            </div>
            <div className="space-y-2">
              <label htmlFor="asset-select" className="text-sm font-medium">
                Asset & Amount
              </label>
              <div className="flex space-x-2">
                <select
                  id="asset-select"
                  className="flex-1 p-2 border rounded-lg bg-background"
                >
                  <option>USDC</option>
                  <option>USDT</option>
                  <option>ETH</option>
                </select>
                <input
                  id="amount-input"
                  type="number"
                  placeholder="0.00"
                  className="flex-1 p-2 border rounded-lg bg-background"
                />
              </div>
            </div>
            <Button className="w-full">Estimate & Transfer</Button>
          </CardContent>
        </Card>
      </div>

      {/* Active Transfers and Validator Network */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Active Transfers */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>Active Transfers</span>
            </CardTitle>
            <CardDescription>
              Real-time cross-chain transfer monitoring
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activeTransfers.map((transfer) => (
                <div
                  key={transfer.id}
                  className="p-4 border rounded-lg space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <div className="font-medium text-sm">
                        {transfer.route}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {transfer.id} • {transfer.asset}
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge
                        variant={getTransferStatusColor(transfer.status) as any}
                      >
                        {transfer.status}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {transfer.eta}
                      </span>
                    </div>
                  </div>
                  <div className="space-y-1">
                    <div className="flex justify-between text-xs">
                      <span>Progress</span>
                      <span>{transfer.progress}%</span>
                    </div>
                    <Progress value={transfer.progress} className="h-2" />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Validator Network */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Users className="h-5 w-5" />
              <span>Validator Network</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {validatorStats.map((stat) => (
              <div key={stat.label} className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">{stat.label}</span>
                  <div className="text-right">
                    <div className="font-bold">{stat.value}</div>
                    {stat.change && (
                      <div className="text-xs text-muted-foreground">
                        {stat.change}
                      </div>
                    )}
                    {stat.percentage && (
                      <div className="text-xs text-green-600">
                        {stat.percentage}%
                      </div>
                    )}
                  </div>
                </div>
                {stat.percentage && (
                  <Progress value={stat.percentage} className="h-2" />
                )}
              </div>
            ))}

            <div className="pt-4 border-t">
              <div className="text-sm font-medium mb-2">Consensus Status</div>
              <div className="flex items-center space-x-2">
                <CheckCircle2 className="h-4 w-4 text-green-600" />
                <span className="text-sm text-green-600">Healthy</span>
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                Last consensus: 2.1s ago
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Network Health Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="h-5 w-5" />
            <span>Network Health Summary</span>
          </CardTitle>
          <CardDescription>
            Overall bridge network performance and status
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-2">
                99.7%
              </div>
              <div className="text-sm text-muted-foreground">Success Rate</div>
              <div className="text-xs text-green-600 mt-1">+0.1% this week</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                2.4min
              </div>
              <div className="text-sm text-muted-foreground">
                Average Transfer Time
              </div>
              <div className="text-xs text-blue-600 mt-1">
                15s faster than last week
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-purple-600 mb-2">
                $2.3M
              </div>
              <div className="text-sm text-muted-foreground">24h Volume</div>
              <div className="text-xs text-purple-600 mt-1">+8.9% today</div>
            </div>
          </div>
        </CardContent>
      </Card>
    </PageLayout>
  );
};

export default BridgeNetwork;
