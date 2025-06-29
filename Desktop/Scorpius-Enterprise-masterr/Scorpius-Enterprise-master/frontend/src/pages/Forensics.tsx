import { useState, useEffect } from "react";
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
import {
  Search,
  Brain,
  Shield,
  Eye,
  Network,
  Filter,
  RefreshCw,
  Download,
  FileText,
  AlertTriangle,
  TrendingUp,
  Database,
} from "lucide-react";
import { PageHeader } from "@/components/PageHeader";

const Forensics = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const investigationMetrics = [
    {
      label: "Active Investigations",
      value: "12",
      change: "+3",
      period: "today",
    },
    {
      label: "Suspicious Addresses",
      value: "847",
      change: "+156",
      period: "flagged",
    },
    {
      label: "Compliance Score",
      value: "97.8%",
      change: "+1.2%",
      period: "improved",
    },
    { label: "AML Alerts", value: "23", change: "-5", period: "24h" },
  ];

  const transactionAnalysis = [
    {
      address: "0x1234...5678",
      type: "wallet",
      riskScore: 85,
      volume: "$245K",
      flags: ["mixing", "high-risk"],
      transactions: 1247,
    },
    {
      address: "0x8765...4321",
      type: "exchange",
      riskScore: 15,
      volume: "$2.3M",
      flags: ["verified"],
      transactions: 8934,
    },
    {
      address: "0xabcd...ef01",
      type: "contract",
      riskScore: 62,
      volume: "$89K",
      flags: ["suspicious"],
      transactions: 345,
    },
    {
      address: "0x9876...1234",
      type: "wallet",
      riskScore: 92,
      volume: "$156K",
      flags: ["sanctions", "mixer"],
      transactions: 567,
    },
  ];

  const patternDetection = [
    {
      name: "Mixing Service Detection",
      confidence: 87,
      description: "Potential coin mixing activity detected",
      addresses: 12,
      transactions: 45,
      severity: "high",
    },
    {
      name: "Rapid Exchange Pattern",
      confidence: 73,
      description: "Unusually fast exchange hopping",
      addresses: 8,
      timeframe: "2 hours",
      severity: "medium",
    },
    {
      name: "Layering Behavior",
      confidence: 91,
      description: "Complex layering structure identified",
      layers: 7,
      totalValue: "$250K",
      severity: "high",
    },
    {
      name: "Circular Transactions",
      confidence: 65,
      description: "Self-referential transaction pattern",
      cycles: 15,
      frequency: "hourly",
      severity: "medium",
    },
  ];

  const complianceMonitoring = [
    {
      category: "AML Screening",
      status: "normal",
      metrics: [
        { label: "Suspicious Transactions", value: 23, threshold: 50 },
        { label: "High-Risk Addresses", value: 156, change: "+12" },
      ],
    },
    {
      category: "Sanctions Screening",
      status: "active",
      databases: ["OFAC", "EU Sanctions", "Custom Watchlists"],
      coverage: 99.7,
    },
  ];

  const getRiskColor = (score: number) => {
    if (score >= 80) return "text-red-600 bg-red-50 dark:bg-red-900/20";
    if (score >= 50) return "text-amber-600 bg-amber-50 dark:bg-amber-900/20";
    return "text-green-600 bg-green-50 dark:bg-green-900/20";
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "destructive";
      case "medium":
        return "default";
      case "low":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <div className="min-h-screen p-6">
      <PageHeader
        title="Blockchain Forensics Center"
        description="AI-powered investigation and compliance hub"
        icon={Search}
        iconGradient="from-indigo-500 to-purple-600"
        borderColor="border-indigo-400/30"
      />

      <main className="max-w-7xl mx-auto space-y-8">
        {/* Investigation Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          {investigationMetrics.map((metric) => (
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

        {/* Main Forensics Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Transaction Graph Visualization */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Network className="h-5 w-5" />
                <span>Transaction Flow Analysis</span>
              </CardTitle>
              <CardDescription>
                Interactive network graph of address relationships and fund
                flows
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="relative h-80 bg-gradient-to-br from-slate-900 to-indigo-900 rounded-lg overflow-hidden">
                {/* Transaction Network Visualization */}
                <div className="absolute inset-0 p-6">
                  <div className="relative h-full">
                    {/* Central node */}
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
                      <div className="w-16 h-16 rounded-full bg-red-500 flex items-center justify-center border-4 border-red-300 animate-pulse">
                        <AlertTriangle className="h-6 w-6 text-white" />
                      </div>
                      <div className="text-center mt-1">
                        <div className="text-xs text-white font-medium">
                          High Risk
                        </div>
                        <div className="text-xs text-red-300">$245K</div>
                      </div>
                    </div>

                    {/* Connected addresses */}
                    {[
                      {
                        position: { top: "20%", left: "30%" },
                        risk: "medium",
                        color: "amber",
                      },
                      {
                        position: { top: "30%", right: "20%" },
                        risk: "low",
                        color: "green",
                      },
                      {
                        position: { bottom: "25%", left: "25%" },
                        risk: "high",
                        color: "red",
                      },
                      {
                        position: { bottom: "20%", right: "30%" },
                        risk: "medium",
                        color: "amber",
                      },
                    ].map((node, index) => (
                      <div
                        key={index}
                        className="absolute transform -translate-x-1/2 -translate-y-1/2"
                        style={node.position}
                      >
                        <div
                          className={`w-8 h-8 rounded-full border-2 flex items-center justify-center ${
                            node.color === "red"
                              ? "bg-red-500 border-red-300"
                              : node.color === "amber"
                                ? "bg-amber-500 border-amber-300"
                                : "bg-green-500 border-green-300"
                          }`}
                        >
                          <div className="w-2 h-2 bg-white rounded-full" />
                        </div>

                        {/* Connection lines */}
                        <div className="absolute inset-0">
                          <div className="w-px h-12 bg-indigo-400/50 transform -translate-x-1/2" />
                        </div>
                      </div>
                    ))}

                    {/* Transaction flow animations */}
                    <div className="absolute top-12 left-16 w-2 h-2 bg-indigo-400 rounded-full animate-ping" />
                    <div className="absolute bottom-16 right-20 w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
                  </div>
                </div>

                {/* Legend */}
                <div className="absolute bottom-4 left-4 space-y-1 text-xs text-white">
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full" />
                    <span>High Risk</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-amber-500 rounded-full" />
                    <span>Medium Risk</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full" />
                    <span>Low Risk</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Compliance Monitoring Panel */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Shield className="h-5 w-5" />
                <span>Compliance Monitor</span>
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {complianceMonitoring.map((category) => (
                <div key={category.category} className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-sm">
                      {category.category}
                    </span>
                    <Badge
                      variant={
                        category.status === "normal" ? "secondary" : "default"
                      }
                    >
                      {category.status}
                    </Badge>
                  </div>

                  {category.metrics && (
                    <div className="space-y-2">
                      {category.metrics.map((metric) => (
                        <div key={metric.label} className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span>{metric.label}</span>
                            <span>{metric.value}</span>
                          </div>
                          {metric.threshold && (
                            <Progress
                              value={(metric.value / metric.threshold) * 100}
                              className="h-1"
                            />
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {category.databases && (
                    <div className="space-y-1">
                      {category.databases.map((db) => (
                        <div key={db} className="flex justify-between text-xs">
                          <span>{db}</span>
                          <Badge variant="outline">Active</Badge>
                        </div>
                      ))}
                      <div className="text-xs text-muted-foreground">
                        Coverage: {category.coverage}%
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

        {/* AI Pattern Analysis and Risk Assessment */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* AI Pattern Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Brain className="h-5 w-5" />
                <span>AI Pattern Detection</span>
              </CardTitle>
              <CardDescription>
                Machine learning-powered suspicious pattern identification
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {patternDetection.map((pattern) => (
                  <div key={pattern.name} className="p-3 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium text-sm">{pattern.name}</div>
                      <div className="flex items-center space-x-2">
                        <Badge
                          variant={getSeverityColor(pattern.severity) as any}
                        >
                          {pattern.severity}
                        </Badge>
                        <span className="text-xs text-muted-foreground">
                          {pattern.confidence}%
                        </span>
                      </div>
                    </div>
                    <div className="text-xs text-muted-foreground mb-2">
                      {pattern.description}
                    </div>
                    <div className="text-xs space-y-1">
                      {pattern.addresses && (
                        <div>Addresses: {pattern.addresses}</div>
                      )}
                      {pattern.transactions && (
                        <div>Transactions: {pattern.transactions}</div>
                      )}
                      {pattern.totalValue && (
                        <div>Total Value: {pattern.totalValue}</div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Transaction Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Eye className="h-5 w-5" />
                <span>Address Risk Assessment</span>
              </CardTitle>
              <CardDescription>
                Detailed risk analysis of monitored addresses
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {transactionAnalysis.map((address) => (
                  <div
                    key={address.address}
                    className="p-3 border rounded-lg space-y-2"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-mono text-sm">
                          {address.address}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          {address.type} • {address.transactions} txs
                        </div>
                      </div>
                      <Badge className={getRiskColor(address.riskScore)}>
                        Risk: {address.riskScore}
                      </Badge>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium">
                        Volume: {address.volume}
                      </span>
                      <div className="flex space-x-1">
                        {address.flags.map((flag) => (
                          <Badge
                            key={flag}
                            variant="outline"
                            className="text-xs"
                          >
                            {flag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Investigation Tools */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Database className="h-5 w-5" />
              <span>Investigation Tools</span>
            </CardTitle>
            <CardDescription>
              Advanced blockchain analysis and reporting tools
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 text-center py-8">
              <div>
                <Search className="h-8 w-8 mx-auto text-indigo-600 mb-2" />
                <h4 className="font-semibold mb-1">Address Investigation</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Deep dive into address history and connections
                </p>
                <Button variant="outline" size="sm">
                  Launch Tool
                </Button>
              </div>
              <div>
                <TrendingUp className="h-8 w-8 mx-auto text-purple-600 mb-2" />
                <h4 className="font-semibold mb-1">Flow Analysis</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Track fund movements across multiple hops
                </p>
                <Button variant="outline" size="sm">
                  Launch Tool
                </Button>
              </div>
              <div>
                <FileText className="h-8 w-8 mx-auto text-blue-600 mb-2" />
                <h4 className="font-semibold mb-1">Compliance Reports</h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Generate regulatory compliance documentation
                </p>
                <Button variant="outline" size="sm">
                  <Download className="h-3 w-3 mr-1" />
                  Generate
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </main>
    </div>
  );
};

export default Forensics;
