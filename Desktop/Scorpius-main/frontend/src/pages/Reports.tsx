import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { StorageManager } from "@/lib/storage";
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

interface ReportTemplate {
  id: string;
  name: string;
  description: string;
  type: "security" | "compliance" | "audit" | "executive";
  formats: string[];
  theme: string;
  lastUsed?: Date;
  popularity: number;
}

interface GeneratedReport {
  id: string;
  title: string;
  scanId: string;
  format: string;
  theme: string;
  status: "generating" | "completed" | "failed" | "signed";
  createdAt: Date;
  size: string;
  downloadCount: number;
  signedBy?: string;
  watermarked: boolean;
  findings: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    total: number;
  };
}

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

  // Report templates from API
  const [reportTemplates, setReportTemplates] = useState<ReportTemplate[]>([
    {
      id: "security_audit",
      name: "Security Audit Report",
      description: "Comprehensive security analysis with vulnerability details",
      type: "security",
      formats: ["pdf", "html", "json", "sarif"],
      theme: "dark_pro",
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 2),
      popularity: 95,
    },
    {
      id: "compliance_report",
      name: "Compliance Assessment",
      description: "Regulatory compliance evaluation and recommendations",
      type: "compliance",
      formats: ["pdf", "html", "csv"],
      theme: "light_corporate",
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 24),
      popularity: 78,
    },
    {
      id: "executive_summary",
      name: "Executive Summary",
      description: "High-level overview for management and stakeholders",
      type: "executive",
      formats: ["pdf", "html"],
      theme: "corporate_blue",
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3),
      popularity: 84,
    },
    {
      id: "technical_deep_dive",
      name: "Technical Deep Dive",
      description: "Detailed technical analysis for development teams",
      type: "audit",
      formats: ["pdf", "html", "markdown", "json"],
      theme: "dark_pro",
      lastUsed: new Date(Date.now() - 1000 * 60 * 60 * 12),
      popularity: 91,
    },
  ]);

  const [scanResults, setScanResults] = useState<ScanResult[]>([
    {
      id: "SCAN_2024_001",
      contractName: "UniswapV3Pool",
      address: "0x742d35Cc6431C8BF3240C39B6969E3C77e1345eF",
      scanDate: new Date(Date.now() - 1000 * 60 * 60 * 2),
      status: "completed",
      findings: { critical: 2, high: 5, medium: 12, low: 8, total: 27 },
      riskScore: 8.5,
    },
    {
      id: "SCAN_2024_002",
      contractName: "AaveV3Pool",
      address: "0x9F8b2C4D5E6A7B8C9D0E1F2A3B4C5D6E7F8A9B0C",
      scanDate: new Date(Date.now() - 1000 * 60 * 60 * 24),
      status: "completed",
      findings: { critical: 0, high: 3, medium: 8, low: 15, total: 26 },
      riskScore: 6.2,
    },
    {
      id: "SCAN_2024_003",
      contractName: "CompoundProtocol",
      address: "0x7E8F9A0B1C2D3E4F5A6B7C8D9E0F1A2B3C4D5E6F",
      scanDate: new Date(Date.now() - 1000 * 60 * 60 * 6),
      status: "completed",
      findings: { critical: 1, high: 4, medium: 10, low: 12, total: 27 },
      riskScore: 7.3,
    },
  ]);

  const [generatedReports, setGeneratedReports] = useState<GeneratedReport[]>([
    {
      id: "RPT_001",
      title: "UniswapV3Pool Security Audit",
      scanId: "SCAN_2024_001",
      format: "pdf",
      theme: "dark_pro",
      status: "signed",
      createdAt: new Date(Date.now() - 1000 * 60 * 60),
      size: "2.4 MB",
      downloadCount: 12,
      signedBy: "security@scorpius.dev",
      watermarked: true,
      findings: { critical: 2, high: 5, medium: 12, low: 8, total: 27 },
    },
    {
      id: "RPT_002",
      title: "AaveV3Pool Compliance Report",
      scanId: "SCAN_2024_002",
      format: "html",
      theme: "light_corporate",
      status: "completed",
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 12),
      size: "1.8 MB",
      downloadCount: 8,
      watermarked: false,
      findings: { critical: 0, high: 3, medium: 8, low: 15, total: 26 },
    },
    {
      id: "RPT_003",
      title: "CompoundProtocol Executive Summary",
      scanId: "SCAN_2024_003",
      format: "pdf",
      theme: "corporate_blue",
      status: "completed",
      createdAt: new Date(Date.now() - 1000 * 60 * 60 * 3),
      size: "912 KB",
      downloadCount: 15,
      watermarked: true,
      findings: { critical: 1, high: 4, medium: 10, low: 12, total: 27 },
    },
  ]);

  const [reportStats, setReportStats] = useState({
    totalReports: 0,
    reportsToday: 0,
    avgGenerationTime: 0,
    popularFormat: "PDF",
    popularTheme: "Dark Pro",
    totalDownloads: 0,
  });

  // Load data from APIs
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load report templates
        const templatesResponse = await fetch(
          `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/reports/templates`,
        );
        if (templatesResponse.ok) {
          const templatesData = await templatesResponse.json();
          if (templatesData.success && templatesData.data) {
            setReportTemplates(templatesData.data);
          }
        }

        // Load scan results
        const scansResponse = await fetch(
          `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/scanner/recent?limit=10`,
        );
        if (scansResponse.ok) {
          const scansData = await scansResponse.json();
          if (scansData.success && scansData.data) {
            setScanResults(scansData.data);
          }
        }

        // Load generated reports
        const reportsResponse = await fetch(
          `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/reports/generated?limit=10`,
        );
        if (reportsResponse.ok) {
          const reportsData = await reportsResponse.json();
          if (reportsData.success && reportsData.data) {
            setGeneratedReports(reportsData.data);
          }
        }

        // Load report statistics (merge API with persistent data)
        const localReportStats = StorageManager.getReportStats();
        setReportStats({
          totalReports: localReportStats.totalReports,
          reportsToday: localReportStats.reportsToday,
          avgGenerationTime: localReportStats.averageGenerationTime,
          popularFormat: "PDF",
          popularTheme: "Dark Pro",
          totalDownloads: localReportStats.totalDownloads,
        });

        try {
          const statsResponse = await fetch(
            `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}/api/reports/stats`,
          );
          if (statsResponse.ok) {
            const statsData = await statsResponse.json();
            if (statsData.success && statsData.data) {
              // Merge API stats with local persistent stats
              setReportStats((prev) => ({
                ...prev,
                ...statsData.data,
                totalReports: Math.max(
                  prev.totalReports,
                  statsData.data.totalReports || 0,
                ),
                totalDownloads: Math.max(
                  prev.totalDownloads,
                  statsData.data.totalDownloads || 0,
                ),
              }));
            }
          }
        } catch (error) {
          console.warn("API stats unavailable, using local data");
        }
      } catch (error) {
        console.error("Failed to load reports data:", error);
      }
    };

    loadData();
  }, []);

  const themes = [
    {
      id: "dark_pro",
      name: "Dark Pro",
      description: "Professional dark theme",
    },
    {
      id: "light_corporate",
      name: "Light Corporate",
      description: "Clean corporate styling",
    },
    {
      id: "corporate_blue",
      name: "Corporate Blue",
      description: "Professional blue theme",
    },
    {
      id: "security_red",
      name: "Security Red",
      description: "High-contrast security theme",
    },
  ];

  const formats = [
    {
      id: "pdf",
      name: "PDF",
      description: "Professional reports with digital signatures",
      icon: FileText,
      features: ["Digital Signatures", "Watermarks", "Print Optimized"],
    },
    {
      id: "html",
      name: "HTML",
      description: "Interactive web-based reports",
      icon: Globe,
      features: ["Interactive Charts", "Search & Filter", "Responsive"],
    },
    {
      id: "json",
      name: "JSON",
      description: "Machine-readable structured data",
      icon: FileCode,
      features: ["API Integration", "Structured Data", "Programmatic Access"],
    },
    {
      id: "csv",
      name: "CSV",
      description: "Spreadsheet-compatible data export",
      icon: Database,
      features: ["Spreadsheet Ready", "Data Analysis", "Bulk Processing"],
    },
    {
      id: "sarif",
      name: "SARIF",
      description: "Industry-standard security format",
      icon: Shield,
      features: ["GitHub Integration", "Tool Compatibility", "Standardized"],
    },
    {
      id: "markdown",
      name: "Markdown",
      description: "Documentation-friendly format",
      icon: File,
      features: ["Version Control", "Documentation", "Developer Friendly"],
    },
  ];

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const generateReport = useCallback(async () => {
    if (!selectedScan) return;

    setIsGenerating(true);
    setGenerationProgress(0);

    // Simulate report generation
    const progressInterval = setInterval(() => {
      setGenerationProgress((prev) => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          setIsGenerating(false);

          // Calculate generation time (simulated)
          const generationTime = Math.random() * 30 + 15; // 15-45 seconds

          // Persist report generation in storage
          StorageManager.incrementReportGeneration(generationTime);

          // Add new report to the list
          const newReport: GeneratedReport = {
            id: `RPT_${Date.now()}`,
            title: `${
              scanResults.find((s) => s.id === selectedScan)?.contractName
            } Security Report`,
            scanId: selectedScan,
            format: selectedFormat,
            theme: selectedTheme,
            status: "completed",
            createdAt: new Date(),
            size: "1.2 MB",
            downloadCount: 0,
            watermarked: includeWatermark,
            signedBy: includeSignature ? "security@scorpius.dev" : undefined,
            findings: scanResults.find((s) => s.id === selectedScan)
              ?.findings || {
              critical: 0,
              high: 0,
              medium: 0,
              low: 0,
              total: 0,
            },
          };

          setGeneratedReports((prev) => [newReport, ...prev]);

          // Update stats from storage
          const updatedStats = StorageManager.getReportStats();
          setReportStats((prev) => ({
            ...prev,
            totalReports: updatedStats.totalReports,
            reportsToday: updatedStats.reportsToday,
            avgGenerationTime: updatedStats.averageGenerationTime,
          }));

          return 100;
        }
        return prev + Math.random() * 15;
      });
    }, 200);

    return () => clearInterval(progressInterval);
  }, [
    selectedScan,
    selectedFormat,
    selectedTheme,
    includeSignature,
    includeWatermark,
    scanResults,
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600";
      case "signed":
        return "text-blue-600";
      case "generating":
        return "text-yellow-600";
      case "failed":
        return "text-red-600";
      default:
        return "text-gray-600";
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4" />;
      case "signed":
        return <Signature className="h-4 w-4" />;
      case "generating":
        return <Loader2 className="h-4 w-4 animate-spin" />;
      case "failed":
        return <XCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 8) return "text-red-600";
    if (score >= 6) return "text-yellow-600";
    if (score >= 4) return "text-blue-600";
    return "text-green-600";
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) return `${diffDays}d ago`;
    if (diffHours > 0) return `${diffHours}h ago`;
    return `${Math.floor(diffMs / (1000 * 60))}m ago`;
  };

  return (
    <PageLayout variant="analytics">
      <PageHeader
        title="Enterprise Reporting System"
        description="Professional security audit reports and analytics"
        icon={FileText}
        iconGradient="from-indigo-500 to-purple-600"
        borderColor="border-indigo-400/30"
      />
      {/* Stats Dashboard */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-6 mb-8"
      >
        {[
          {
            label: "Total Reports",
            value: reportStats.totalReports,
            icon: FileText,
            color: "text-blue-600",
          },
          {
            label: "Reports Today",
            value: reportStats.reportsToday,
            icon: Calendar,
            color: "text-green-600",
          },
          {
            label: "Avg Gen Time",
            value: reportStats.avgGenerationTime,
            icon: Clock,
            color: "text-yellow-600",
            suffix: "s",
          },
          {
            label: "Popular Format",
            value: reportStats.popularFormat,
            icon: Star,
            color: "text-purple-600",
            isText: true,
          },
          {
            label: "Popular Theme",
            value: reportStats.popularTheme,
            icon: Award,
            color: "text-indigo-600",
            isText: true,
          },
          {
            label: "Total Downloads",
            value: reportStats.totalDownloads,
            icon: Download,
            color: "text-cyan-600",
          },
        ].map((stat, index) => (
          <motion.div
            key={stat.label}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3, delay: 0.1 * index }}
            whileHover={{ scale: 1.05, y: -5 }}
            className="bg-background/80 backdrop-blur border rounded-xl p-4 shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <div className="flex items-center justify-between mb-3">
              <div
                className={`p-2 rounded-lg bg-background border ${stat.color}`}
              >
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
              </div>
            </div>
            <div className="space-y-1">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ duration: 0.5, delay: 0.2 + index * 0.1 }}
                className={`text-2xl font-bold ${stat.color}`}
              >
                {stat.isText ? (
                  stat.value
                ) : (
                  <LiveCounter
                    value={Number(stat.value)}
                    suffix={stat.suffix}
                    decimals={0}
                    duration={2000}
                  />
                )}
              </motion.div>
              <div className="text-xs text-muted-foreground font-medium">
                {stat.label}
              </div>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Main Content Tabs */}
      <Tabs defaultValue="generate" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="generate">Generate Reports</TabsTrigger>
          <TabsTrigger value="history">Report History</TabsTrigger>
          <TabsTrigger value="templates">Templates</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Generate Reports Tab */}
        <TabsContent value="generate" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Report Configuration */}
            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Settings className="h-5 w-5" />
                  <span>Report Configuration</span>
                </CardTitle>
                <CardDescription>
                  Configure your security audit report settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Scan Selection */}
                <div className="space-y-3">
                  <Label className="text-sm font-medium">Select Scan</Label>
                  <div className="grid gap-3">
                    {scanResults.map((scan) => (
                      <motion.div
                        key={scan.id}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => setSelectedScan(scan.id)}
                        className={`p-4 border rounded-lg cursor-pointer transition-all ${
                          selectedScan === scan.id
                            ? "border-indigo-500 bg-indigo-500/10"
                            : "border-border hover:bg-muted/50"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <div>
                            <h4 className="font-semibold">
                              {scan.contractName}
                            </h4>
                            <p className="text-xs text-muted-foreground font-mono">
                              {scan.address}
                            </p>
                          </div>
                          <div className="text-right">
                            <div
                              className={`text-sm font-bold ${getRiskColor(scan.riskScore)}`}
                            >
                              Risk: {scan.riskScore}/10
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {formatTime(scan.scanDate)}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-4 text-xs">
                          <span className="text-red-600">
                            Critical: {scan.findings.critical}
                          </span>
                          <span className="text-yellow-600">
                            High: {scan.findings.high}
                          </span>
                          <span className="text-blue-600">
                            Medium: {scan.findings.medium}
                          </span>
                          <span className="text-green-600">
                            Low: {scan.findings.low}
                          </span>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Format Selection */}
                <div className="space-y-3">
                  <Label className="text-sm font-medium">Output Format</Label>
                  <div className="grid grid-cols-2 gap-3">
                    {formats.map((format) => (
                      <motion.div
                        key={format.id}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => setSelectedFormat(format.id)}
                        className={`p-3 border rounded-lg cursor-pointer transition-all ${
                          selectedFormat === format.id
                            ? "border-indigo-500 bg-indigo-500/10"
                            : "border-border hover:bg-muted/50"
                        }`}
                      >
                        <div className="flex items-center gap-3 mb-2">
                          <format.icon className="h-5 w-5 text-indigo-600" />
                          <div>
                            <h4 className="font-semibold">{format.name}</h4>
                            <p className="text-xs text-muted-foreground">
                              {format.description}
                            </p>
                          </div>
                        </div>
                        <div className="flex flex-wrap gap-1">
                          {format.features.map((feature) => (
                            <Badge
                              key={feature}
                              variant="secondary"
                              className="text-xs"
                            >
                              {feature}
                            </Badge>
                          ))}
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Theme Selection */}
                <div className="space-y-3">
                  <Label className="text-sm font-medium">Theme</Label>
                  <div className="grid grid-cols-2 gap-3">
                    {themes.map((theme) => (
                      <motion.div
                        key={theme.id}
                        whileHover={{ scale: 1.02 }}
                        onClick={() => setSelectedTheme(theme.id)}
                        className={`p-3 border rounded-lg cursor-pointer transition-all ${
                          selectedTheme === theme.id
                            ? "border-indigo-500 bg-indigo-500/10"
                            : "border-border hover:bg-muted/50"
                        }`}
                      >
                        <h4 className="font-semibold">{theme.name}</h4>
                        <p className="text-xs text-muted-foreground">
                          {theme.description}
                        </p>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Enterprise Options */}
                <div className="space-y-4">
                  <Label className="text-sm font-medium">
                    Enterprise Features
                  </Label>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Signature className="h-4 w-4 text-blue-600" />
                        <Label htmlFor="signature" className="text-sm">
                          Digital Signature
                        </Label>
                      </div>
                      <Switch
                        id="signature"
                        checked={includeSignature}
                        onCheckedChange={setIncludeSignature}
                      />
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Droplets className="h-4 w-4 text-purple-600" />
                        <Label htmlFor="watermark" className="text-sm">
                          Watermark
                        </Label>
                      </div>
                      <Switch
                        id="watermark"
                        checked={includeWatermark}
                        onCheckedChange={setIncludeWatermark}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Generation Panel */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Zap className="h-5 w-5" />
                  <span>Generate Report</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {!isGenerating ? (
                  <>
                    <div className="space-y-3">
                      <div className="text-sm">
                        <strong>Selected Configuration:</strong>
                      </div>
                      <div className="space-y-2 text-xs">
                        <div>
                          Scan:{" "}
                          {scanResults.find((s) => s.id === selectedScan)
                            ?.contractName || "None selected"}
                        </div>
                        <div>Format: {selectedFormat.toUpperCase()}</div>
                        <div>
                          Theme:{" "}
                          {themes.find((t) => t.id === selectedTheme)?.name}
                        </div>
                        <div>
                          Signature: {includeSignature ? "Enabled" : "Disabled"}
                        </div>
                        <div>
                          Watermark: {includeWatermark ? "Enabled" : "Disabled"}
                        </div>
                      </div>
                    </div>

                    <Button
                      onClick={generateReport}
                      disabled={!selectedScan}
                      className="w-full bg-gradient-to-r from-indigo-600 to-purple-600"
                    >
                      <Zap className="h-4 w-4 mr-2" />
                      Generate Report
                    </Button>
                  </>
                ) : (
                  <div className="space-y-4">
                    <div className="text-sm font-medium">
                      Generating Report...
                    </div>
                    <Progress value={generationProgress} className="h-2" />
                    <div className="text-xs text-muted-foreground">
                      {Math.round(generationProgress)}% complete
                    </div>
                  </div>
                )}

                {/* Quick Actions */}
                <div className="space-y-2 pt-4 border-t">
                  <div className="text-sm font-medium">Quick Actions</div>
                  <div className="space-y-2">
                    <Button variant="outline" size="sm" className="w-full">
                      <Package className="h-4 w-4 mr-2" />
                      Generate Audit Bundle
                    </Button>
                    <Button variant="outline" size="sm" className="w-full">
                      <GitCompare className="h-4 w-4 mr-2" />
                      Create Diff Report
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Report History Tab */}
        <TabsContent value="history" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    <Clock className="h-5 w-5" />
                    <span>Report History</span>
                  </CardTitle>
                  <CardDescription>
                    Manage and download previously generated reports
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Filter
                  </Button>
                  <Button variant="outline" size="sm">
                    <RefreshCw className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {generatedReports.map((report, index) => (
                  <motion.div
                    key={report.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: 0.1 * index }}
                    className="p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center space-x-3">
                        <div
                          className={`p-2 rounded ${getStatusColor(report.status)}`}
                        >
                          {getStatusIcon(report.status)}
                        </div>
                        <div>
                          <h4 className="font-semibold">{report.title}</h4>
                          <p className="text-sm text-muted-foreground">
                            {report.format.toUpperCase()} • {report.theme} •{" "}
                            {report.size}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {report.watermarked && (
                          <Badge variant="outline" className="text-xs">
                            <Droplets className="h-3 w-3 mr-1" />
                            Watermarked
                          </Badge>
                        )}
                        {report.signedBy && (
                          <Badge variant="outline" className="text-xs">
                            <Signature className="h-3 w-3 mr-1" />
                            Signed
                          </Badge>
                        )}
                        <Button variant="outline" size="sm">
                          <Download className="h-4 w-4 mr-2" />
                          Download
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <div className="flex items-center space-x-4">
                        <span>Generated: {formatTime(report.createdAt)}</span>
                        <span>Downloads: {report.downloadCount}</span>
                        {report.signedBy && (
                          <span>Signed by: {report.signedBy}</span>
                        )}
                      </div>
                      <div className="flex items-center space-x-3">
                        <span className="text-red-600">
                          Critical: {report.findings.critical}
                        </span>
                        <span className="text-yellow-600">
                          High: {report.findings.high}
                        </span>
                        <span className="text-blue-600">
                          Medium: {report.findings.medium}
                        </span>
                        <span className="text-green-600">
                          Low: {report.findings.low}
                        </span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Briefcase className="h-5 w-5" />
                <span>Report Templates</span>
              </CardTitle>
              <CardDescription>
                Professional templates for different types of reports
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {reportTemplates.map((template, index) => (
                  <motion.div
                    key={template.id}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.3, delay: 0.1 * index }}
                    whileHover={{ scale: 1.02, y: -5 }}
                    className="p-6 border rounded-xl bg-gradient-to-br from-background to-muted/50 hover:shadow-lg transition-all"
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div>
                        <h3 className="font-semibold text-lg">
                          {template.name}
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          {template.description}
                        </p>
                      </div>
                      <Badge variant="secondary">{template.type}</Badge>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span>Popularity</span>
                        <div className="flex items-center space-x-2">
                          <Progress
                            value={template.popularity}
                            className="w-16 h-2"
                          />
                          <span className="text-xs">
                            {template.popularity}%
                          </span>
                        </div>
                      </div>

                      {template.lastUsed && (
                        <div className="flex items-center justify-between text-sm">
                          <span>Last Used</span>
                          <span className="text-muted-foreground">
                            {formatTime(template.lastUsed)}
                          </span>
                        </div>
                      )}

                      <div className="flex flex-wrap gap-1">
                        {template.formats.map((format) => (
                          <Badge
                            key={format}
                            variant="outline"
                            className="text-xs"
                          >
                            {format.toUpperCase()}
                          </Badge>
                        ))}
                      </div>

                      <Button className="w-full" variant="outline">
                        <FileText className="h-4 w-4 mr-2" />
                        Use Template
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Report Generation Trends */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5" />
                  <span>Generation Trends</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto text-indigo-600 mb-4" />
                    <p className="text-sm text-muted-foreground">
                      Report Generation Chart
                    </p>
                    <div className="grid grid-cols-2 gap-4 mt-4 text-sm">
                      <div>
                        <div className="font-bold text-indigo-600">347</div>
                        <div className="text-muted-foreground">
                          Total Reports
                        </div>
                      </div>
                      <div>
                        <div className="font-bold text-purple-600">23</div>
                        <div className="text-muted-foreground">Today</div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Format Distribution */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <PieChart className="h-5 w-5" />
                  <span>Format Distribution</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 bg-gradient-to-br from-green-100 to-blue-100 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <PieChart className="h-12 w-12 mx-auto text-green-600 mb-4" />
                    <p className="text-sm text-muted-foreground">
                      Format Usage Chart
                    </p>
                    <div className="grid grid-cols-3 gap-2 mt-4 text-xs">
                      <div>
                        <div className="font-bold text-blue-600">45%</div>
                        <div className="text-muted-foreground">PDF</div>
                      </div>
                      <div>
                        <div className="font-bold text-green-600">28%</div>
                        <div className="text-muted-foreground">HTML</div>
                      </div>
                      <div>
                        <div className="font-bold text-purple-600">27%</div>
                        <div className="text-muted-foreground">Other</div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Performance Metrics */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Activity className="h-5 w-5" />
                <span>Performance Metrics</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-center">
                <div>
                  <div className="text-3xl font-bold text-blue-600 mb-2">
                    <LiveCounter
                      value={45}
                      suffix="s"
                      decimals={0}
                      duration={2000}
                    />
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Avg Generation Time
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    <LiveCounter
                      value={99.2}
                      suffix="%"
                      decimals={1}
                      duration={2000}
                    />
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Success Rate
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-purple-600 mb-2">
                    <LiveCounter value={2847} decimals={0} duration={2000} />
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Total Downloads
                  </div>
                </div>
                <div>
                  <div className="text-3xl font-bold text-cyan-600 mb-2">
                    <LiveCounter
                      value={1.2}
                      suffix="MB"
                      decimals={1}
                      duration={2000}
                    />
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Avg Report Size
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </PageLayout>
  );
};

export default Reports;
