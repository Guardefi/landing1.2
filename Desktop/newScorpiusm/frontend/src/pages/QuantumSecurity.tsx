'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import {
  Shield,
  Zap,
  Atom,
  Lock,
  Key,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Activity,
  TrendingUp,
  TrendingDown,
  Cpu,
  Database,
  Network,
  Eye,
  Settings,
  Play,
  Pause,
  RefreshCw,
  Fingerprint,
  Binary,
  Globe,
  Wifi,
  Server,
  Layers,
} from 'lucide-react';

// Mock quantum security data
const quantumMetrics = {
  encryptionStrength: 98.5,
  keyRotationStatus: 'Active',
  quantumReadiness: 87,
  threatLevel: 'Low',
  lastKeyRotation: '2 hours ago',
  activeProtocols: 12,
  quantumComputers: 3,
  secureChannels: 156,
};

const quantumSecurityData = Array.from({ length: 24 }, (_, i) => ({
  time: `${i}:00`,
  encryptionStrength: 85 + Math.sin(i * 0.3) * 10 + Math.random() * 5,
  quantumResistance: 75 + Math.sin(i * 0.4) * 8 + Math.random() * 4,
  keyEntropy: 90 + Math.sin(i * 0.2) * 5 + Math.random() * 3,
  threatDetection: Math.random() * 20 + 5,
}));

const protocolStatus = [
  {
    name: 'Lattice-based Cryptography',
    status: 'active',
    strength: 98,
    quantum_safe: true,
  },
  {
    name: 'Code-based Cryptography',
    status: 'active',
    strength: 95,
    quantum_safe: true,
  },
  {
    name: 'Multivariate Cryptography',
    status: 'standby',
    strength: 92,
    quantum_safe: true,
  },
  { name: 'Hash-based Signatures', status: 'active', strength: 99, quantum_safe: true },
  {
    name: 'Isogeny-based Cryptography',
    status: 'testing',
    strength: 88,
    quantum_safe: true,
  },
  { name: 'RSA-2048', status: 'deprecated', strength: 45, quantum_safe: false },
  { name: 'ECDSA-256', status: 'phasing_out', strength: 52, quantum_safe: false },
  { name: 'AES-256', status: 'active', strength: 85, quantum_safe: false },
];

const quantumThreatAnalysis = [
  {
    category: 'Public Key Cryptography',
    current: 95,
    post_quantum: 25,
    risk: 'Critical',
  },
  { category: 'Digital Signatures', current: 92, post_quantum: 30, risk: 'High' },
  { category: 'Key Exchange', current: 88, post_quantum: 35, risk: 'High' },
  { category: 'Symmetric Encryption', current: 85, post_quantum: 75, risk: 'Medium' },
  { category: 'Hash Functions', current: 98, post_quantum: 90, risk: 'Low' },
  { category: 'Random Number Generation', current: 96, post_quantum: 95, risk: 'Low' },
];

const quantumDeployments = [
  {
    id: 'QS-001',
    name: 'Primary Wallet Protection',
    type: 'Lattice-based',
    status: 'Deployed',
    coverage: 98,
    performance: 'High',
    lastUpdate: '2024-01-15 10:30:00',
  },
  {
    id: 'QS-002',
    name: 'Cross-chain Bridge Security',
    type: 'Hash-based',
    status: 'Deployed',
    coverage: 95,
    performance: 'High',
    lastUpdate: '2024-01-15 09:15:00',
  },
  {
    id: 'QS-003',
    name: 'MEV Bot Communications',
    type: 'Code-based',
    status: 'Testing',
    coverage: 78,
    performance: 'Medium',
    lastUpdate: '2024-01-15 08:45:00',
  },
];

const keyManagement = {
  totalKeys: 2847,
  activeKeys: 2789,
  expiredKeys: 45,
  compromisedKeys: 0,
  rotationsPending: 13,
  nextRotation: '6 hours',
  entropyLevel: 256,
  quantumSafeKeys: 2234,
};

export function QuantumSecurity() {
  const [activeTab, setActiveTab] = useState('overview');
  const [simulationRunning, setSimulationRunning] = useState(false);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
      case 'Deployed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'testing':
      case 'Testing':
        return <Activity className="h-4 w-4 text-blue-500" />;
      case 'standby':
        return <Pause className="h-4 w-4 text-yellow-500" />;
      case 'deprecated':
      case 'phasing_out':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
      case 'Deployed':
        return (
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            Active
          </Badge>
        );
      case 'testing':
      case 'Testing':
        return (
          <Badge variant="secondary" className="bg-blue-100 text-blue-800">
            Testing
          </Badge>
        );
      case 'standby':
        return (
          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
            Standby
          </Badge>
        );
      case 'deprecated':
        return <Badge variant="destructive">Deprecated</Badge>;
      case 'phasing_out':
        return (
          <Badge variant="secondary" className="bg-orange-100 text-orange-800">
            Phasing Out
          </Badge>
        );
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'Critical':
        return <Badge variant="destructive">Critical</Badge>;
      case 'High':
        return (
          <Badge variant="secondary" className="bg-red-100 text-red-800">
            High
          </Badge>
        );
      case 'Medium':
        return (
          <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
            Medium
          </Badge>
        );
      case 'Low':
        return (
          <Badge variant="secondary" className="bg-green-100 text-green-800">
            Low
          </Badge>
        );
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Quantum Security</h1>
          <p className="text-muted-foreground">
            Next-generation quantum-resistant cryptographic protection
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setSimulationRunning(!simulationRunning)}
          >
            {simulationRunning ? (
              <Pause className="h-4 w-4 mr-2" />
            ) : (
              <Play className="h-4 w-4 mr-2" />
            )}
            {simulationRunning ? 'Stop' : 'Run'} Simulation
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Configure
          </Button>
          <Button variant="outline" size="sm">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Quantum Security Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Quantum Readiness</CardTitle>
            <Atom className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-500">
              {quantumMetrics.quantumReadiness}%
            </div>
            <Progress value={quantumMetrics.quantumReadiness} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">
              Post-quantum migration progress
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Encryption Strength</CardTitle>
            <Lock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {quantumMetrics.encryptionStrength}%
            </div>
            <Progress value={quantumMetrics.encryptionStrength} className="mt-2" />
            <p className="text-xs text-muted-foreground mt-1">
              Current protection level
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Protocols</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{quantumMetrics.activeProtocols}</div>
            <p className="text-xs text-muted-foreground">
              {quantumMetrics.secureChannels} secure channels
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Threat Level</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {quantumMetrics.threatLevel}
            </div>
            <p className="text-xs text-muted-foreground">
              Last rotation: {quantumMetrics.lastKeyRotation}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quantum Security Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="protocols">Protocols</TabsTrigger>
          <TabsTrigger value="keys">Key Management</TabsTrigger>
          <TabsTrigger value="threats">Threat Analysis</TabsTrigger>
          <TabsTrigger value="deployments">Deployments</TabsTrigger>
          <TabsTrigger value="migration">Migration</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Quantum Security Metrics (24h)</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={quantumSecurityData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area
                      type="monotone"
                      dataKey="encryptionStrength"
                      stackId="1"
                      stroke="#8884d8"
                      fill="#8884d8"
                      name="Encryption Strength"
                    />
                    <Area
                      type="monotone"
                      dataKey="quantumResistance"
                      stackId="1"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      name="Quantum Resistance"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Security Posture Analysis</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={quantumThreatAnalysis}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="category" />
                    <PolarRadiusAxis />
                    <Radar
                      name="Current Security"
                      dataKey="current"
                      stroke="#8884d8"
                      fill="#8884d8"
                      fillOpacity={0.6}
                    />
                    <Radar
                      name="Post-Quantum"
                      dataKey="post_quantum"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      fillOpacity={0.6}
                    />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="protocols" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Cryptographic Protocols Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {protocolStatus.map((protocol, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(protocol.status)}
                      <div>
                        <div className="font-medium">{protocol.name}</div>
                        <div className="text-sm text-muted-foreground">
                          Strength: {protocol.strength}% |
                          {protocol.quantum_safe
                            ? ' Quantum-Safe'
                            : ' Quantum-Vulnerable'}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Progress value={protocol.strength} className="w-20" />
                      {getStatusBadge(protocol.status)}
                      {protocol.quantum_safe && (
                        <Badge
                          variant="secondary"
                          className="bg-blue-100 text-blue-800"
                        >
                          <Atom className="h-3 w-3 mr-1" />
                          Quantum-Safe
                        </Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="keys" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Key Statistics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Total Keys</span>
                  <Badge variant="secondary">{keyManagement.totalKeys}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Active Keys</span>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    {keyManagement.activeKeys}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Quantum-Safe Keys</span>
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                    {keyManagement.quantumSafeKeys}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Expired Keys</span>
                  <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                    {keyManagement.expiredKeys}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Compromised Keys</span>
                  <Badge
                    variant={
                      keyManagement.compromisedKeys > 0 ? 'destructive' : 'secondary'
                    }
                  >
                    {keyManagement.compromisedKeys}
                  </Badge>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Key Rotation Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Rotation Status</span>
                  <Badge variant="secondary" className="bg-green-100 text-green-800">
                    Active
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Pending Rotations</span>
                  <Badge variant="outline">{keyManagement.rotationsPending}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Next Rotation</span>
                  <span className="text-sm">{keyManagement.nextRotation}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium">Entropy Level</span>
                  <Badge variant="secondary">{keyManagement.entropyLevel}-bit</Badge>
                </div>
                <Button className="w-full" size="sm">
                  <Key className="h-4 w-4 mr-2" />
                  Force Rotation
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Key Generation Rate</CardTitle>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={200}>
                  <LineChart data={quantumSecurityData.slice(-12)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="time" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="keyEntropy"
                      stroke="#8884d8"
                      name="Key Entropy"
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="threats" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quantum Threat Assessment</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {quantumThreatAnalysis.map((threat, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="font-medium">{threat.category}</div>
                      {getRiskBadge(threat.risk)}
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-sm text-muted-foreground">
                          Current Security
                        </div>
                        <div className="flex items-center space-x-2">
                          <Progress value={threat.current} className="flex-1" />
                          <span className="text-sm font-medium">{threat.current}%</span>
                        </div>
                      </div>
                      <div>
                        <div className="text-sm text-muted-foreground">
                          Post-Quantum Security
                        </div>
                        <div className="flex items-center space-x-2">
                          <Progress value={threat.post_quantum} className="flex-1" />
                          <span className="text-sm font-medium">
                            {threat.post_quantum}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="deployments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Quantum Security Deployments</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {quantumDeployments.map((deployment, index) => (
                  <div key={index} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <div className="font-medium">{deployment.name}</div>
                        <div className="text-sm text-muted-foreground">
                          {deployment.id} | {deployment.type}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {getStatusIcon(deployment.status)}
                        {getStatusBadge(deployment.status)}
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Coverage:</span>
                        <div className="flex items-center space-x-2">
                          <Progress value={deployment.coverage} className="flex-1" />
                          <span className="font-medium">{deployment.coverage}%</span>
                        </div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Performance:</span>
                        <div className="font-medium">{deployment.performance}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Last Update:</span>
                        <div className="text-xs">{deployment.lastUpdate}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="migration" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Post-Quantum Migration Progress</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-blue-500 mb-2">87%</div>
                  <div className="text-muted-foreground">Migration Complete</div>
                  <Progress value={87} className="mt-4" />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-3">
                    <h4 className="font-medium">Completed Migrations</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Wallet Encryption</span>
                        <Badge
                          variant="secondary"
                          className="bg-green-100 text-green-800"
                        >
                          Complete
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>API Communications</span>
                        <Badge
                          variant="secondary"
                          className="bg-green-100 text-green-800"
                        >
                          Complete
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Database Encryption</span>
                        <Badge
                          variant="secondary"
                          className="bg-green-100 text-green-800"
                        >
                          Complete
                        </Badge>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="font-medium">Pending Migrations</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Legacy Contracts</span>
                        <Badge
                          variant="secondary"
                          className="bg-yellow-100 text-yellow-800"
                        >
                          In Progress
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Third-party APIs</span>
                        <Badge variant="outline">Pending</Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Archive Data</span>
                        <Badge variant="outline">Scheduled</Badge>
                      </div>
                    </div>
                  </div>
                </div>

                <Button className="w-full">
                  <TrendingUp className="h-4 w-4 mr-2" />
                  Accelerate Migration
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
