/**
 * Scanner API Connection Test Component
 * Tests and displays the connection status for the Scanner module
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useScannerAPI, type ScannerHealth } from '@/hooks/useScannerAPI';
import {
  Shield,
  Activity,
  Zap,
  RefreshCw,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Play,
} from 'lucide-react';

export const ScannerConnectionTest: React.FC = () => {
  const { getHealth, startScan, isLoading, error, clearError } = useScannerAPI();
  const [healthData, setHealthData] = useState<ScannerHealth | null>(null);
  const [testScanResult, setTestScanResult] = useState<any>(null);

  const fetchHealth = async () => {
    try {
      clearError();
      const health = await getHealth();
      setHealthData(health);
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const testScan = async () => {
    try {
      clearError();
      setTestScanResult(null);

      // Test scan with a sample address
      const scanRequest = {
        target: '0x1234567890123456789012345678901234567890', // Sample address
        enable_simulation: true,
        plugins: ['basic', 'security'],
      };

      const result = await startScan(scanRequest);
      setTestScanResult(result);
    } catch (err) {
      console.error('Test scan failed:', err);
    }
  };

  useEffect(() => {
    fetchHealth();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600';
      case 'degraded':
        return 'text-yellow-600';
      case 'unhealthy':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  if (isLoading && !healthData) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Scanner API Connection Test
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <div className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4 animate-spin" />
              Testing scanner connection...
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card
        className={`w-full ${
          error ? 'border-red-200' : healthData ? 'border-green-200' : 'border-gray-200'
        }`}
      >
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Scanner API Connection Test
            </div>
            {healthData && !error && (
              <Badge variant="outline" className="bg-green-50 text-green-700">
                <CheckCircle className="h-3 w-3 mr-1" />
                Connected
              </Badge>
            )}
            {error && (
              <Badge variant="destructive">
                <XCircle className="h-3 w-3 mr-1" />
                Error
              </Badge>
            )}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {error ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2 text-red-600">
                <AlertTriangle className="h-4 w-4" />
                <span className="font-medium">Connection Failed</span>
              </div>
              <p className="text-red-600 text-sm">{error}</p>
              <Button onClick={fetchHealth} variant="outline" disabled={isLoading}>
                <RefreshCw
                  className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`}
                />
                Retry Connection
              </Button>
            </div>
          ) : healthData ? (
            <div className="space-y-6">
              {/* Health Status */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Activity className="h-4 w-4 text-green-500" />
                      <span className="text-sm font-medium">Status</span>
                    </div>
                    <div
                      className={`text-lg font-bold ${getStatusColor(
                        healthData.status,
                      )}`}
                    >
                      {healthData.status.toUpperCase()}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Zap className="h-4 w-4 text-blue-500" />
                      <span className="text-sm font-medium">Active Scans</span>
                    </div>
                    <div className="text-lg font-bold text-blue-600">
                      {healthData.active_scans}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Shield className="h-4 w-4 text-purple-500" />
                      <span className="text-sm font-medium">Total Scans</span>
                    </div>
                    <div className="text-lg font-bold text-purple-600">
                      {healthData.total_scans}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardContent className="p-4">
                    <div className="flex items-center gap-2">
                      <Activity className="h-4 w-4 text-orange-500" />
                      <span className="text-sm font-medium">External Scanner</span>
                    </div>
                    <div
                      className={`text-lg font-bold ${
                        healthData.external_scanner ? 'text-green-600' : 'text-gray-600'
                      }`}
                    >
                      {healthData.external_scanner ? 'Available' : 'Not Available'}
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Test Scan Section */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Test Scan Function</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <p className="text-sm text-gray-600">
                      Test the scanner by initiating a scan with sample data
                    </p>

                    <Button
                      onClick={testScan}
                      disabled={isLoading}
                      className="w-full md:w-auto"
                    >
                      <Play
                        className={`h-4 w-4 mr-2 ${isLoading ? 'animate-pulse' : ''}`}
                      />
                      {isLoading ? 'Starting Test Scan...' : 'Start Test Scan'}
                    </Button>

                    {testScanResult && (
                      <div className="mt-4 p-4 bg-green-50 rounded-lg border border-green-200">
                        <div className="flex items-center gap-2 text-green-700 font-medium mb-2">
                          <CheckCircle className="h-4 w-4" />
                          Test Scan Initiated Successfully
                        </div>
                        <div className="space-y-1 text-sm">
                          <p>
                            <strong>Scan ID:</strong> {testScanResult.scan_id}
                          </p>
                          <p>
                            <strong>Status:</strong> {testScanResult.status}
                          </p>
                          <p>
                            <strong>Message:</strong> {testScanResult.message}
                          </p>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* API Endpoints Status */}
              <Card>
                <CardHeader>
                  <CardTitle>Scanner API Endpoints</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    <Badge
                      variant="outline"
                      className="bg-green-50 text-green-700 justify-start"
                    >
                      ✅ GET /api/scanner/health
                    </Badge>
                    <Badge
                      variant="outline"
                      className="bg-blue-50 text-blue-700 justify-start"
                    >
                      📡 POST /api/scanner/scan
                    </Badge>
                    <Badge
                      variant="outline"
                      className="bg-purple-50 text-purple-700 justify-start"
                    >
                      🔍 GET /api/scanner/scan/{'{{id}}'}
                    </Badge>
                    <Badge
                      variant="outline"
                      className="bg-orange-50 text-orange-700 justify-start"
                    >
                      📊 GET /api/scanner/scans
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-gray-500">No health data available</p>
              <Button onClick={fetchHealth} variant="outline" className="mt-4">
                <RefreshCw className="h-4 w-4 mr-2" />
                Check Health
              </Button>
            </div>
          )}

          {/* Refresh Button */}
          <div className="mt-6 flex justify-end">
            <Button
              onClick={fetchHealth}
              variant="outline"
              size="sm"
              disabled={isLoading}
            >
              <RefreshCw
                className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`}
              />
              Refresh Status
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
