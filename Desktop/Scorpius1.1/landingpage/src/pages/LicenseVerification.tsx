import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  Shield,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Loader2,
  Scan,
  FileText,
  Calendar,
  User,
  Building,
  Key,
  Lock,
  Unlock,
  Clock,
  Database,
  Server,
  Globe,
  ArrowLeft,
  Upload,
  Download,
} from "lucide-react";
import { ParticleField, FloatingOrbs } from "@/components/ui/particle-effects";
import { Link, useNavigate } from "react-router-dom";
import { useLicenseVerification } from "@/hooks";
import { toast } from "sonner";
import type { LicenseInfo } from "@/lib/api/types";

const LicenseVerification = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [verificationStep, setVerificationStep] = useState<
    "input" | "scanning" | "results"
  >("input");
  const [licenseKey, setLicenseKey] = useState("");
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [verificationMethod, setVerificationMethod] = useState<"key" | "file">(
    "key",
  );
  const [progress, setProgress] = useState(0);
  const [licenseInfo, setLicenseInfo] = useState<LicenseInfo | null>(null);

  const navigate = useNavigate();

  // API Hook for license verification
  const licenseVerificationMutation = useLicenseVerification({
    onSuccess: (data) => {
      if (data.success && data.data) {
        setLicenseInfo(data.data);
        setVerificationStep("results");
        toast.success("License verified successfully!");
      }
    },
    onError: (error) => {
      toast.error(error.message || "License verification failed");
      setVerificationStep("input");
      setProgress(0);
    },
  });

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Simulate progress during verification
  useEffect(() => {
    if (
      licenseVerificationMutation.isPending &&
      verificationStep === "scanning"
    ) {
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) return prev; // Stop at 90% until actual response
          return prev + Math.random() * 10;
        });
      }, 300);

      return () => clearInterval(interval);
    }
  }, [licenseVerificationMutation.isPending, verificationStep]);

  const handleVerification = async () => {
    if (verificationMethod === "key" && !licenseKey.trim()) {
      toast.error("Please enter a license key");
      return;
    }

    if (verificationMethod === "file" && !uploadedFile) {
      toast.error("Please upload a license file");
      return;
    }

    setProgress(0);
    setVerificationStep("scanning");

    const verificationData = {
      license_key: verificationMethod === "key" ? licenseKey : undefined,
      license_file: verificationMethod === "file" ? uploadedFile : undefined,
    };

    licenseVerificationMutation.mutate(verificationData);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "active":
        return "text-green-400 bg-green-400/10 border-green-400/30";
      case "expired":
        return "text-red-400 bg-red-400/10 border-red-400/30";
      case "pending":
        return "text-yellow-400 bg-yellow-400/10 border-yellow-400/30";
      default:
        return "text-gray-400 bg-gray-400/10 border-gray-400/30";
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "enterprise":
        return "text-purple-400 bg-purple-400/10 border-purple-400/30";
      case "professional":
        return "text-blue-400 bg-blue-400/10 border-blue-400/30";
      case "standard":
        return "text-cyan-400 bg-cyan-400/10 border-cyan-400/30";
      default:
        return "text-gray-400 bg-gray-400/10 border-gray-400/30";
    }
  };

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900/20 to-pink-900/20" />
      <ParticleField
        particleCount={50}
        colors={["#a855f7", "#ec4899", "#06b6d4", "#22c55e"]}
        className="opacity-30"
      />
      <FloatingOrbs orbCount={3} className="opacity-20" />

      {/* Grid Pattern */}
      <div
        className="absolute inset-0 opacity-10"
        style={{
          backgroundImage: `
            linear-gradient(rgba(168, 85, 247, 0.3) 1px, transparent 1px),
            linear-gradient(90deg, rgba(168, 85, 247, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: "30px 30px",
        }}
      />

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-8"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Link to="/login">
                <Button
                  variant="outline"
                  size="sm"
                  className="border-purple-500/30"
                >
                  <ArrowLeft className="h-4 w-4 mr-2" />
                  Back to Login
                </Button>
              </Link>
              <div className="flex items-center space-x-3">
                <div className="p-3 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-600 shadow-lg">
                  <Scan className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                    License Verification
                  </h1>
                  <p className="text-muted-foreground">
                    Validate your Scorpius X license
                  </p>
                </div>
              </div>
            </div>

            <div className="text-right text-sm text-muted-foreground">
              <div>{currentTime.toLocaleDateString()}</div>
              <div>{currentTime.toLocaleTimeString()}</div>
            </div>
          </div>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          <AnimatePresence mode="wait">
            {verificationStep === "input" && (
              <motion.div
                key="input"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
              >
                <Card className="bg-background/80 backdrop-blur border-purple-500/20 shadow-2xl">
                  <CardHeader>
                    <CardTitle className="text-2xl font-bold text-center">
                      Verify Your License
                    </CardTitle>
                    <p className="text-center text-muted-foreground">
                      Choose your verification method to access the platform
                    </p>
                  </CardHeader>

                  <CardContent className="space-y-6">
                    {/* Verification Method Selector */}
                    <div className="flex space-x-2 p-1 bg-background/50 rounded-lg">
                      {[
                        { id: "key", label: "License Key", icon: Key },
                        { id: "file", label: "License File", icon: FileText },
                      ].map((method) => (
                        <button
                          key={method.id}
                          onClick={() =>
                            setVerificationMethod(method.id as any)
                          }
                          className={`flex-1 flex items-center justify-center space-x-2 py-3 px-4 rounded-md text-sm font-medium transition-all duration-200 ${
                            verificationMethod === method.id
                              ? "bg-purple-500/20 text-purple-400 border border-purple-500/30"
                              : "text-muted-foreground hover:text-foreground hover:bg-background/50"
                          }`}
                        >
                          <method.icon className="h-4 w-4" />
                          <span>{method.label}</span>
                        </button>
                      ))}
                    </div>

                    {/* Input Methods */}
                    <AnimatePresence mode="wait">
                      {verificationMethod === "key" && (
                        <motion.div
                          key="key-input"
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: 20 }}
                          transition={{ duration: 0.3 }}
                          className="space-y-4"
                        >
                          <div className="space-y-2">
                            <Label
                              htmlFor="license-key"
                              className="text-foreground"
                            >
                              License Key
                            </Label>
                            <div className="relative">
                              <Key className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                              <Input
                                id="license-key"
                                type="text"
                                placeholder="SX-ENT-2024-XXXX or paste your license key"
                                value={licenseKey}
                                onChange={(e) => setLicenseKey(e.target.value)}
                                className="pl-10 bg-background/50 border-purple-500/20 focus:border-purple-500/50 font-mono"
                              />
                            </div>
                            <p className="text-xs text-muted-foreground">
                              Enter your Scorpius X license key (format:
                              SX-XXX-YYYY-ZZZZ)
                            </p>
                          </div>
                        </motion.div>
                      )}

                      {verificationMethod === "file" && (
                        <motion.div
                          key="file-input"
                          initial={{ opacity: 0, x: 20 }}
                          animate={{ opacity: 1, x: 0 }}
                          exit={{ opacity: 0, x: -20 }}
                          transition={{ duration: 0.3 }}
                          className="space-y-4"
                        >
                          <div className="space-y-2">
                            <Label
                              htmlFor="license-file"
                              className="text-foreground"
                            >
                              License File
                            </Label>
                            <div className="border-2 border-dashed border-purple-500/30 rounded-lg p-6 text-center hover:border-purple-500/50 transition-colors">
                              <input
                                id="license-file"
                                type="file"
                                accept=".lic,.license,.xml,.json"
                                onChange={handleFileUpload}
                                className="hidden"
                              />
                              <label
                                htmlFor="license-file"
                                className="cursor-pointer"
                              >
                                {uploadedFile ? (
                                  <div className="space-y-2">
                                    <CheckCircle2 className="h-8 w-8 text-green-400 mx-auto" />
                                    <p className="font-medium">
                                      {uploadedFile.name}
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                      {(uploadedFile.size / 1024).toFixed(1)} KB
                                    </p>
                                  </div>
                                ) : (
                                  <div className="space-y-2">
                                    <Upload className="h-8 w-8 text-purple-400 mx-auto" />
                                    <p className="font-medium">
                                      Click to upload license file
                                    </p>
                                    <p className="text-xs text-muted-foreground">
                                      Supports .lic, .license, .xml, .json files
                                    </p>
                                  </div>
                                )}
                              </label>
                            </div>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>

                    {licenseVerificationMutation.isError && (
                      <Alert className="border-red-500/20 bg-red-500/10">
                        <XCircle className="h-4 w-4 text-red-500" />
                        <AlertDescription className="text-red-400">
                          {licenseVerificationMutation.error?.message ||
                            "Verification failed"}
                        </AlertDescription>
                      </Alert>
                    )}

                    <Button
                      onClick={handleVerification}
                      disabled={
                        licenseVerificationMutation.isPending ||
                        (verificationMethod === "key" && !licenseKey) ||
                        (verificationMethod === "file" && !uploadedFile)
                      }
                      className="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white"
                    >
                      {licenseVerificationMutation.isPending ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Verifying...
                        </>
                      ) : (
                        <>
                          <Scan className="mr-2 h-4 w-4" />
                          Verify License
                        </>
                      )}
                    </Button>

                    {/* Sample License Key */}
                    <div className="pt-4 border-t border-purple-500/20">
                      <div className="text-xs text-muted-foreground text-center space-y-1">
                        <p>
                          For demo purposes, try:{" "}
                          <code className="bg-background/50 px-2 py-1 rounded">
                            SX-ENT-2024-7891
                          </code>
                        </p>
                        <p>Or upload any file named "license.lic"</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {verificationStep === "scanning" && (
              <motion.div
                key="scanning"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 1.1 }}
                transition={{ duration: 0.5 }}
              >
                <Card className="bg-background/80 backdrop-blur border-purple-500/20 shadow-2xl">
                  <CardContent className="p-8">
                    <div className="text-center space-y-6">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{
                          duration: 2,
                          repeat: Infinity,
                          ease: "linear",
                        }}
                        className="mx-auto w-24 h-24 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-600/20 border border-purple-500/30 flex items-center justify-center"
                      >
                        <Scan className="h-12 w-12 text-purple-400" />
                      </motion.div>

                      <div>
                        <h3 className="text-2xl font-bold mb-2">
                          Verifying License
                        </h3>
                        <p className="text-muted-foreground">
                          Please wait while we validate your license...
                        </p>
                      </div>

                      <div className="space-y-2">
                        <Progress value={progress} className="h-2" />
                        <p className="text-sm text-purple-400">
                          {progress.toFixed(0)}% Complete
                        </p>
                      </div>

                      <div className="grid grid-cols-3 gap-4 text-xs">
                        <div className="space-y-1">
                          <div className="w-2 h-2 rounded-full bg-green-400 mx-auto" />
                          <p>Format Check</p>
                        </div>
                        <div className="space-y-1">
                          <div
                            className={`w-2 h-2 rounded-full mx-auto ${progress > 40 ? "bg-green-400" : "bg-gray-600"}`}
                          />
                          <p>Signature</p>
                        </div>
                        <div className="space-y-1">
                          <div
                            className={`w-2 h-2 rounded-full mx-auto ${progress > 80 ? "bg-green-400" : "bg-gray-600"}`}
                          />
                          <p>Authority</p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}

            {verificationStep === "results" && licenseInfo && (
              <motion.div
                key="results"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
                className="space-y-6"
              >
                {/* Verification Success */}
                <Card className="bg-background/80 backdrop-blur border-green-500/20 shadow-2xl">
                  <CardContent className="p-6">
                    <div className="flex items-center space-x-4">
                      <div className="p-3 rounded-full bg-green-500/20">
                        <CheckCircle2 className="h-8 w-8 text-green-400" />
                      </div>
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-green-400">
                          License Verified Successfully
                        </h3>
                        <p className="text-muted-foreground">
                          Your license is valid and active
                        </p>
                      </div>
                      <Button className="bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white">
                        <Unlock className="mr-2 h-4 w-4" />
                        Access Platform
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* License Details */}
                <div className="grid lg:grid-cols-2 gap-6">
                  {/* Basic Information */}
                  <Card className="bg-background/80 backdrop-blur border-purple-500/20">
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <FileText className="h-5 w-5" />
                        <span>License Information</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-muted-foreground">
                            License ID
                          </Label>
                          <p className="font-mono text-sm">{licenseInfo.id}</p>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">
                            Status
                          </Label>
                          <Badge className={getStatusColor(licenseInfo.status)}>
                            {licenseInfo.status.toUpperCase()}
                          </Badge>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-muted-foreground">Type</Label>
                          <Badge className={getTypeColor(licenseInfo.type)}>
                            {licenseInfo.type.toUpperCase()}
                          </Badge>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">
                            Organization
                          </Label>
                          <p className="text-sm">{licenseInfo.organization}</p>
                        </div>
                      </div>

                      <Separator />

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-muted-foreground">
                            License Holder
                          </Label>
                          <div className="flex items-center space-x-2">
                            <User className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">
                              {licenseInfo.holder}
                            </span>
                          </div>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">Users</Label>
                          <div className="flex items-center space-x-2">
                            <span className="text-sm">
                              {licenseInfo.current_users} /{" "}
                              {licenseInfo.max_users}
                            </span>
                            <div className="flex-1 h-2 bg-background/50 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-green-500 to-emerald-600"
                                style={{
                                  width: `${(licenseInfo.current_users / licenseInfo.max_users) * 100}%`,
                                }}
                              />
                            </div>
                          </div>
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <Label className="text-muted-foreground">
                            Issued Date
                          </Label>
                          <div className="flex items-center space-x-2">
                            <Calendar className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">
                              {licenseInfo.issued_date}
                            </span>
                          </div>
                        </div>
                        <div>
                          <Label className="text-muted-foreground">
                            Expiry Date
                          </Label>
                          <div className="flex items-center space-x-2">
                            <Clock className="h-4 w-4 text-muted-foreground" />
                            <span className="text-sm">
                              {licenseInfo.expiry_date}
                            </span>
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Features & Capabilities */}
                  <Card className="bg-background/80 backdrop-blur border-purple-500/20">
                    <CardHeader>
                      <CardTitle className="flex items-center space-x-2">
                        <Shield className="h-5 w-5" />
                        <span>Licensed Features</span>
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {licenseInfo.features.map((feature, index) => (
                          <motion.div
                            key={feature}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: index * 0.1 }}
                            className="flex items-center space-x-3 p-2 rounded-lg bg-background/50"
                          >
                            <CheckCircle2 className="h-4 w-4 text-green-400 flex-shrink-0" />
                            <span className="text-sm">{feature}</span>
                          </motion.div>
                        ))}
                      </div>

                      <Separator className="my-4" />

                      <div className="grid grid-cols-3 gap-4 text-center">
                        <div className="space-y-1">
                          <Database className="h-6 w-6 text-cyan-400 mx-auto" />
                          <p className="text-xs text-muted-foreground">
                            Data Access
                          </p>
                          <p className="text-sm font-medium">Unlimited</p>
                        </div>
                        <div className="space-y-1">
                          <Server className="h-6 w-6 text-blue-400 mx-auto" />
                          <p className="text-xs text-muted-foreground">
                            API Calls
                          </p>
                          <p className="text-sm font-medium">1M/month</p>
                        </div>
                        <div className="space-y-1">
                          <Globe className="h-6 w-6 text-purple-400 mx-auto" />
                          <p className="text-xs text-muted-foreground">
                            Regions
                          </p>
                          <p className="text-sm font-medium">Global</p>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Actions */}
                <Card className="bg-background/80 backdrop-blur border-cyan-500/20">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="font-semibold">
                          Ready to access Scorpius X
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          Your license has been successfully verified
                        </p>
                      </div>
                      <div className="flex space-x-3">
                        <Button
                          variant="outline"
                          className="border-purple-500/30"
                        >
                          <Download className="mr-2 h-4 w-4" />
                          Download Certificate
                        </Button>
                        <Link to="/">
                          <Button className="bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white">
                            <Shield className="mr-2 h-4 w-4" />
                            Enter Platform
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
};

export default LicenseVerification;
