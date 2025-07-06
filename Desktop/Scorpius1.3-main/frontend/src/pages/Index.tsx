import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { useDashboardData } from "@/hooks/useDashboardData";
import {
  Shield,
  Activity,
  BarChart3,
  Server,
  Database,
  Network,
  Brain,
  Globe,
  Search,
  TrendingUp,
  Eye,
  Clock,
  Users,
  Zap,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  GrafanaBoardGrid,
  defaultGrafanaBoards,
} from "@/components/GrafanaBoardGrid";
import { PageLayout } from "@/components/PageLayout";
import { Link } from "react-router-dom";

const Index = () => {
  // Real-time dashboard data
  const {
    systemHealth,
    dashboardMetrics,
    securityMetrics,
    performanceMetrics,
    recentScans,
    isLoading,
    isConnected,
    refreshAll,
  } = useDashboardData();

  // Calculate system stats from API data
  const systemStats = {
    totalScans: dashboardMetrics?.totalScans || 0,
    activeTrades: dashboardMetrics?.activeTrades || 0,
    systemUptime: performanceMetrics?.systemUptime || "0%",
    threatLevel: securityMetrics?.currentThreatLevel || "Unknown",
    lastUpdate: new Date().toISOString(),
  };

  // Top priority dashboards for command center
  const commandCenterBoards = defaultGrafanaBoards
    .filter((board) => board.priority <= 4)
    .map((board) => ({ ...board, height: 350 }));

  const quickStats = [
    {
      title: "System Health",
      value: systemStats.systemUptime,
      icon: Activity,
      color: "text-green-400",
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/20",
    },
    {
      title: "Active Scans",
      value: systemStats.totalScans.toLocaleString(),
      icon: Search,
      color: "text-cyan-400",
      bgColor: "bg-cyan-500/10",
      borderColor: "border-cyan-500/20",
    },
    {
      title: "AI Trades",
      value: systemStats.activeTrades,
      icon: Brain,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/20",
    },
    {
      title: "Threat Level",
      value: systemStats.threatLevel,
      icon: Shield,
      color:
        systemStats.threatLevel === "Low"
          ? "text-green-400"
          : "text-orange-400",
      bgColor:
        systemStats.threatLevel === "Low"
          ? "bg-green-500/10"
          : "bg-orange-500/10",
      borderColor:
        systemStats.threatLevel === "Low"
          ? "border-green-500/20"
          : "border-orange-500/20",
    },
  ];

  const modules = [
    {
      title: "Vulnerability Scanner",
      description: "AI-powered security analysis and threat detection",
      icon: Search,
      color: "text-red-400",
      bgColor: "bg-red-500/10",
      borderColor: "border-red-500/20",
      path: "/scanner",
      status: "active",
    },
    {
      title: "AI Trading Engine",
      description: "Automated trading strategies and market analysis",
      icon: Brain,
      color: "text-green-400",
      bgColor: "bg-green-500/10",
      borderColor: "border-green-500/20",
      path: "/trading/ai",
      status: "active",
    },
    {
      title: "Bridge Network",
      description: "Cross-chain operations and monitoring",
      icon: Globe,
      color: "text-purple-400",
      bgColor: "bg-purple-500/10",
      borderColor: "border-purple-500/20",
      path: "/bridge/network",
      status: "active",
    },
    {
      title: "Security Operations",
      description: "Real-time threat detection and response",
      icon: Shield,
      color: "text-orange-400",
      bgColor: "bg-orange-500/10",
      borderColor: "border-orange-500/20",
      path: "/security/elite",
      status: "active",
    },
    {
      title: "Analytics Platform",
      description: "Business intelligence and data visualization",
      icon: BarChart3,
      color: "text-blue-400",
      bgColor: "bg-blue-500/10",
      borderColor: "border-blue-500/20",
      path: "/analytics/enterprise",
      status: "active",
    },
    {
      title: "Grafana Monitoring",
      description: "Real-time dashboards and system metrics",
      icon: Activity,
      color: "text-amber-400",
      bgColor: "bg-amber-500/10",
      borderColor: "border-amber-500/20",
      path: "/monitoring/grafana",
      status: "active",
    },
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setSystemStats((prev) => ({
        ...prev,
        totalScans: prev.totalScans + Math.floor(Math.random() * 3),
        activeTrades: Math.max(
          1,
          prev.activeTrades + Math.floor(Math.random() * 5) - 2,
        ),
        lastUpdate: new Date().toISOString(),
      }));
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  return (
    <PageLayout>
      <div className="min-h-screen bg-background">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-br from-slate-900 via-slate-800 to-cyan-900/20 border-b border-cyan-400/20 mb-8"
        >
          <div className="container mx-auto px-6 py-12">
            <div className="flex items-center gap-4 mb-6">
              <div className="p-3 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg">
                <Shield className="h-10 w-10 text-white" />
              </div>
              <div>
                <h1 className="text-4xl font-bold text-white mb-2">
                  Scorpius Command Center
                </h1>
                <p className="text-xl text-gray-300">
                  Real-time security operations and system monitoring
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                <span>All systems operational</span>
              </div>
              <span>•</span>
              <span>Last updated: {new Date().toLocaleTimeString()}</span>
            </div>
          </div>
        </motion.div>

        <div className="container mx-auto px-6 space-y-8">
          {/* Quick Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
              {quickStats.map((stat, index) => (
                <motion.div
                  key={stat.title}
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 0.1 + index * 0.05 }}
                >
                  <Card
                    className={`${stat.bgColor} ${stat.borderColor} border hover:border-opacity-60 transition-all duration-300`}
                  >
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm text-muted-foreground">
                            {stat.title}
                          </p>
                          <p className={`text-2xl font-bold ${stat.color}`}>
                            {stat.value}
                          </p>
                        </div>
                        <stat.icon className={`h-8 w-8 ${stat.color}`} />
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Main Content Tabs */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <Tabs defaultValue="dashboards" className="w-full">
              <TabsList className="grid w-full grid-cols-2 lg:grid-cols-3">
                <TabsTrigger value="dashboards">Live Dashboards</TabsTrigger>
                <TabsTrigger value="modules">System Modules</TabsTrigger>
                <TabsTrigger value="overview">System Overview</TabsTrigger>
              </TabsList>

              <TabsContent value="dashboards" className="space-y-6 mt-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold text-foreground">
                    Real-time Monitoring
                  </h2>
                  <Link to="/monitoring/grafana">
                    <Button
                      variant="outline"
                      className="border-cyan-500/30 hover:bg-cyan-500/10"
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      View All Dashboards
                    </Button>
                  </Link>
                </div>

                <GrafanaBoardGrid
                  boards={commandCenterBoards}
                  gridCols={2}
                  compact={true}
                  showControls={true}
                />
              </TabsContent>

              <TabsContent value="modules" className="space-y-6 mt-6">
                <h2 className="text-2xl font-bold text-foreground mb-6">
                  System Modules
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {modules.map((module, index) => (
                    <motion.div
                      key={module.title}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                    >
                      <Link to={module.path}>
                        <Card
                          className={`${module.bgColor} ${module.borderColor} border hover:border-opacity-60 transition-all duration-300 hover:scale-105`}
                        >
                          <CardHeader className="pb-4">
                            <div className="flex items-center justify-between">
                              <module.icon
                                className={`h-8 w-8 ${module.color}`}
                              />
                              <Badge
                                variant={
                                  module.status === "active"
                                    ? "default"
                                    : "secondary"
                                }
                                className="text-xs"
                              >
                                {module.status}
                              </Badge>
                            </div>
                          </CardHeader>
                          <CardContent>
                            <h3
                              className={`text-lg font-semibold ${module.color} mb-2`}
                            >
                              {module.title}
                            </h3>
                            <p className="text-sm text-muted-foreground">
                              {module.description}
                            </p>
                          </CardContent>
                        </Card>
                      </Link>
                    </motion.div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="overview" className="space-y-6 mt-6">
                <h2 className="text-2xl font-bold text-foreground mb-6">
                  System Overview
                </h2>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <Card className="bg-background/50 backdrop-blur border-cyan-500/20">
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Activity className="h-5 w-5 text-cyan-400" />
                        <span>System Health</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          Overall Status
                        </span>
                        <div className="flex items-center space-x-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          <span className="text-green-500 font-medium">
                            Operational
                          </span>
                        </div>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          Uptime
                        </span>
                        <span className="text-green-500 font-medium">
                          {systemStats.systemUptime}
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          Last Incident
                        </span>
                        <span className="text-muted-foreground">
                          None in 30 days
                        </span>
                      </div>
                    </CardContent>
                  </Card>

                  <Card className="bg-background/50 backdrop-blur border-cyan-500/20">
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <TrendingUp className="h-5 w-5 text-blue-400" />
                        <span>Performance Metrics</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          Response Time
                        </span>
                        <span className="text-blue-400 font-medium">
                          45ms avg
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          Throughput
                        </span>
                        <span className="text-blue-400 font-medium">
                          1.2k req/sec
                        </span>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">
                          Error Rate
                        </span>
                        <span className="text-green-500 font-medium">
                          0.01%
                        </span>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>
            </Tabs>
          </motion.div>
        </div>
      </div>
    </PageLayout>
  );
};

export default Index;
