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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  BarChart3,
  TrendingUp,
  PieChart,
  RefreshCw,
  Download,
  Building2,
  DollarSign,
  Users,
  Globe,
} from "lucide-react";
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import {
  EnhancedLineChart,
  EnhancedDonutChart,
  EnhancedComposedChart,
  EnhancedRadialChart,
} from "@/components/ui/enhanced-charts";

const Analytics = () => {
  useEffect(() => {
    const timer = setInterval(() => {}, 1000);
    return () => clearInterval(timer);
  }, []);

  const kpis = [
    {
      title: "Total Value Secured",
      value: "$847.2M",
      change: "+23.4%",
      period: "QoQ",
      icon: Building2,
      color: "text-blue-600",
    },
    {
      title: "Threats Prevented",
      value: "12,847",
      change: "+156%",
      period: "YoY",
      icon: TrendingUp,
      color: "text-red-600",
    },
    {
      title: "Trading Revenue",
      value: "$2.34M",
      change: "+45.7%",
      period: "MoM",
      icon: DollarSign,
      color: "text-green-600",
    },
    {
      title: "System Uptime",
      value: "99.97%",
      change: "+0.03%",
      period: "MTD",
      icon: BarChart3,
      color: "text-purple-600",
    },
  ];

  const performanceMetrics = [
    { name: "Security Performance", value: 98.7, color: "red" },
    { name: "Trading Performance", value: 94.3, color: "green" },
    { name: "Bridge Performance", value: 97.8, color: "blue" },
    { name: "System Performance", value: 96.2, color: "purple" },
  ];

  const moduleUsage = [
    { module: "Security Operations", usage: 89, users: 234 },
    { module: "AI Trading", usage: 76, users: 189 },
    { module: "Bridge Network", usage: 82, users: 156 },
    { module: "Analytics", usage: 67, users: 98 },
    { module: "Computing", usage: 45, users: 67 },
    { module: "Monitoring", usage: 91, users: 278 },
  ];

  return (
    <PageLayout variant="analytics">
      <PageHeader
        title="Enterprise Analytics Platform"
        description="Advanced business intelligence and reporting"
        icon={BarChart3}
        iconGradient="from-blue-500 to-purple-600"
        borderColor="border-blue-400/30"
      />
      {/* Analytics Navigation */}
      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4 max-w-2xl">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="risk">Risk Analysis</TabsTrigger>
          <TabsTrigger value="reports">Custom Reports</TabsTrigger>
        </TabsList>

        {/* Executive Overview */}
        <TabsContent value="overview" className="space-y-6">
          {/* Key Performance Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {kpis.map((kpi) => (
              <Card key={kpi.title}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      {kpi.title}
                    </CardTitle>
                    <kpi.icon className={`h-4 w-4 ${kpi.color}`} />
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div className="text-2xl font-bold">{kpi.value}</div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="secondary" className="text-xs">
                        {kpi.change}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {kpi.period}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Revenue Trends and Geographic Distribution */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Revenue Trends */}
            <Card className="relative overflow-hidden">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Revenue Trends</span>
                </CardTitle>
                <CardDescription>
                  Multi-module revenue performance over time
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <EnhancedLineChart
                    data={[
                      { time: "Jan", trading: 2.1, security: 1.5, bridge: 0.8 },
                      { time: "Feb", trading: 2.3, security: 1.7, bridge: 0.9 },
                      { time: "Mar", trading: 2.0, security: 1.8, bridge: 1.1 },
                      { time: "Apr", trading: 2.5, security: 1.6, bridge: 1.0 },
                      { time: "May", trading: 2.7, security: 1.9, bridge: 1.2 },
                      {
                        time: "Jun",
                        trading: 2.34,
                        security: 1.87,
                        bridge: 1.1,
                      },
                    ]}
                    lines={[
                      { dataKey: "trading", color: "#22c55e", name: "Trading" },
                      {
                        dataKey: "security",
                        color: "#3b82f6",
                        name: "Security",
                      },
                      { dataKey: "bridge", color: "#a855f7", name: "Bridge" },
                    ]}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Geographic Distribution */}
            <Card className="relative overflow-hidden">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Globe className="h-5 w-5" />
                  <span>Geographic Distribution</span>
                </CardTitle>
                <CardDescription>User distribution by region</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <EnhancedDonutChart
                    data={[
                      { name: "Americas", value: 45, color: "#3b82f6" },
                      { name: "Europe", value: 32, color: "#8b5cf6" },
                      { name: "Asia", value: 23, color: "#22c55e" },
                    ]}
                    innerRadius={60}
                    outerRadius={100}
                  />
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="text-center">
                      <div className="text-2xl font-bold">100%</div>
                      <div className="text-sm text-muted-foreground">
                        Global Coverage
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Feature Utilization */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Users className="h-5 w-5" />
                <span>Module Utilization</span>
              </CardTitle>
              <CardDescription>
                Usage statistics across all Scorpius X modules
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {moduleUsage.map((item) => (
                  <div key={item.module} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="font-medium">{item.module}</span>
                      <div className="flex items-center space-x-4">
                        <span className="text-sm text-muted-foreground">
                          {item.users} users
                        </span>
                        <span className="font-bold">{item.usage}%</span>
                      </div>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-800 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-indigo-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${item.usage}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Analytics */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Metrics */}
            <Card className="relative overflow-hidden">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <BarChart3 className="h-5 w-5" />
                  <span>Module Performance</span>
                </CardTitle>
                <CardDescription>
                  Performance scores across all modules
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <EnhancedRadialChart
                    data={performanceMetrics.map((metric) => ({
                      name: metric.name,
                      value: metric.value,
                      color:
                        metric.color === "red"
                          ? "#ef4444"
                          : metric.color === "green"
                            ? "#22c55e"
                            : metric.color === "blue"
                              ? "#3b82f6"
                              : "#8b5cf6",
                    }))}
                    innerRadius={40}
                    outerRadius={80}
                  />
                </div>
              </CardContent>
            </Card>

            {/* Trading Performance Deep Dive */}
            <Card className="relative overflow-hidden">
              <CardHeader>
                <CardTitle>Trading Performance Analysis</CardTitle>
                <CardDescription>
                  Detailed trading metrics and strategy performance
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <EnhancedComposedChart
                    data={[
                      { name: "Q1", profit: 2.1, trades: 45, volume: 125 },
                      { name: "Q2", profit: 2.3, trades: 52, volume: 142 },
                      { name: "Q3", profit: 2.0, trades: 48, volume: 138 },
                      { name: "Q4", profit: 2.34, trades: 56, volume: 156 },
                    ]}
                    bars={[
                      { dataKey: "trades", color: "#3b82f6", name: "Trades" },
                    ]}
                    lines={[
                      {
                        dataKey: "profit",
                        color: "#22c55e",
                        name: "Profit (ETH)",
                      },
                      { dataKey: "volume", color: "#f59e0b", name: "Volume" },
                    ]}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Risk Analysis */}
        <TabsContent value="risk" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Risk Analytics Dashboard</CardTitle>
              <CardDescription>
                Comprehensive risk assessment across all modules
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center py-12">
              <BarChart3 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">
                Risk Analysis Center
              </h3>
              <p className="text-muted-foreground mb-4">
                Advanced risk metrics, stress testing, and scenario analysis
                tools.
              </p>
              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <div className="font-bold text-green-600">Low</div>
                  <div className="text-muted-foreground">Overall Risk</div>
                </div>
                <div>
                  <div className="font-bold text-blue-600">97.2%</div>
                  <div className="text-muted-foreground">Risk Coverage</div>
                </div>
                <div>
                  <div className="font-bold text-purple-600">A+</div>
                  <div className="text-muted-foreground">Risk Score</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Custom Reports */}
        <TabsContent value="reports" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Custom Report Builder</CardTitle>
              <CardDescription>
                Create and schedule custom analytics reports
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center py-12">
              <PieChart className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">
                Report Builder Interface
              </h3>
              <p className="text-muted-foreground mb-4">
                Drag-and-drop report builder with widget library and custom data
                sources.
              </p>
              <div className="flex justify-center space-x-4">
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Create Report
                </Button>
                <Button>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Schedule Report
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </PageLayout>
  );
};

export default Analytics;
