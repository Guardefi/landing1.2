import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Progress } from '../components/ui/progress';
import {
  Shield,
  AlertTriangle,
  CheckCircle,
  Clock,
  Zap,
  Eye,
  Search,
  FileText,
} from 'lucide-react';

interface ThreatAlert {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  type: string;
  description: string;
  timestamp: string;
  status: 'active' | 'investigating' | 'resolved';
  source: string;
}

interface VulnerabilityData {
  id: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  address: string;
  type: string;
  riskScore: number;
}

const mockThreats: ThreatAlert[] = [
  {
    id: '1',
    severity: 'high',
    type: 'Suspicious Transaction',
    description: 'Large value transaction detected from flagged address',
    timestamp: '2 minutes ago',
    status: 'investigating',
    source: '0x742d35Cc6097C0532',
  },
  {
    id: '2',
    severity: 'medium',
    type: 'Contract Vulnerability',
    description: 'Potential reentrancy vulnerability in smart contract',
    timestamp: '15 minutes ago',
    status: 'active',
    source: 'Contract Analysis',
  },
  {
    id: '3',
    severity: 'low',
    type: 'Unusual Pattern',
    description: 'Abnormal trading pattern detected in DEX pools',
    timestamp: '1 hour ago',
    status: 'resolved',
    source: 'Pattern Recognition',
  },
];

const mockVulnerabilities: VulnerabilityData[] = [
  {
    id: '1',
    severity: 'critical',
    address: '0x1234...5678',
    type: 'Honeypot',
    riskScore: 95,
  },
  {
    id: '2',
    severity: 'high',
    address: '0xabcd...efgh',
    type: 'Rug Pull Risk',
    riskScore: 82,
  },
  {
    id: '3',
    severity: 'medium',
    address: '0x9876...5432',
    type: 'Flash Loan Attack',
    riskScore: 64,
  },
  {
    id: '4',
    severity: 'low',
    address: '0xfedc...ba98',
    type: 'Price Manipulation',
    riskScore: 31,
  },
];

export function SecurityOperationsCenter() {
  const [threats, setThreats] = useState<ThreatAlert[]>(mockThreats);
  const [scanProgress, setScanProgress] = useState(0);
  const [isScanning, setIsScanning] = useState(false);

  useEffect(() => {
    // Simulate scanning progress
    if (isScanning) {
      const interval = setInterval(() => {
        setScanProgress(prev => {
          if (prev >= 100) {
            setIsScanning(false);
            return 0;
          }
          return prev + Math.random() * 10;
        });
      }, 500);
      return () => clearInterval(interval);
    }
  }, [isScanning]);

  const startScan = () => {
    setIsScanning(true);
    setScanProgress(0);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-blue-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'investigating':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'resolved':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Security Operations Center
          </h1>
          <p className="text-muted-foreground">
            Advanced threat detection and response for blockchain security
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <Button onClick={startScan} disabled={isScanning}>
            <Search className="h-4 w-4 mr-2" />
            {isScanning ? 'Scanning...' : 'Start Full Scan'}
          </Button>
        </div>
      </div>

      {/* Security Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-green-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Score</CardTitle>
            <Shield className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">98.7%</div>
            <p className="text-xs text-muted-foreground">Excellent security posture</p>
          </CardContent>
        </Card>

        <Card className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border-red-500/20">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Threats</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-500">
              {threats.filter(t => t.status === 'active').length}
            </div>
            <p className="text-xs text-muted-foreground">Require immediate attention</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Scans Completed</CardTitle>
            <Eye className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1,247</div>
            <p className="text-xs text-muted-foreground">In the last 24 hours</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Response Time</CardTitle>
            <Zap className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">1.2s</div>
            <p className="text-xs text-muted-foreground">Average detection time</p>
          </CardContent>
        </Card>
      </div>

      {/* Scanning Progress */}
      {isScanning && (
        <Card>
          <CardHeader>
            <CardTitle>Security Scan in Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span>Scanning blockchain transactions...</span>
                <span>{Math.round(scanProgress)}%</span>
              </div>
              <Progress value={scanProgress} className="w-full" />
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Threat Timeline */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              <span>Live Threat Feed</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {threats.map(threat => (
                <div
                  key={threat.id}
                  className="flex items-start space-x-3 p-3 rounded-lg border"
                >
                  <div
                    className={`w-3 h-3 rounded-full mt-2 ${getSeverityColor(
                      threat.severity,
                    )}`}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium">{threat.type}</p>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(threat.status)}
                        <Badge variant="outline" className="text-xs">
                          {threat.severity.toUpperCase()}
                        </Badge>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {threat.description}
                    </p>
                    <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                      <span>{threat.source}</span>
                      <span>{threat.timestamp}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            <Button variant="outline" className="w-full mt-4">
              <FileText className="h-4 w-4 mr-2" />
              View Full Threat Report
            </Button>
          </CardContent>
        </Card>

        {/* Vulnerability Heat Map */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Search className="h-5 w-5 text-purple-500" />
              <span>Vulnerability Assessment</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {mockVulnerabilities.map(vuln => (
                <div
                  key={vuln.id}
                  className="flex items-center justify-between p-3 rounded-lg border"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-3 h-3 rounded-full ${getSeverityColor(
                        vuln.severity,
                      )}`}
                    />
                    <div>
                      <p className="text-sm font-medium">{vuln.type}</p>
                      <p className="text-xs text-muted-foreground">{vuln.address}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold">{vuln.riskScore}%</p>
                    <p className="text-xs text-muted-foreground">Risk Score</p>
                  </div>
                </div>
              ))}
            </div>
            <Button variant="outline" className="w-full mt-4">
              <Shield className="h-4 w-4 mr-2" />
              Deploy Mitigation
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Incident Response Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Incident Response & Mitigation</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button className="h-20 flex flex-col space-y-2">
              <Shield className="h-6 w-6" />
              <span>Auto Mitigate</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <AlertTriangle className="h-6 w-6" />
              <span>Manual Review</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col space-y-2">
              <FileText className="h-6 w-6" />
              <span>Generate Report</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
