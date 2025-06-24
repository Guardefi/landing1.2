import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { ScrollArea } from '../components/ui/scroll-area';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../components/ui/dialog';
import { Alert, AlertDescription } from '../components/ui/alert';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  Search,
  FileText,
  Clock,
  AlertTriangle,
  Shield,
  Eye,
  Download,
  Filter,
  Zap,
  Hash,
  Link,
  Network,
  Users,
  DollarSign,
  TrendingUp,
  Archive,
  Database,
  Fingerprint,
  ScanLine,
  Target,
  Activity,
  MapPin,
  Calendar,
  Copy,
  ExternalLink,
  Play,
  Pause,
  RefreshCw,
  Plus,
  CheckCircle,
  XCircle,
  Info,
  BarChart3,
  Brain,
  Loader2,
} from 'lucide-react';

import { useForensicsEngine } from '../hooks/useForensicsEngine';
import {
  RiskLevel,
  ForensicsEventType,
  ComplianceStandard,
  AddressInvestigationRequest,
} from '../services/forensicsApi';

const CHART_COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

export default function DigitalForensics() {
  const {
    alerts,
    cases,
    statistics,
    investigations,
    patterns,
    loading,
    error,
    monitoring,

    // Functions
    investigateAddress,
    createCase,
    refreshAlerts,
    refreshStatistics,
    detectPatterns,
    checkCompliance,
    runAIAnalysis,
    startMonitoring,
    stopMonitoring,
    getRiskLevelColor,
    getRiskLevelLabel,
    clearError,
    refreshAllData,
  } = useForensicsEngine();

  const [activeTab, setActiveTab] = useState('overview');
  const [searchAddress, setSearchAddress] = useState('');
  const [investigationDepth, setInvestigationDepth] = useState(3);
  const [selectedAlert, setSelectedAlert] = useState<string | null>(null);
  const [newCaseTitle, setNewCaseTitle] = useState('');
  const [newCaseDescription, setNewCaseDescription] = useState('');
  const [investigator, setInvestigator] = useState('forensics_team');
  const [aiAnalysisType, setAiAnalysisType] = useState('full_analysis');

  // Handle address investigation
  const handleInvestigateAddress = async () => {
    if (!searchAddress.trim()) return;

    const request: AddressInvestigationRequest = {
      address: searchAddress,
      depth: investigationDepth,
    };

    await investigateAddress(request);
  };

  // Handle case creation
  const handleCreateCase = async () => {
    if (!newCaseTitle.trim() || !newCaseDescription.trim()) return;

    const caseId = await createCase({
      title: newCaseTitle,
      description: newCaseDescription,
      investigator,
      priority: RiskLevel.MEDIUM,
    });

    if (caseId) {
      setNewCaseTitle('');
      setNewCaseDescription('');
    }
  };

  // Handle AI analysis
  const handleAIAnalysis = async () => {
    if (!searchAddress.trim()) return;

    await runAIAnalysis({
      addresses: [searchAddress],
      analysis_type: aiAnalysisType as any,
    });
  };

  // Handle monitoring toggle
  const handleMonitoringToggle = async () => {
    if (monitoring.active) {
      await stopMonitoring();
    } else {
      if (searchAddress.trim()) {
        await startMonitoring({
          addresses: [searchAddress],
          alert_thresholds: {
            risk_score: 0.7,
            transaction_volume: 10000,
          },
          notification_channels: ['dashboard'],
        });
      }
    }
  };

  // Get risk level styling
  const getRiskStyling = (riskLevel: RiskLevel) => {
    switch (riskLevel) {
      case RiskLevel.LOW:
        return {
          color: 'text-green-500',
          bg: 'bg-green-100',
          variant: 'secondary' as const,
        };
      case RiskLevel.MEDIUM:
        return {
          color: 'text-yellow-500',
          bg: 'bg-yellow-100',
          variant: 'secondary' as const,
        };
      case RiskLevel.HIGH:
        return {
          color: 'text-orange-500',
          bg: 'bg-orange-100',
          variant: 'destructive' as const,
        };
      case RiskLevel.CRITICAL:
        return {
          color: 'text-red-500',
          bg: 'bg-red-100',
          variant: 'destructive' as const,
        };
      default:
        return {
          color: 'text-gray-500',
          bg: 'bg-gray-100',
          variant: 'outline' as const,
        };
    }
  };

  // Prepare chart data from statistics
  const alertDistributionData = statistics?.alert_distribution
    ? Object.entries(statistics.alert_distribution).map(([type, count]) => ({
        name: type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
        value: count,
      }))
    : [];

  const riskDistributionData = statistics?.risk_distribution
    ? Object.entries(statistics.risk_distribution).map(([level, count]) => ({
        level: level,
        count: count,
      }))
    : [];

  const complianceViolationsData = statistics?.compliance_violations_by_standard
    ? Object.entries(statistics.compliance_violations_by_standard).map(
        ([standard, count]) => ({
          standard: standard.replace(/_/g, ' ').toUpperCase(),
          violations: count,
        }),
      )
    : [];

  // Investigation timeline data
  const investigationTimelineData = Array.from({ length: 24 }, (_, i) => {
    const hour = new Date();
    hour.setHours(hour.getHours() - (23 - i));
    return {
      time: hour.getHours() + ':00',
      investigations: Math.floor(Math.random() * 10) + 1,
      alerts: alerts.filter(alert => {
        const alertTime = new Date(alert.timestamp);
        return alertTime.getHours() === hour.getHours();
      }).length,
      patterns: Math.floor(Math.random() * 5),
    };
  });

  useEffect(() => {
    refreshAllData();
  }, [refreshAllData]);

  return (
    <div className="p-6 space-y-6 bg-black min-h-screen text-white">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Digital Forensics</h1>
          <p className="text-muted-foreground">
            AI-powered blockchain forensics and investigation platform
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={refreshAllData}
            disabled={loading.general}
          >
            {loading.general ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Refresh
          </Button>
          <Button
            variant={monitoring.active ? 'destructive' : 'default'}
            size="sm"
            onClick={handleMonitoringToggle}
          >
            {monitoring.active ? (
              <>
                <Pause className="h-4 w-4 mr-2" />
                Stop Monitoring
              </>
            ) : (
              <>
                <Play className="h-4 w-4 mr-2" />
                Start Monitoring
              </>
            )}
          </Button>
          <Dialog>
            <DialogTrigger asChild>
              <Button size="sm">
                <Plus className="h-4 w-4 mr-2" />
                New Case
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-gray-900 text-white">
              <DialogHeader>
                <DialogTitle>Create Investigation Case</DialogTitle>
                <DialogDescription>
                  Start a new forensics investigation case
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4">
                <Input
                  placeholder="Case title"
                  value={newCaseTitle}
                  onChange={e => setNewCaseTitle(e.target.value)}
                />
                <Textarea
                  placeholder="Case description"
                  value={newCaseDescription}
                  onChange={e => setNewCaseDescription(e.target.value)}
                />
                <Input
                  placeholder="Investigator ID"
                  value={investigator}
                  onChange={e => setInvestigator(e.target.value)}
                />
                <Button onClick={handleCreateCase} disabled={loading.cases}>
                  {loading.cases ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4 mr-2" />
                  )}
                  Create Case
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Error Alerts */}
      {Object.entries(error).map(
        ([type, errorMsg]) =>
          errorMsg && (
            <Alert key={type} className="border-red-500 bg-red-950">
              <XCircle className="h-4 w-4" />
              <AlertDescription>
                {errorMsg}
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-2"
                  onClick={() => clearError(type as any)}
                >
                  Dismiss
                </Button>
              </AlertDescription>
            </Alert>
          ),
      )}

      {/* Statistics Overview */}
      {statistics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Cases</CardTitle>
              <Archive className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.active_cases}</div>
              <p className="text-xs text-muted-foreground">
                {statistics.total_cases} total cases
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">High Risk Alerts</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-500">
                {statistics.high_risk_alerts}
              </div>
              <p className="text-xs text-muted-foreground">
                {statistics.total_alerts} total alerts
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Patterns Detected</CardTitle>
              <Target className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{statistics.patterns_detected}</div>
              <p className="text-xs text-muted-foreground">
                Avg time: {statistics.average_investigation_time.toFixed(2)}s
              </p>
            </CardContent>
          </Card>

          <Card className="bg-gray-900 border-gray-800">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                Compliance Violations
              </CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-orange-500">
                {statistics.compliance_violations}
              </div>
              <p className="text-xs text-muted-foreground">
                {statistics.address_profiles} profiles analyzed
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="investigate">Investigate</TabsTrigger>
          <TabsTrigger value="alerts">Alerts</TabsTrigger>
          <TabsTrigger value="cases">Cases</TabsTrigger>
          <TabsTrigger value="patterns">Patterns</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Investigation Timeline */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Investigation Activity Timeline</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={investigationTimelineData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="time" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1f2937',
                        border: '1px solid #374151',
                        color: '#fff',
                      }}
                    />
                    <Legend />
                    <Line
                      type="monotone"
                      dataKey="investigations"
                      stroke="#8884d8"
                      name="Investigations"
                    />
                    <Line
                      type="monotone"
                      dataKey="alerts"
                      stroke="#82ca9d"
                      name="Alerts"
                    />
                    <Line
                      type="monotone"
                      dataKey="patterns"
                      stroke="#ffc658"
                      name="Patterns"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Alert Distribution */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Alert Type Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={alertDistributionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) =>
                        `${name} ${(percent * 100).toFixed(0)}%`
                      }
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {alertDistributionData.map((entry, index) => (
                        <Cell
                          key={`cell-${index}`}
                          fill={CHART_COLORS[index % CHART_COLORS.length]}
                        />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Risk Level Distribution */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Risk Level Distribution</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={riskDistributionData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="level" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1f2937',
                        border: '1px solid #374151',
                        color: '#fff',
                      }}
                    />
                    <Bar dataKey="count" fill="#8884d8" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* Compliance Violations */}
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Compliance Violations by Standard</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={complianceViolationsData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="standard" stroke="#9ca3af" />
                    <YAxis stroke="#9ca3af" />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: '#1f2937',
                        border: '1px solid #374151',
                        color: '#fff',
                      }}
                    />
                    <Bar dataKey="violations" fill="#ff7c7c" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Investigate Tab */}
        <TabsContent value="investigate" className="space-y-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle>Address Investigation</CardTitle>
              <div className="flex items-center space-x-4">
                <div className="flex-1">
                  <Input
                    placeholder="Enter blockchain address to investigate"
                    value={searchAddress}
                    onChange={e => setSearchAddress(e.target.value)}
                    className="bg-gray-800"
                  />
                </div>
                <Select
                  value={investigationDepth.toString()}
                  onValueChange={value => setInvestigationDepth(parseInt(value))}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Depth 1</SelectItem>
                    <SelectItem value="2">Depth 2</SelectItem>
                    <SelectItem value="3">Depth 3</SelectItem>
                    <SelectItem value="4">Depth 4</SelectItem>
                    <SelectItem value="5">Depth 5</SelectItem>
                  </SelectContent>
                </Select>
                <Button
                  onClick={handleInvestigateAddress}
                  disabled={loading.investigation || !searchAddress.trim()}
                >
                  {loading.investigation ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4 mr-2" />
                  )}
                  Investigate
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {searchAddress && investigations[searchAddress] && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <Card className="bg-gray-800">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Risk Score</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div
                          className={`text-2xl font-bold ${getRiskLevelColor(
                            investigations[searchAddress].profile.risk_score > 0.7
                              ? RiskLevel.HIGH
                              : RiskLevel.MEDIUM,
                          )}`}
                        >
                          {(investigations[searchAddress].risk_score * 100).toFixed(1)}%
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="bg-gray-800">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Anomalies</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold text-orange-500">
                          {investigations[searchAddress].anomalies.length}
                        </div>
                      </CardContent>
                    </Card>

                    <Card className="bg-gray-800">
                      <CardHeader className="pb-2">
                        <CardTitle className="text-sm">Patterns</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold text-blue-500">
                          {investigations[searchAddress].patterns.length}
                        </div>
                      </CardContent>
                    </Card>
                  </div>

                  {investigations[searchAddress].alerts.length > 0 && (
                    <Alert className="border-orange-500 bg-orange-950">
                      <AlertTriangle className="h-4 w-4" />
                      <AlertDescription>
                        Investigation generated{' '}
                        {investigations[searchAddress].alerts.length} alert(s). Review
                        in the Alerts tab.
                      </AlertDescription>
                    </Alert>
                  )}
                </div>
              )}
            </CardContent>
          </Card>

          {/* AI Analysis */}
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="h-5 w-5 mr-2" />
                AI Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-4">
                <Select value={aiAnalysisType} onValueChange={setAiAnalysisType}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="anomaly_detection">Anomaly Detection</SelectItem>
                    <SelectItem value="pattern_recognition">
                      Pattern Recognition
                    </SelectItem>
                    <SelectItem value="risk_assessment">Risk Assessment</SelectItem>
                    <SelectItem value="full_analysis">Full Analysis</SelectItem>
                  </SelectContent>
                </Select>
                <Button onClick={handleAIAnalysis} disabled={!searchAddress.trim()}>
                  <Brain className="h-4 w-4 mr-2" />
                  Run AI Analysis
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Alerts Tab */}
        <TabsContent value="alerts" className="space-y-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span>Forensics Alerts</span>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={refreshAlerts}
                  disabled={loading.alerts}
                >
                  {loading.alerts ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4 mr-2" />
                  )}
                  Refresh
                </Button>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-4">
                  {alerts.map(alert => (
                    <Card key={alert.id} className="bg-gray-800">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <Badge variant={getRiskStyling(alert.risk_level).variant}>
                                {getRiskLevelLabel(alert.risk_level)}
                              </Badge>
                              <Badge variant="outline">
                                {alert.event_type
                                  .replace(/_/g, ' ')
                                  .replace(/\b\w/g, l => l.toUpperCase())}
                              </Badge>
                              <span className="text-sm text-gray-400">
                                Confidence: {(alert.confidence * 100).toFixed(1)}%
                              </span>
                            </div>
                            <p className="text-sm font-medium">{alert.description}</p>
                            <div className="text-xs text-gray-400">
                              <p>Addresses: {alert.addresses_involved.length}</p>
                              <p>Transactions: {alert.transaction_hashes.length}</p>
                              <p>
                                Timestamp: {new Date(alert.timestamp).toLocaleString()}
                              </p>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {alerts.length === 0 && !loading.alerts && (
                    <div className="text-center text-gray-400 py-8">
                      No alerts found
                    </div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Cases Tab */}
        <TabsContent value="cases" className="space-y-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle>Investigation Cases</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-4">
                  {cases.map(case_ => (
                    <Card key={case_.case_id} className="bg-gray-800">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="space-y-2">
                            <div className="flex items-center space-x-2">
                              <Badge variant={getRiskStyling(case_.priority).variant}>
                                {getRiskLevelLabel(case_.priority)}
                              </Badge>
                              <Badge
                                variant={
                                  case_.status === 'open' ? 'default' : 'secondary'
                                }
                              >
                                {case_.status.toUpperCase()}
                              </Badge>
                            </div>
                            <h3 className="text-sm font-medium">{case_.title}</h3>
                            <p className="text-xs text-gray-400">{case_.description}</p>
                            <div className="text-xs text-gray-400">
                              <p>Investigator: {case_.investigator}</p>
                              <p>
                                Created:{' '}
                                {new Date(case_.created_at).toLocaleDateString()}
                              </p>
                              <p>Alerts: {case_.alerts.length}</p>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm">
                            <FileText className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {cases.length === 0 && !loading.cases && (
                    <div className="text-center text-gray-400 py-8">No cases found</div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Patterns Tab */}
        <TabsContent value="patterns" className="space-y-6">
          <Card className="bg-gray-900 border-gray-800">
            <CardHeader>
              <CardTitle>Detected Patterns</CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-4">
                  {patterns.map((pattern, index) => (
                    <Card key={index} className="bg-gray-800">
                      <CardContent className="p-4">
                        <div className="space-y-2">
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline">
                              {pattern.pattern_type
                                .replace(/_/g, ' ')
                                .replace(/\b\w/g, l => l.toUpperCase())}
                            </Badge>
                            <span className="text-sm text-gray-400">
                              Confidence: {(pattern.confidence * 100).toFixed(1)}%
                            </span>
                          </div>
                          <p className="text-sm font-medium">{pattern.description}</p>
                          <div className="text-xs text-gray-400">
                            <p>Addresses: {pattern.addresses.length}</p>
                            <p>Transactions: {pattern.transactions.length}</p>
                            <p>Total Value: {pattern.total_value}</p>
                            <p>Risk Indicators: {pattern.risk_indicators.join(', ')}</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                  {patterns.length === 0 && !loading.patterns && (
                    <div className="text-center text-gray-400 py-8">
                      No patterns detected
                    </div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>Investigation Performance</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between">
                    <span>Total Investigations</span>
                    <span className="font-bold">
                      {statistics?.total_investigations || 0}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Time</span>
                    <span className="font-bold">
                      {statistics?.average_investigation_time.toFixed(2) || 0}s
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Success Rate</span>
                    <span className="font-bold text-green-500">
                      {statistics
                        ? (
                            (statistics.patterns_detected /
                              Math.max(statistics.total_investigations, 1)) *
                            100
                          ).toFixed(1)
                        : 0}
                      %
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card className="bg-gray-900 border-gray-800">
              <CardHeader>
                <CardTitle>System Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span>Real-time Monitoring</span>
                    <Badge variant={monitoring.active ? 'default' : 'secondary'}>
                      {monitoring.active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <div className="flex justify-between">
                    <span>Monitored Addresses</span>
                    <span className="font-bold">
                      {monitoring.addresses_monitored.length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Alerts Generated</span>
                    <span className="font-bold">{monitoring.alerts_generated}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
