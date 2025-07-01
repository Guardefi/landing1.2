import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { usePersistedStats } from "@/hooks/usePersistedStats";
import { apiService, useBackendStatus } from "@/lib/api-integration";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { PageLayout } from "@/components/PageLayout";
import { PageHeader } from "@/components/PageHeader";
import {
  Shield,
  Globe,
  Brain,
  TrendingUp,
  Server,
  Activity,
  AlertTriangle,
  AlertOctagon,
  Search,
  Target,
  Database,
  RefreshCw,
  Zap,
  Building2,
  Eye,
  BarChart3,
  Cpu,
} from "lucide-react";

const Index = () => {
  const { stats } = usePersistedStats();
  const { isAvailable: backendAvailable } = useBackendStatus();
  const [dashboardStats, setDashboardStats] = useState(null);

  useEffect(() => {
    const loadDashboardStats = async () => {
      const data = await apiService.getDashboardStats();
      setDashboardStats(data);
    };

    loadDashboardStats();
  }, []);

  // Hero metrics data - use backend data when available, fallback to persistent storage
  const threatsBlocked =
    dashboardStats?.threatsBlocked ?? stats.scanStats.threatsDetected;
  const tradingProfit =
    dashboardStats?.tradingProfit ?? stats.tradingStats.totalProfit;
  const activeScans = dashboardStats?.activeScans ?? stats.scanStats.totalScans;
  const networkUptime = dashboardStats?.networkUptime ?? 0;

  const heroMetrics = [
    {
      title: "Threats Blocked",
      value: threatsBlocked.toLocaleString(),
      trend: threatsBlocked > 0 ? "+12.5%" : "0%",
      icon: Shield,
      color: "bg-gradient-to-br from-red-500/20 to-red-600/10",
      borderColor: "border-red-200 dark:border-red-800",
      iconColor: "text-red-600",
      features: ["Real-time detection", "99.9% accuracy"],
      link: "/security/elite",
    },
    {
      title: "Trading Profit",
      value: `$${tradingProfit.toFixed(1)}${tradingProfit >= 1000 ? "K" : ""}`,
      trend: tradingProfit > 0 ? "+23.8%" : "0%",
      icon: TrendingUp,
      color: "bg-gradient-to-br from-green-500/20 to-green-600/10",
      borderColor: "border-green-200 dark:border-green-800",
      iconColor: "text-green-600",
      features: ["AI-powered trades", "Success rate: 94.2%"],
      link: "/trading/ai",
    },
    {
      title: "Active Scans",
      value: activeScans.toLocaleString(),
      trend: activeScans > 0 ? "+8.1%" : "0%",
      icon: Search,
      color: "bg-gradient-to-br from-blue-500/20 to-blue-600/10",
      borderColor: "border-blue-200 dark:border-blue-800",
      iconColor: "text-blue-600",
      features: ["Multi-chain support", "Deep analysis"],
      link: "/scanner",
    },
    {
      title: "Network Uptime",
      value: networkUptime > 0 ? `${networkUptime.toFixed(2)}%` : "0%",
      trend: networkUptime > 0 ? "+0.02%" : "0%",
      icon: Globe,
      color: "bg-gradient-to-br from-purple-500/20 to-purple-600/10",
      borderColor: "border-purple-200 dark:border-purple-800",
      iconColor: "text-purple-600",
      features: ["24/7 monitoring", "Auto-scaling"],
      link: "/monitoring",
    },
  ];

  const serviceCards = [
    {
      title: "Security Elite",
      description: "Advanced threat detection and prevention",
      icon: Shield,
      status: "active",
      link: "/security/elite",
      metrics: {
        threats: threatsBlocked,
        accuracy: threatsBlocked > 0 ? "99.9%" : "0%",
      },
    },
    {
      title: "Trading AI",
      description: "Intelligent trading algorithms",
      icon: Brain,
      status: "active",
      link: "/trading/ai",
      metrics: {
        profit: `$${tradingProfit.toFixed(1)}${tradingProfit >= 1000 ? "K" : ""}`,
        success: tradingProfit > 0 ? "94.2%" : "0%",
      },
    },
    {
      title: "Bridge Network",
      description: "Cross-chain bridge monitoring",
      icon: Building2,
      status: "active",
      link: "/bridge",
      metrics: { bridges: 0, volume: "$0" },
    },
    {
      title: "Smart Scanner",
      description: "Contract vulnerability analysis",
      icon: Search,
      status: "active",
      link: "/scanner",
      metrics: { scans: activeScans, critical: threatsBlocked },
    },
    {
      title: "Mempool Monitor",
      description: "Real-time transaction monitoring",
      icon: Activity,
      status: "active",
      link: "/mempool",
      metrics: { txs: "0/s", pending: 0 },
    },
    {
      title: "Analytics Hub",
      description: "Data analysis and reporting",
      icon: BarChart3,
      status: "active",
      link: "/analytics",
      metrics: { reports: dashboardStats?.totalReports ?? 0, insights: 0 },
    },
  ];

  return (
    <PageLayout>
      <div className="space-y-8">
        <PageHeader
          title="Scorpius Enterprise Platform"
          description="Your comprehensive blockchain security and trading platform"
          icon={Shield}
        />

        {/* Backend Status Alert */}
        {!backendAvailable && (
          <Alert className="border-orange-200 bg-orange-50">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              Backend services are offline. Displaying cached data from local
              storage. Some features may be limited.
            </AlertDescription>
          </Alert>
        )}

        {/* Hero Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {heroMetrics.map((metric, index) => (
            <Link key={index} to={metric.link}>
              <Card
                className={`hover:shadow-lg transition-all duration-300 ${metric.borderColor} ${metric.color}`}
              >
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {metric.title}
                  </CardTitle>
                  <metric.icon className={`h-4 w-4 ${metric.iconColor}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metric.value}</div>
                  <div className="flex items-center space-x-2 text-xs text-muted-foreground mt-1">
                    <span className="text-green-600 font-medium">
                      {metric.trend}
                    </span>
                    <span>from last month</span>
                  </div>
                  <div className="mt-3 space-y-1">
                    {metric.features.map((feature, idx) => (
                      <Badge key={idx} className="text-xs mr-1">
                        {feature}
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {/* Service Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {serviceCards.map((service, index) => (
            <Link key={index} to={service.link}>
              <Card className="hover:shadow-lg transition-all duration-300 border-border/50 hover:border-border">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <div>
                    <CardTitle className="text-lg">{service.title}</CardTitle>
                    <CardDescription className="mt-1">
                      {service.description}
                    </CardDescription>
                  </div>
                  <div className="flex flex-col items-center space-y-2">
                    <service.icon className="h-8 w-8 text-primary" />
                    <Badge className="text-xs">{service.status}</Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {Object.entries(service.metrics).map(([key, value]) => (
                      <div key={key} className="flex flex-col">
                        <span className="text-muted-foreground capitalize">
                          {key}
                        </span>
                        <span className="font-semibold">{value}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5" />
              <span>Quick Actions</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Button
                asChild
                className="h-20 flex-col space-y-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground"
              >
                <Link to="/scanner">
                  <Search className="h-6 w-6" />
                  <span>New Scan</span>
                </Link>
              </Button>
              <Button
                asChild
                className="h-20 flex-col space-y-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground"
              >
                <Link to="/trading/ai">
                  <TrendingUp className="h-6 w-6" />
                  <span>Start Trading</span>
                </Link>
              </Button>
              <Button
                asChild
                className="h-20 flex-col space-y-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground"
              >
                <Link to="/reports">
                  <BarChart3 className="h-6 w-6" />
                  <span>View Reports</span>
                </Link>
              </Button>
              <Button
                asChild
                className="h-20 flex-col space-y-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground"
              >
                <Link to="/simulation">
                  <Target className="h-6 w-6" />
                  <span>Simulation</span>
                </Link>
              </Button>
              <Button
                asChild
                className="h-20 flex-col space-y-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground"
              >
                <Link to="/settings">
                  <Server className="h-6 w-6" />
                  <span>Settings</span>
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* System Status */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>System Status</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div
                    className={`w-3 h-3 rounded-full ${
                      backendAvailable ? "bg-green-500" : "bg-red-500"
                    }`}
                  ></div>
                  <span>Backend Services</span>
                </div>
                <Badge
                  className={
                    backendAvailable
                      ? "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200"
                      : "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                  }
                >
                  {backendAvailable ? "Operational" : "Offline"}
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span>Security Scanners</span>
                </div>
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  Online
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span>Trading Engine</span>
                </div>
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  Active
                </Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span>Monitoring</span>
                </div>
                <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                  Partial
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageLayout>
  );
};

export default Index;
