/**
 * API Connection Test Component
 * Tests the connection between frontend and backend
 */

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useDashboardData } from '@/hooks/useDashboardData';
import { Activity, Cpu, HardDrive, Network, RefreshCw } from 'lucide-react';

export const ApiConnectionTest: React.FC = () => {
  const { data, loading, error, refresh } = useDashboardData();

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            API Connection Test
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center p-8">
            <div className="flex items-center gap-2">
              <RefreshCw className="h-4 w-4 animate-spin" />
              Loading dashboard data...
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full border-red-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-red-600">
            <Activity className="h-5 w-5" />
            API Connection Test - Error
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Badge variant="destructive">Connection Failed</Badge>
            <p className="text-red-600">{error}</p>
            <Button onClick={refresh} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry Connection
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      <Card className="w-full border-green-200">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-green-600">
              <Activity className="h-5 w-5" />
              API Connection Test - Success
            </div>
            <Badge variant="outline" className="bg-green-50 text-green-700">
              Connected
            </Badge>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Cpu className="h-4 w-4 text-blue-500" />
                  <span className="text-sm font-medium">CPU Usage</span>
                </div>
                <div className="text-2xl font-bold text-blue-600">
                  {data?.cpu.toFixed(1)}%
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-orange-500" />
                  <span className="text-sm font-medium">Memory Usage</span>
                </div>
                <div className="text-2xl font-bold text-orange-600">
                  {data?.mem.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">
                  {data?.mem_available_gb.toFixed(1)}GB /{' '}
                  {data?.mem_total_gb.toFixed(1)}GB
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <HardDrive className="h-4 w-4 text-purple-500" />
                  <span className="text-sm font-medium">Disk Usage</span>
                </div>
                <div className="text-2xl font-bold text-purple-600">
                  {data?.disk.percent.toFixed(1)}%
                </div>
                <div className="text-xs text-gray-500">
                  {data?.disk.used_gb.toFixed(1)}GB / {data?.disk.total_gb.toFixed(1)}GB
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-4">
                <div className="flex items-center gap-2">
                  <Network className="h-4 w-4 text-green-500" />
                  <span className="text-sm font-medium">Network</span>
                </div>
                <div className="text-lg font-bold text-green-600">
                  {((data?.network.bytes_recv || 0) / (1024 * 1024 * 1024)).toFixed(2)}
                  GB
                </div>
                <div className="text-xs text-gray-500">Received</div>
              </CardContent>
            </Card>
          </div>

          <div className="mt-6 flex items-center justify-between">
            <div className="text-sm text-gray-500">
              Last updated:{' '}
              {data ? new Date(data.timestamp).toLocaleTimeString() : 'Never'}
            </div>
            <Button onClick={refresh} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Backend API Endpoints Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Badge variant="outline" className="bg-green-50 text-green-700">
                ✅ Dashboard API (http://localhost:8000/api/dashboard/stats)
              </Badge>
              <Badge variant="outline" className="bg-blue-50 text-blue-700">
                📊 Real-time system metrics
              </Badge>
              <Badge variant="outline" className="bg-purple-50 text-purple-700">
                🔄 Auto-refresh every 30s
              </Badge>
            </div>
            <div className="space-y-2">
              <Badge variant="outline">🛡️ Scanner API (/api/scanner/*)</Badge>
              <Badge variant="outline">💎 MEV API (/api/mev/*)</Badge>
              <Badge variant="outline">📈 Reports API (/api/reports/*)</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
