import React from "react";
import { Link } from "react-router-dom";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
  Database,
  RefreshCw,
  Zap,
  Building2,
  Eye,
  BarChart3,
  Cpu,
} from "lucide-react";

const Index = () => {
  // Hero metrics data
  const heroMetrics = [
    {
      title: "Threats Blocked",
      value: "1,247",
      trend: "+12.5%",
      icon: Shield,
      color: "bg-gradient-to-br from-red-500/20 to-red-600/10",
      borderColor: "border-red-200 dark:border-red-800",
      iconColor: "text-red-600",
      features: ["Real-time detection", "99.9% accuracy"],
      link: "/security/elite",
    },
    {
      title: "Trading Profit",
      value: "$47.2K",
      trend: "+23.8%",
      icon: TrendingUp,
      color: "bg-gradient-to-br from-green-500/20 to-green-600/10",
      borderColor: "border-green-200 dark:border-green-800",
      iconColor: "text-green-600",
      features: ["AI-powered trades", "Success rate: 94.2%"],
      link: "/trading/ai",
    },
    {
      title: "Active Scans",
      value: "342",
      trend: "+8.1%",
      icon: Search,
      color: "bg-gradient-to-br from-blue-500/20 to-blue-600/10",
      borderColor: "border-blue-200 dark:border-blue-800",
      iconColor: "text-blue-600",
      features: ["Multi-chain support", "Deep analysis"],
      link: "/scanner",
    },
    {
      title: "Network Uptime",
      value: "99.97%",
      trend: "+0.02%",
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
      metrics: { threats: 1247, accuracy: "99.9%" },
    },
    {
      title: "Trading AI",
      description: "Intelligent trading algorithms",
      icon: Brain,
      status: "active",
      link: "/trading/ai",
      metrics: { profit: "$47.2K", success: "94.2%" },
    },
    {
      title: "Bridge Network",
      description: "Cross-chain bridge monitoring",
      icon: Building2,
      status: "active",
      link: "/bridge",
      metrics: { bridges: 45, volume: "$2.1M" },
    },
    {
      title: "Smart Scanner",
      description: "Contract vulnerability analysis",
      icon: Search,
      status: "active",
      link: "/scanner",
      metrics: { scans: 342, critical: 12 },
    },
    {
      title: "Mempool Monitor",
      description: "Real-time transaction monitoring",
      icon: Activity,
      status: "active",
      link: "/mempool",
      metrics: { txs: "1.2K/s", pending: 847 },
    },
    {
      title: "Analytics Hub",
      description: "Data analysis and reporting",
      icon: BarChart3,
      status: "active",
      link: "/analytics",
      metrics: { reports: 156, insights: 89 },
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

        {/* Hero Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {heroMetrics.map((metric, index) => (
            <Link key={index} to={metric.link}>
              <Card className={`hover:shadow-lg transition-all duration-300 ${metric.borderColor} ${metric.color}`}>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {metric.title}
                  </CardTitle>
                  <metric.icon className={`h-4 w-4 ${metric.iconColor}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{metric.value}</div>
                  <div className="flex items-center space-x-2 text-xs text-muted-foreground mt-1">
                    <span className="text-green-600 font-medium">{metric.trend}</span>
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
                    <Badge 
                      className="text-xs"
                    >
                      {service.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    {Object.entries(service.metrics).map(([key, value]) => (
                      <div key={key} className="flex flex-col">
                        <span className="text-muted-foreground capitalize">{key}</span>
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
              <Button asChild className="h-20 flex-col space-y-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground">
                <Link to="/scanner">
                  <Search className="h-6 w-6" />
                  <span>New Scan</span>
                </Link>
              </Button>
              <Button asChild className="h-20 flex-col space-y-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground">
                <Link to="/trading/ai">
                  <TrendingUp className="h-6 w-6" />
                  <span>Start Trading</span>
                </Link>
              </Button>
              <Button asChild className="h-20 flex-col space-y-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground">
                <Link to="/reports">
                  <BarChart3 className="h-6 w-6" />
                  <span>View Reports</span>
                </Link>
              </Button>
              <Button asChild className="h-20 flex-col space-y-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground">
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
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span>Backend Services</span>
                </div>
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Operational</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span>Security Scanners</span>
                </div>
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Online</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span>Trading Engine</span>
                </div>
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Active</Badge>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                  <span>Monitoring</span>
                </div>
                <Badge className="bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">Partial</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </PageLayout>
  );
};

export default Index;
