import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { StorageManager } from "@/lib/storage";
import { reportingService } from "@/services/api/reporting";
import type { 
  ReportTemplate, 
  GeneratedReport, 
  ReportGenerationRequest,
  ReportStatus 
} from "@/services/api/reporting";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { LiveCounter } from "@/components/ui/live-counter";
import { PageHeader } from "@/components/PageHeader";
import { PageLayout } from "@/components/PageLayout";
import {
  FileText,
  Download,
  Settings,
  RefreshCw,
  Plus,
  Search,
  Filter,
  Eye,
  Share2,
  Lock,
  Shield,
  Calendar,
  Clock,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  XCircle,
  FileCode,
  File,
  Globe,
  Database,
  Zap,
  Target,
  BarChart3,
  PieChart,
  Activity,
  Users,
  Signature,
  Droplets,
  GitCompare,
  Package,
  ExternalLink,
  Loader2,
  ChevronDown,
  ChevronRight,
  Star,
  Award,
  Briefcase,
} from "lucide-react";
import { Link } from "react-router-dom";

interface ScanResult {
  id: string;
  contractName: string;
  address: string;
  scanDate: Date;
  status: "completed" | "pending" | "failed";
  findings: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    total: number;
  };
  riskScore: number;
}

const Reports = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedScan, setSelectedScan] = useState<string>("");
  const [selectedFormat, setSelectedFormat] = useState("pdf");
  const [selectedTheme, setSelectedTheme] = useState("dark_pro");
  const [includeSignature, setIncludeSignature] = useState(true);
  const [includeWatermark, setIncludeWatermark] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationProgress, setGenerationProgress] = useState(0);
  const [currentReportId, setCurrentReportId] = useState<string | null>(null);

  // API-driven state
  const [reportTemplates, setReportTemplates] = useState<ReportTemplate[]>([]);
  const [scanResults, setScanResults] = useState<ScanResult[]>([]);
  const [generatedReports, setGeneratedReports] = useState<GeneratedReport[]>([]);
  const [serviceHealth, setServiceHealth] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Clock update effect
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  // Load initial data
  useEffect(() => {
    loadData();
  }, []);

  // Poll for report status updates
  useEffect(() => {
    if (currentReportId) {
      const pollInterval = setInterval(async () => {
        try {
          const response = await reportingService.getReportStatus(currentReportId);
          if (response.success && response.data) {
            const status = response.data;
            setGenerationProgress(status.progress);
            
            if (status.status === 'completed') {
              setIsGenerating(false);
              setCurrentReportId(null);
              setGenerationProgress(0);
              // Refresh reports list
              loadGeneratedReports();
            } else if (status.status === 'failed') {
              setIsGenerating(false);
              setCurrentReportId(null);
              setGenerationProgress(0);
              setError(status.error_message || 'Report generation failed');
            }
          }
        } catch (error) {
          console.error('Error polling report status:', error);
        }
      }, 2000);

      return () => clearInterval(pollInterval);
    }
  }, [currentReportId]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Check service health
      const healthResponse = await reportingService.getHealth();
      setServiceHealth(healthResponse.success);

      // Load templates
      const templatesResponse = await reportingService.getTemplates();
      if (templatesResponse.success && templatesResponse.data) {
        setReportTemplates(templatesResponse.data.templates);
      }

      // Load scans
      const scansResponse = await reportingService.getScans();
      if (scansResponse.success && scansResponse.data) {
        const apiScans = scansResponse.data.scans.map(scan => ({
          id: scan.scan_id,
          contractName: scan.contract_name || 'Unknown Contract',
          address: scan.contract_address || 'Unknown Address',
          scanDate: new Date(scan.scan_date),
          status: scan.status as "completed" | "pending" | "failed",
          findings: scan.findings,
          riskScore: scan.risk_score
        }));
        setScanResults(apiScans);
      }

      // Load generated reports
      await loadGeneratedReports();
      
    } catch (error) {
      console.error('Error loading data:', error);
      setError('Failed to load reporting data');
    } finally {
      setLoading(false);
    }
  };

  const loadGeneratedReports = async () => {
    try {
      const reportsResponse = await reportingService.getReports();
      if (reportsResponse.success && reportsResponse.data) {
        setGeneratedReports(reportsResponse.data.reports);
      }
    } catch (error) {
      console.error('Error loading generated reports:', error);
    }
  };

  const handleGenerateReport = async () => {
    if (!selectedScan) {
      setError("Please select a scan to generate a report");
      return;
    }

    setIsGenerating(true);
    setGenerationProgress(0);
    setError(null);

    try {
      const request: ReportGenerationRequest = {
        scan_id: selectedScan,
        formats: [selectedFormat],
        theme: selectedTheme,
        include_signature: includeSignature,
        include_watermark: includeWatermark,
        title: `Security Report - ${scanResults.find(s => s.id === selectedScan)?.contractName || 'Contract'}`
      };

      const response = await reportingService.generateReport(request);
      
      if (response.success && response.data) {
        setCurrentReportId(response.data.report_id);
        // Polling will be handled by the useEffect
      } else {
        setError(response.message || 'Failed to start report generation');
        setIsGenerating(false);
      }
    } catch (error) {
      console.error('Error generating report:', error);
      setError('Failed to generate report');
      setIsGenerating(false);
    }
  };

  const handleDownloadReport = async (reportId: string) => {
    try {
      const reportDetails = generatedReports.find(r => r.id === reportId);
      const filename = reportDetails 
        ? `${reportDetails.title.replace(/[^a-zA-Z0-9]/g, '_')}.${reportDetails.format}`
        : undefined;
      
      await reportingService.downloadAndSaveReport(reportId, filename);
    } catch (error) {
      console.error('Error downloading report:', error);
      setError('Failed to download report');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-400";
      case "generating":
        return "text-blue-400";
      case "failed":
        return "text-red-400";
      default:
        return "text-gray-400";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-400" />;
      case "generating":
        return <Loader2 className="h-4 w-4 text-blue-400 animate-spin" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-400" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 8) return "text-red-400";
    if (score >= 6) return "text-orange-400";
    if (score >= 4) return "text-yellow-400";
    return "text-green-400";
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour12: false,
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const formatDate = (date: Date | string) => {
    const d = typeof date === 'string' ? new Date(date) : date;
    return d.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return "Unknown";
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`;
  };

  if (loading) {
    return (
      <PageLayout>
        <div className="flex items-center justify-center h-96">
          <Loader2 className="h-8 w-8 animate-spin text-blue-400" />
          <span className="ml-2 text-lg">Loading reports...</span>
        </div>
      </PageLayout>
    );
  }

  return (
    <PageLayout>
      <div className="space-y-6">
        {/* Header */}
        <PageHeader
          title="Enterprise Reports"
          description="Generate comprehensive security reports with digital signatures and watermarks"
        >
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${serviceHealth ? 'bg-green-400' : 'bg-red-400'}`} />
              <span className="text-sm text-gray-400">
                Service {serviceHealth ? 'Online' : 'Offline'}
              </span>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-400">Current Time</div>
              <div className="text-lg font-mono">
                {formatTime(currentTime)}
              </div>
            </div>
          </div>
        </PageHeader>

        {/* Error Alert */}
        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-400" />
              <span className="text-red-400">{error}</span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setError(null)}
                className="ml-auto text-red-400 hover:text-red-300"
              >
                ×
              </Button>
            </div>
          </div>
        )}

        {/* Main Content */}
        <Tabs defaultValue="generate" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="generate">Generate Report</TabsTrigger>
            <TabsTrigger value="reports">Generated Reports</TabsTrigger>
            <TabsTrigger value="templates">Templates</TabsTrigger>
          </TabsList>

          {/* Generate Report Tab */}
          <TabsContent value="generate" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Report Generation Form */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Plus className="h-5 w-5" />
                    Generate New Report
                  </CardTitle>
                  <CardDescription>
                    Create professional security reports with customizable formats and themes
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Scan Selection */}
                  <div className="space-y-2">
                    <Label>Select Scan</Label>
                    <select
                      value={selectedScan}
                      onChange={(e) => setSelectedScan(e.target.value)}
                      className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg"
                    >
                      <option value="">Choose a scan...</option>
                      {scanResults.map((scan) => (
                        <option key={scan.id} value={scan.id}>
                          {scan.contractName} - {scan.address.slice(0, 10)}...
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Format Selection */}
                  <div className="space-y-2">
                    <Label>Format</Label>
                    <select
                      value={selectedFormat}
                      onChange={(e) => setSelectedFormat(e.target.value)}
                      className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg"
                    >
                      <option value="pdf">PDF</option>
                      <option value="html">HTML</option>
                      <option value="json">JSON</option>
                      <option value="sarif">SARIF</option>
                      <option value="csv">CSV</option>
                      <option value="markdown">Markdown</option>
                    </select>
                  </div>

                  {/* Theme Selection */}
                  <div className="space-y-2">
                    <Label>Theme</Label>
                    <select
                      value={selectedTheme}
                      onChange={(e) => setSelectedTheme(e.target.value)}
                      className="w-full p-2 bg-gray-800 border border-gray-700 rounded-lg"
                    >
                      <option value="dark_pro">Dark Professional</option>
                      <option value="light_corporate">Light Corporate</option>
                      <option value="corporate_blue">Corporate Blue</option>
                      <option value="security_red">Security Red</option>
                    </select>
                  </div>

                  {/* Options */}
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <Label>Digital Signature</Label>
                      <Switch
                        checked={includeSignature}
                        onCheckedChange={setIncludeSignature}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <Label>Watermark</Label>
                      <Switch
                        checked={includeWatermark}
                        onCheckedChange={setIncludeWatermark}
                      />
                    </div>
                  </div>

                  {/* Generate Button */}
                  <Button
                    onClick={handleGenerateReport}
                    disabled={!selectedScan || isGenerating}
                    className="w-full"
                  >
                    {isGenerating ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <FileText className="h-4 w-4 mr-2" />
                        Generate Report
                      </>
                    )}
                  </Button>

                  {/* Progress Bar */}
                  {isGenerating && (
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Generation Progress</span>
                        <span>{generationProgress}%</span>
                      </div>
                      <Progress value={generationProgress} className="w-full" />
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Recent Scans */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Database className="h-5 w-5" />
                    Available Scans
                  </CardTitle>
                  <CardDescription>
                    Recent vulnerability scans available for reporting
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {scanResults.slice(0, 5).map((scan) => (
                      <div
                        key={scan.id}
                        className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg"
                      >
                        <div>
                          <div className="font-medium">{scan.contractName}</div>
                          <div className="text-sm text-gray-400">
                            {scan.address.slice(0, 20)}...
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`text-sm ${getRiskColor(scan.riskScore)}`}>
                            Risk: {scan.riskScore}/10
                          </div>
                          <div className="text-xs text-gray-500">
                            {formatDate(scan.scanDate)}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          {/* Generated Reports Tab */}
          <TabsContent value="reports" className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Generated Reports</h3>
                <p className="text-sm text-gray-400">
                  {generatedReports.length} reports generated
                </p>
              </div>
              <Button onClick={loadGeneratedReports} variant="outline" size="sm">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {generatedReports.map((report) => (
                <Card key={report.id}>
                  <CardHeader className="pb-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getStatusIcon(report.status)}
                        <Badge variant="secondary" className="text-xs">
                          {report.format.toUpperCase()}
                        </Badge>
                      </div>
                      <div className="text-xs text-gray-400">
                        {formatDate(report.created_at)}
                      </div>
                    </div>
                    <CardTitle className="text-sm">{report.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Size:</span>
                      <span>{formatFileSize(report.file_size)}</span>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Downloads:</span>
                      <span>{report.download_count}</span>
                    </div>
                    {report.findings && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Findings:</span>
                        <span className="flex items-center gap-1">
                          {report.findings.critical > 0 && (
                            <span className="text-red-400">{report.findings.critical}C</span>
                          )}
                          {report.findings.high > 0 && (
                            <span className="text-orange-400">{report.findings.high}H</span>
                          )}
                          {report.findings.medium > 0 && (
                            <span className="text-yellow-400">{report.findings.medium}M</span>
                          )}
                          {report.findings.low > 0 && (
                            <span className="text-green-400">{report.findings.low}L</span>
                          )}
                        </span>
                      </div>
                    )}
                    <div className="flex items-center gap-2 pt-2">
                      <Button
                        size="sm"
                        onClick={() => handleDownloadReport(report.id)}
                        disabled={report.status !== 'completed'}
                        className="flex-1"
                      >
                        <Download className="h-3 w-3 mr-1" />
                        Download
                      </Button>
                      {report.signed_by && (
                        <div className="flex items-center gap-1 text-xs text-green-400">
                          <Signature className="h-3 w-3" />
                          Signed
                        </div>
                      )}
                      {report.watermarked && (
                        <div className="flex items-center gap-1 text-xs text-blue-400">
                          <Droplets className="h-3 w-3" />
                          Watermarked
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Templates Tab */}
          <TabsContent value="templates" className="space-y-6">
            <div>
              <h3 className="text-lg font-semibold">Report Templates</h3>
              <p className="text-sm text-gray-400">
                {reportTemplates.length} templates available
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {reportTemplates.map((template) => (
                <Card key={template.id}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-sm">{template.name}</CardTitle>
                      <Badge variant="outline">
                        {template.type}
                      </Badge>
                    </div>
                    <CardDescription className="text-xs">
                      {template.description}
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Popularity:</span>
                      <div className="flex items-center gap-1">
                        <Star className="h-3 w-3 text-yellow-400" />
                        <span>{template.popularity}%</span>
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-400">Formats:</span>
                      <span className="text-xs">
                        {template.formats.join(', ').toUpperCase()}
                      </span>
                    </div>
                    {template.lastUsed && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-gray-400">Last Used:</span>
                        <span className="text-xs">
                          {formatDate(template.lastUsed)}
                        </span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </PageLayout>
  );
};

export default Reports;
