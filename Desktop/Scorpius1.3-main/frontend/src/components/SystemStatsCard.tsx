import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import {
  Activity,
  Shield,
  TrendingUp,
  FileText,
  BarChart3,
  Clock,
  Target,
  Zap,
  Download,
  RefreshCw,
} from "lucide-react";
import { usePersistedStats } from "@/hooks/usePersistedStats";
import { StorageManager } from "@/lib/storage";
import { toast } from "sonner";

interface SystemStatsCardProps {
  className?: string;
  showExportButton?: boolean;
}

export const SystemStatsCard = ({
  className,
  showExportButton = false,
}: SystemStatsCardProps) => {
  const { stats, refreshStats } = usePersistedStats();

  const handleExportData = () => {
    try {
      const data = StorageManager.exportData();
      const blob = new Blob([data], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `scorpius-stats-${new Date().toISOString().split("T")[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success("Statistics exported successfully");
    } catch (error) {
      toast.error("Failed to export statistics");
    }
  };

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    return new Date(dateString).toLocaleDateString();
  };

  const formatTime = (dateString: string | null) => {
    if (!dateString) return "Never";
    return new Date(dateString).toLocaleString();
  };

  const calculateTotalVulnerabilities = () => {
    return stats.scanStats.vulnerabilitiesFound;
  };

  const calculateSuccessRate = () => {
    const total = stats.scanStats.totalScans;
    if (total === 0) return 0;
    const threats = stats.scanStats.threatsDetected;
    return Math.round(((total - threats) / total) * 100);
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5" />
              <span>System Statistics</span>
            </CardTitle>
            <CardDescription>
              Persistent data across all sessions
            </CardDescription>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={refreshStats}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            {showExportButton && (
              <Button variant="outline" size="sm" onClick={handleExportData}>
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Security Scanning Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg border">
            <Shield className="h-8 w-8 text-blue-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-blue-900">
              {stats.scanStats.totalScans}
            </div>
            <div className="text-sm text-blue-600">Total Scans</div>
          </div>

          <div className="text-center p-4 bg-red-50 rounded-lg border">
            <Target className="h-8 w-8 text-red-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-red-900">
              {calculateTotalVulnerabilities()}
            </div>
            <div className="text-sm text-red-600">Vulnerabilities</div>
          </div>

          <div className="text-center p-4 bg-green-50 rounded-lg border">
            <TrendingUp className="h-8 w-8 text-green-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-green-900">
              {calculateSuccessRate()}%
            </div>
            <div className="text-sm text-green-600">Success Rate</div>
          </div>

          <div className="text-center p-4 bg-purple-50 rounded-lg border">
            <Activity className="h-8 w-8 text-purple-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-purple-900">
              {stats.scanStats.contractsAnalyzed}
            </div>
            <div className="text-sm text-purple-600">Contracts</div>
          </div>
        </div>

        {/* Trading & MEV Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-emerald-50 rounded-lg border">
            <Zap className="h-8 w-8 text-emerald-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-emerald-900">
              {stats.tradingStats.totalTrades}
            </div>
            <div className="text-sm text-emerald-600">Total Trades</div>
          </div>

          <div className="text-center p-4 bg-yellow-50 rounded-lg border">
            <TrendingUp className="h-8 w-8 text-yellow-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-yellow-900">
              ${stats.tradingStats.totalProfit.toFixed(2)}
            </div>
            <div className="text-sm text-yellow-600">Total Profit</div>
          </div>

          <div className="text-center p-4 bg-cyan-50 rounded-lg border">
            <Shield className="h-8 w-8 text-cyan-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-cyan-900">
              {stats.tradingStats.attacksPrevented}
            </div>
            <div className="text-sm text-cyan-600">Attacks Prevented</div>
          </div>

          <div className="text-center p-4 bg-indigo-50 rounded-lg border">
            <TrendingUp className="h-8 w-8 text-indigo-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-indigo-900">
              ${stats.tradingStats.valueSaved.toFixed(2)}
            </div>
            <div className="text-sm text-indigo-600">Value Saved</div>
          </div>
        </div>

        {/* Mempool & Reports Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-orange-50 rounded-lg border">
            <Activity className="h-8 w-8 text-orange-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-orange-900">
              {stats.mempoolStats.transactionsMonitored}
            </div>
            <div className="text-sm text-orange-600">Mempool Txs</div>
          </div>

          <div className="text-center p-4 bg-pink-50 rounded-lg border">
            <Target className="h-8 w-8 text-pink-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-pink-900">
              {stats.mempoolStats.threatsDetected}
            </div>
            <div className="text-sm text-pink-600">Threats Found</div>
          </div>

          <div className="text-center p-4 bg-teal-50 rounded-lg border">
            <FileText className="h-8 w-8 text-teal-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-teal-900">
              {stats.reportStats.totalReports}
            </div>
            <div className="text-sm text-teal-600">Reports Generated</div>
          </div>

          <div className="text-center p-4 bg-slate-50 rounded-lg border">
            <Clock className="h-8 w-8 text-slate-600 mx-auto mb-2" />
            <div className="text-2xl font-bold text-slate-900">
              {stats.reportStats.averageGenerationTime.toFixed(1)}s
            </div>
            <div className="text-sm text-slate-600">Avg Gen Time</div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="space-y-3">
          <h4 className="font-semibold text-sm text-gray-700">
            Recent Activity
          </h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Last Scan:</span>
              <Badge variant="outline">
                {formatTime(stats.scanStats.lastScanDate)}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Last Trade:</span>
              <Badge variant="outline">
                {formatTime(stats.tradingStats.lastTradeDate)}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Last Mempool Activity:</span>
              <Badge variant="outline">
                {formatTime(stats.mempoolStats.lastActivityDate)}
              </Badge>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Last Report:</span>
              <Badge variant="outline">
                {formatTime(stats.reportStats.lastReportDate)}
              </Badge>
            </div>
          </div>
        </div>

        {/* Today's Activity */}
        <div className="space-y-3 pt-4 border-t">
          <h4 className="font-semibold text-sm text-gray-700">
            Today's Activity
          </h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Reports Today:</span>
              <span className="font-medium">
                {stats.reportStats.reportsToday}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Success Rate:</span>
              <span className="font-medium">{calculateSuccessRate()}%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default SystemStatsCard;
