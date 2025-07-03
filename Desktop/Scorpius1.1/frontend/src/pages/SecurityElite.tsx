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
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import { MetricsCard } from "@/components/MetricsCard";
import { ActivityFeed } from "@/components/ActivityFeed";
import { useSecurityMonitoring } from "@/hooks";
import {
  ErrorBoundary,
  ModuleLoadingWrapper,
  ConnectionStatus,
} from "@/components/ui/error-boundary";
import {
  Shield,
  AlertTriangle,
  Eye,
  Brain,
  Activity,
  Zap,
  AlertOctagon,
  CheckCircle2,
  Clock,
  Settings,
} from "lucide-react";

const SecurityElite = () => {
  const [currentTime, setCurrentTime] = useState(new Date());

  // Real-time API integration
  const {
    threats,
    metrics,
    isConnected,
    error: securityError,
    mitigateThreat,
  } = useSecurityMonitoring();

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const securityMetrics = [
    {
      title: "Detection Rate",
      value: "99.7%",
      change: "+0.2%",
      period: "vs target 99.5%",
      icon: Eye,
      variant: "positive" as const,
    },
    {
      title: "Response Time",
      value: "2.3s",
      change: "-0.5s",
      period: "avg response",
      icon: Zap,
      variant: "positive" as const,
    },
    {
      title: "False Positives",
      value: "0.8%",
      change: "-0.2%",
      period: "target <2%",
      icon: CheckCircle2,
      variant: "positive" as const,
    },
    {
      title: "Coverage",
      value: "98.9%",
      change: "+1.4%",
      period: "target >95%",
      icon: Shield,
      variant: "positive" as const,
    },
  ];

  const threatLevels = [
    { level: "Critical", count: 0, color: "destructive" },
    { level: "High", count: 3, color: "destructive" },
    { level: "Medium", count: 12, color: "default" },
    { level: "Low", count: 45, color: "secondary" },
  ];

  const recentActivities = [
    {
      id: "THR-001",
      type: "security",
      icon: Shield,
      iconColor: "text-red-500",
      message: "DDoS Attack blocked from 185.220.101.42",
      time: "2 min ago",
      severity: "error" as const,
    },
    {
      id: "THR-002",
      type: "security",
      icon: AlertTriangle,
      iconColor: "text-amber-500",
      message: "Malware Detection: suspicious file quarantined",
      time: "5 min ago",
      severity: "warning" as const,
    },
    {
      id: "THR-003",
      type: "security",
      icon: Eye,
      iconColor: "text-blue-500",
      message: "Suspicious Login attempt from 192.168.1.100",
      time: "8 min ago",
      severity: "warning" as const,
    },
    {
      id: "THR-004",
      type: "security",
      icon: CheckCircle2,
      iconColor: "text-green-500",
      message: "Security scan completed: no threats detected",
      time: "12 min ago",
      severity: "success" as const,
    },
  ];

  return (
    <PageLayout variant="security">
      <PageHeader
        title="Security Operations Center"
        description="Elite threat detection and response"
        icon={Shield}
        currentTime={currentTime}
      />

      {/* Alert Banner */}
      <div className="mb-6 p-4 bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-200 dark:border-amber-800 rounded-lg">
        <div className="flex items-center space-x-2">
          <AlertTriangle className="h-5 w-5 text-amber-600" />
          <span className="font-medium text-amber-800 dark:text-amber-200">
            3 high-priority threats detected in the last hour - All threats
            contained
          </span>
        </div>
      </div>

      {/* Security Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {securityMetrics.map((metric) => (
          <MetricsCard
            key={metric.title}
            title={metric.title}
            value={metric.value}
            change={metric.change}
            period={metric.period}
            icon={metric.icon}
            variant={metric.variant}
          />
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Threat Map */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Eye className="h-5 w-5" />
              <span>Global Threat Map</span>
            </CardTitle>
            <CardDescription>
              Real-time threat visualization across all monitored networks
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="relative h-80 bg-gradient-to-br from-slate-900 to-red-900 rounded-lg overflow-hidden">
              {/* 3D Globe with Threats */}
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="relative">
                  <div className="w-56 h-56 rounded-full bg-gradient-to-br from-red-600/20 to-orange-600/20 border-2 border-red-400/50 animate-pulse">
                    <div className="absolute inset-6 rounded-full bg-gradient-to-br from-red-500/30 to-orange-500/30 border border-red-300/30">
                      {/* Active threat markers */}
                      <div className="absolute top-4 left-8 w-4 h-4 bg-red-500 rounded-full animate-ping">
                        <div className="absolute inset-1 bg-red-600 rounded-full" />
                      </div>
                      <div className="absolute top-12 right-6 w-3 h-3 bg-amber-500 rounded-full animate-pulse" />
                      <div className="absolute bottom-8 left-12 w-3 h-3 bg-orange-500 rounded-full animate-pulse" />
                      <div className="absolute bottom-4 right-10 w-2 h-2 bg-red-400 rounded-full animate-ping" />
                      {/* Defensive grid */}
                      <div className="absolute inset-0 border-2 border-blue-400/30 rounded-full animate-spin-slow" />
                    </div>
                  </div>
                </div>
              </div>
              {/* Threat statistics */}
              <div className="absolute bottom-4 left-4 space-y-2 text-white">
                <div className="text-lg font-bold">Active Threats: 3</div>
                <div className="text-sm opacity-80">
                  Monitoring 847 endpoints
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Threat Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5" />
              <span>Threat Summary</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {threatLevels.map((threat) => (
                <div
                  key={threat.level}
                  className="flex items-center justify-between"
                >
                  <span className="text-sm font-medium">{threat.level}</span>
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl font-bold">{threat.count}</span>
                    <Badge variant={threat.color as any}>
                      {threat.level.toLowerCase()}
                    </Badge>
                  </div>
                </div>
              ))}
              <div className="pt-4 border-t">
                <div className="text-center">
                  <div className="text-3xl font-bold text-emerald-600 mb-1">
                    A+
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Security Score
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* AI Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Brain className="h-5 w-5" />
              <span>AI Analysis</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  94.7%
                </div>
                <div className="text-sm text-muted-foreground">
                  Detection Confidence
                </div>
              </div>
              <div className="space-y-2">
                <div className="text-sm font-medium">Pattern Recognition</div>
                <Progress value={89} className="h-2" />
                <div className="text-xs text-muted-foreground">
                  12 attack patterns identified
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quantum Security */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Zap className="h-5 w-5" />
              <span>Quantum Security</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600 mb-1">
                  Level 5
                </div>
                <div className="text-sm text-muted-foreground">
                  Quantum Resistance
                </div>
              </div>
              <div className="space-y-2 text-xs">
                <div className="flex justify-between">
                  <span>Kyber</span>
                  <Badge variant="secondary">Active</Badge>
                </div>
                <div className="flex justify-between">
                  <span>Dilithium</span>
                  <Badge variant="secondary">Active</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Shield className="h-5 w-5" />
              <span>Quick Actions</span>
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start bg-gradient-to-r from-red-600 to-red-700 text-white">
              <AlertOctagon className="h-4 w-4 mr-2" />
              Emergency Lockdown
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Eye className="h-4 w-4 mr-2" />
              Full System Scan
            </Button>
            <Button variant="outline" className="w-full justify-start">
              <Brain className="h-4 w-4 mr-2" />
              AI Analysis Report
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Activity Feed */}
      <ActivityFeed
        title="Recent Threat Activity"
        description="Latest security events and response actions"
        activities={recentActivities}
      />
    </PageLayout>
  );
};

export default SecurityElite;
