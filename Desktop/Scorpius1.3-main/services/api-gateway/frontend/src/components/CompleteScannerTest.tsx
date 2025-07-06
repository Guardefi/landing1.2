/**
 * Complete Scanner Module Test Component
 * Tests all Scanner functionality including plugins, scans, and results
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  useScannerAPI,
  type ScannerHealth,
  type ScanPlugin,
  type ScanListItem,
  type ScanResult,
} from '@/hooks/useScannerAPI';
import {
  Shield,
  Activity,
  Zap,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Play,
  List,
  Search,
  Clock,
  Eye,
  Trash2,
} from 'lucide-react';

export const CompleteScannerTest: React.FC = () => {
  const {
    getHealth,
    getPlugins,
    startScan,
    getScanResults,
    getAllScans,
    stopScan,
    isLoading,
    error,
    clearError,
  } = useScannerAPI();

  // State
  const [healthData, setHealthData] = useState<ScannerHealth | null>(null);
  const [plugins, setPlugins] = useState<ScanPlugin[]>([]);
  const [scans, setScans] = useState<ScanListItem[]>([]);
  const [selectedScanResult, setSelectedScanResult] = useState<ScanResult | null>(null);

  // Form state
  const [targetAddress, setTargetAddress] = useState(
    '0x1234567890123456789012345678901234567890',
  );
  const [selectedPlugins, setSelectedPlugins] = useState<string[]>([]);
  const [enableSimulation, setEnableSimulation] = useState(true);

  // Fetch all data
  const fetchAllData = async () => {
    try {
      clearError();
      const [healthResult, pluginsResult, scansResult] = await Promise.all([
        getHealth(),
        getPlugins(),
        getAllScans(),
      ]);

      setHealthData(healthResult);
      setPlugins(pluginsResult);
      setScans(scansResult);
    } catch (err) {
      console.error('Failed to fetch data:', err);
    }
  };

  const handleStartScan = async () => {
    try {
      clearError();
      const scanRequest = {
        target: targetAddress,
        plugins:
          selectedPlugins.length > 0 ? selectedPlugins : ['reentrancy', 'overflow'],
        enable_simulation: enableSimulation,
      };

      const result = await startScan(scanRequest);
      console.log('Scan started:', result);

      // Refresh scans list
      const updatedScans = await getAllScans();
      setScans(updatedScans);
    } catch (err) {
      console.error('Failed to start scan:', err);
    }
  };

  const handleViewScanResults = async (scanId: string) => {
    try {
      clearError();
      const result = await getScanResults(scanId);
      setSelectedScanResult(result);
    } catch (err) {
      console.error('Failed to get scan results:', err);
    }
  };

  const handleDeleteScan = async (scanId: string) => {
    try {
      clearError();
      await stopScan(scanId);
      // Refresh scans list
      const updatedScans = await getAllScans();
      setScans(updatedScans);
    } catch (err) {
      console.error('Failed to delete scan:', err);
    }
  };

  const handlePluginToggle = (pluginName: string, checked: boolean) => {
    if (checked) {
      setSelectedPlugins(prev => [...prev, pluginName]);
    } else {
      setSelectedPlugins(prev => prev.filter(p => p !== pluginName));
    }
  };

  useEffect(() => {
    fetchAllData();
  }, []);

  const getStatusBadge = (status: string) => {
    const colors = {
      completed: 'bg-green-50 text-green-700',
      running: 'bg-blue-50 text-blue-700',
      queued: 'bg-yellow-50 text-yellow-700',
      failed: 'bg-red-50 text-red-700',
      cancelled: 'bg-gray-50 text-gray-700',
    };

    return (
      <Badge
        variant="outline"
        className={colors[status as keyof typeof colors] || 'bg-gray-50 text-gray-700'}
      >
        {status.toUpperCase()}
      </Badge>
    );
  };

  if (isLoading && !healthData) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Complete Scanner Module Test
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <div className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4 animate-spin" />
              Loading scanner module...
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="w-full border-blue-200">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-blue-600" />
              Complete Scanner Module Test
            </div>
            <Button
              onClick={fetchAllData}
              variant="outline"
              size="sm"
              disabled={isLoading}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`}
              />
              Refresh All
            </Button>
          </CardTitle>
        </CardHeader>
      </Card>

      {/* Error Display */}
      {error && (
        <Card className="w-full border-red-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-red-600">
              <AlertTriangle className="h-4 w-4" />
              <span className="font-medium">Error: {error}</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Health Status */}
      {healthData && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Scanner Health Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="text-center p-4 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {healthData.status.toUpperCase()}
                </div>
                <div className="text-sm text-gray-600">Status</div>
              </div>
              <div className="text-center p-4 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">
                  {healthData.active_scans}
                </div>
                <div className="text-sm text-gray-600">Active Scans</div>
              </div>
              <div className="text-center p-4 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {healthData.total_scans}
                </div>
                <div className="text-sm text-gray-600">Total Scans</div>
              </div>
              <div className="text-center p-4 bg-orange-50 rounded-lg">
                <div
                  className={`text-2xl font-bold ${
                    healthData.external_scanner ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {healthData.external_scanner ? 'YES' : 'NO'}
                </div>
                <div className="text-sm text-gray-600">External Scanner</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Available Plugins */}
      {plugins.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Available Scanner Plugins ({plugins.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {plugins.map(plugin => (
                <div
                  key={plugin.name}
                  className="flex items-center space-x-2 p-3 border rounded-lg"
                >
                  <Checkbox
                    id={plugin.name}
                    checked={selectedPlugins.includes(plugin.name)}
                    onCheckedChange={checked =>
                      handlePluginToggle(plugin.name, checked as boolean)
                    }
                  />
                  <div className="flex-1">
                    <Label htmlFor={plugin.name} className="font-medium">
                      {plugin.name}
                    </Label>
                    <p className="text-sm text-gray-600">{plugin.description}</p>
                    <Badge variant="outline" className="mt-1">
                      {plugin.category}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* New Scan Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Start New Scan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <Label htmlFor="target">Target Contract Address</Label>
              <Input
                id="target"
                value={targetAddress}
                onChange={e => setTargetAddress(e.target.value)}
                placeholder="0x..."
                className="mt-1"
              />
            </div>

            <div className="flex items-center space-x-2">
              <Checkbox
                id="simulation"
                checked={enableSimulation}
                onCheckedChange={checked => setEnableSimulation(checked as boolean)}
              />
              <Label htmlFor="simulation">Enable Simulation</Label>
            </div>

            <div>
              <Label>
                Selected Plugins:{' '}
                {selectedPlugins.length > 0
                  ? selectedPlugins.join(', ')
                  : 'Default (reentrancy, overflow)'}
              </Label>
            </div>

            <Button
              onClick={handleStartScan}
              disabled={isLoading || !targetAddress}
              className="w-full"
            >
              <Play className={`h-4 w-4 mr-2 ${isLoading ? 'animate-pulse' : ''}`} />
              {isLoading ? 'Starting Scan...' : 'Start Scan'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Scans List */}
      {scans.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <List className="h-5 w-5" />
              Recent Scans ({scans.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {scans.map(scan => (
                <div
                  key={scan.scan_id}
                  className="flex items-center justify-between p-4 border rounded-lg"
                >
                  <div className="flex-1">
                    <div className="font-medium">{scan.target}</div>
                    <div className="text-sm text-gray-600">
                      ID: {scan.scan_id.substring(0, 8)}... | Created:{' '}
                      {new Date(scan.created_at).toLocaleString()} | Findings:{' '}
                      {scan.findings_count}
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusBadge(scan.status)}
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleViewScanResults(scan.scan_id)}
                      disabled={isLoading}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleDeleteScan(scan.scan_id)}
                      disabled={isLoading}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Scan Results */}
      {selectedScanResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Scan Results
              </div>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setSelectedScanResult(null)}
              >
                <XCircle className="h-4 w-4" />
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="font-medium">Target</div>
                  <div className="text-sm">{selectedScanResult.target}</div>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="font-medium">Status</div>
                  {getStatusBadge(selectedScanResult.status)}
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="font-medium">Findings</div>
                  <div className="text-sm">{selectedScanResult.findings.length}</div>
                </div>
              </div>

              {selectedScanResult.findings.length > 0 ? (
                <div className="space-y-2">
                  <div className="font-medium">Findings:</div>
                  {selectedScanResult.findings.map(finding => (
                    <div key={finding.id} className="p-3 border rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div className="font-medium">{finding.title}</div>
                        <Badge
                          variant={
                            finding.severity === 'critical' ? 'destructive' : 'outline'
                          }
                        >
                          {finding.severity.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600">{finding.description}</div>
                      <div className="text-xs text-gray-500 mt-1">
                        Confidence: {(finding.confidence * 100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <CheckCircle className="h-8 w-8 mx-auto mb-2" />
                  No vulnerabilities found
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};
