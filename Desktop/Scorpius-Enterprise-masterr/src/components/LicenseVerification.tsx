import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Shield,
  CheckCircle,
  AlertTriangle,
  Key,
  Lock,
  Unlock,
  Globe,
  Cpu,
  Database,
  Zap,
  Eye,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface LicenseVerificationProps {
  onLicenseVerified: (licenseKey: string) => Promise<boolean>;
}

export const LicenseVerification = ({
  onLicenseVerified,
}: LicenseVerificationProps) => {
  const [licenseKey, setLicenseKey] = useState("");
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationStep, setVerificationStep] = useState(0);
  const [error, setError] = useState("");
  const [showFeatures, setShowFeatures] = useState(false);

  const verificationSteps = [
    "Initializing Neural Interface",
    "Validating License Signature",
    "Checking Quantum Encryption",
    "Authenticating with Scorpius Network",
    "Loading Security Protocols",
    "Establishing Secure Connection",
    "License Verified Successfully",
  ];

  const features = [
    {
      name: "Smart Contract Scanner",
      status: "Active",
      icon: Shield,
      color: "#00ffff",
    },
    { name: "MEV Operations", status: "Active", icon: Zap, color: "#0ea5e9" },
    { name: "Neural Analytics", status: "Active", icon: Cpu, color: "#06b6d4" },
    { name: "Threat Detection", status: "Active", icon: Eye, color: "#3b82f6" },
    {
      name: "Quantum Encryption",
      status: "Active",
      icon: Lock,
      color: "#6366f1",
    },
    { name: "Global Network", status: "Active", icon: Globe, color: "#8b5cf6" },
  ];

  const handleLicenseSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsVerifying(true);
    setError("");
    setVerificationStep(0);

    // Validate license key before processing
    if (!licenseKey || licenseKey.trim() === "") {
      setError("Please enter a license key.");
      setIsVerifying(false);
      return;
    }

    try {
      // Simulate verification steps
      for (let i = 0; i < verificationSteps.length; i++) {
        setVerificationStep(i);
        await new Promise((resolve) => setTimeout(resolve, 500));
      }

      // Call the actual license verification function
      const isValid = await onLicenseVerified(licenseKey);

      if (!isValid) {
        setError("Invalid license key. Please contact support for assistance.");
        setIsVerifying(false);
        return;
      }

      // Show features for 2 seconds then proceed
      setShowFeatures(true);
      await new Promise((resolve) => setTimeout(resolve, 3000));
    } catch (error) {
      console.error("License verification error:", error);
      setError("License verification failed. Please try again.");
      setIsVerifying(false);
    }
  };

  const skipLicense = async () => {
    try {
      // For demo purposes, use demo license key
      const demoLicenseKey = "SCORPIUS-DEMO-2024";
      const isValid = await onLicenseVerified(demoLicenseKey);

      if (isValid) {
        setShowFeatures(true);
        await new Promise((resolve) => setTimeout(resolve, 2000));
      } else {
        setError("Demo access failed. Please try again.");
      }
    } catch (error) {
      console.error("Demo license error:", error);
      setError("Demo access failed. Please try again.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <AnimatePresence mode="wait">
        {!showFeatures ? (
          <motion.div
            key="license-form"
            initial={{ opacity: 0, scale: 0.9, y: 50 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.9, y: -50 }}
            className="relative z-10 w-full max-w-lg p-8 bg-background/80 backdrop-blur border border-border rounded-2xl shadow-lg"
          >
            {/* Header */}
            <div className="text-center mb-8">
              {/* Scorpius Logo */}
              <motion.div
                className="w-24 h-24 mx-auto mb-6 relative"
                animate={{
                  rotateY: [0, 360],
                }}
                transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
              >
                <div className="w-full h-full rounded-2xl flex items-center justify-center relative bg-black border-2 border-blue-400 shadow-[0_0_40px_rgba(59,130,246,0.6)]">
                  <Shield
                    className="w-16 h-16 text-cyan-400"
                    style={{
                      filter:
                        "drop-shadow(0 0 20px #00ffff) drop-shadow(0 0 30px #00cccc)",
                    }}
                  />

                  {/* Multiple glow rings */}
                  {[0, 1, 2].map((ring) => (
                    <motion.div
                      key={ring}
                      className="absolute inset-0 rounded-2xl border-2"
                      style={{
                        borderColor: ["#3b82f6", "#0ea5e9", "#00ffff"][ring],
                      }}
                      animate={{
                        opacity: [0, 0.8, 0],
                        scale: [1, 1.2 + ring * 0.1, 1],
                      }}
                      transition={{
                        duration: 3,
                        repeat: Infinity,
                        delay: ring * 0.5,
                      }}
                    />
                  ))}
                </div>
              </motion.div>

              <motion.h1
                className="text-4xl font-bold mb-2 bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent"
                animate={{
                  backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
                }}
                transition={{ duration: 4, repeat: Infinity }}
              >
                SCORPIUS X
              </motion.h1>

              <motion.div
                className="text-lg text-cyan-400 font-mono mb-4"
                animate={{ opacity: [0.7, 1, 0.7] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                LICENSE VERIFICATION REQUIRED
              </motion.div>

              <div className="text-sm text-muted-foreground font-mono">
                Elite Security Operations Platform
              </div>
            </div>

            {/* License verification status */}
            {isVerifying && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 p-4 rounded-xl border border-cyan-400/40 bg-cyan-400/10"
              >
                <div className="flex items-center gap-3 mb-3">
                  <motion.div
                    className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full"
                    animate={{ rotate: 360 }}
                    transition={{
                      duration: 1,
                      repeat: Infinity,
                      ease: "linear",
                    }}
                  />
                  <span className="text-cyan-400 font-mono text-sm">
                    {verificationSteps[verificationStep]}
                  </span>
                </div>

                {/* Progress bar */}
                <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-cyan-400 to-blue-400"
                    initial={{ width: "0%" }}
                    animate={{
                      width: `${
                        ((verificationStep + 1) / verificationSteps.length) *
                        100
                      }%`,
                    }}
                    transition={{ duration: 0.5, ease: "easeOut" }}
                    style={{
                      boxShadow: "0 0 15px rgba(0, 255, 255, 0.8)",
                    }}
                  />
                </div>
              </motion.div>
            )}

            {/* Error alert */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.9, y: -10 }}
                  animate={{ opacity: 1, scale: 1, y: 0 }}
                  exit={{ opacity: 0, scale: 0.9, y: -10 }}
                  className="mb-6 p-4 rounded-2xl border-2 border-red-500/40 bg-red-500/10 flex items-center gap-3"
                  style={{ boxShadow: "0 0 20px rgba(255, 68, 68, 0.2)" }}
                >
                  <AlertTriangle className="w-5 h-5 text-red-500" />
                  <span className="text-red-400 text-sm font-mono">
                    {error}
                  </span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* License form */}
            <form onSubmit={handleLicenseSubmit} className="space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-foreground font-mono flex items-center gap-2">
                  <Key className="w-4 h-4 text-blue-400" />
                  LICENSE KEY
                </label>
                <div className="relative">
                  <Input
                    type="text"
                    value={licenseKey}
                    onChange={(e) =>
                      setLicenseKey(e.target.value.toUpperCase())
                    }
                    placeholder="ENTER ELITE LICENSE KEY..."
                    required
                    disabled={isVerifying}
                    className="w-full bg-background/60 border-2 border-blue-400/40 rounded-2xl px-4 py-3 text-foreground placeholder-muted-foreground font-mono text-sm focus:border-blue-400 transition-all duration-300 uppercase tracking-wider"
                    style={{
                      boxShadow: "inset 0 0 20px rgba(59, 130, 246, 0.1)",
                    }}
                  />
                  <motion.div
                    className="absolute right-4 top-1/2 transform -translate-y-1/2 w-2 h-2 bg-blue-400 rounded-full"
                    animate={{ opacity: [1, 0.3, 1] }}
                    transition={{ duration: 2, repeat: Infinity }}
                    style={{ boxShadow: "0 0 10px rgba(59, 130, 246, 0.8)" }}
                  />
                </div>
                <div className="text-xs text-muted-foreground font-mono">
                  Format: SCORPIUS-ELITE-YYYY
                </div>
              </div>

              <Button
                type="submit"
                disabled={isVerifying || !licenseKey}
                className="w-full py-3 rounded-2xl font-mono font-bold transition-all duration-300 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white border-2 border-blue-400/60"
                style={{
                  boxShadow:
                    isVerifying || !licenseKey
                      ? "0 0 20px rgba(102, 102, 102, 0.4)"
                      : "0 0 30px rgba(59, 130, 246, 0.5)",
                }}
                whileHover={
                  !isVerifying && licenseKey ? { scale: 1.02, y: -2 } : {}
                }
                whileTap={!isVerifying && licenseKey ? { scale: 0.98 } : {}}
              >
                {isVerifying ? (
                  <div className="flex items-center justify-center gap-3">
                    <motion.div
                      className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full"
                      animate={{ rotate: 360 }}
                      transition={{
                        duration: 1,
                        repeat: Infinity,
                        ease: "linear",
                      }}
                    />
                    <span>VERIFYING LICENSE...</span>
                  </div>
                ) : (
                  <div className="flex items-center justify-center gap-3">
                    <Shield className="w-4 h-4" />
                    <span>VERIFY LICENSE</span>
                  </div>
                )}
              </Button>
            </form>

            {/* Demo access */}
            <div className="mt-8 text-center">
              <div className="text-xs text-muted-foreground font-mono mb-3">
                Don't have a license key?
              </div>
              <Button
                onClick={skipLicense}
                disabled={isVerifying}
                variant="outline"
                className="border-2 border-cyan-400/40 bg-transparent text-cyan-400 hover:bg-cyan-400/10 font-mono text-sm"
                style={{
                  boxShadow: "0 0 15px rgba(0, 255, 255, 0.2)",
                }}
              >
                <Eye className="w-4 h-4 mr-2" />
                DEMO ACCESS
              </Button>

              {/* Demo license hint */}
              <div className="mt-4 text-xs text-cyan-400 bg-cyan-400/20 rounded-lg p-2 border border-cyan-400/40">
                <div className="font-mono">TRIAL LICENSE:</div>
                <div className="font-mono text-blue-400">
                  SCORPIUS-ELITE-2024
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="features"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.1 }}
            className="relative z-10 w-full max-w-2xl p-8 bg-background/80 backdrop-blur border border-border rounded-2xl shadow-lg"
          >
            <div className="text-center mb-8">
              <motion.div
                className="w-16 h-16 mx-auto mb-4 rounded-2xl flex items-center justify-center bg-gradient-to-r from-cyan-500 to-blue-500"
                style={{
                  boxShadow: "0 0 40px rgba(0, 255, 255, 0.6)",
                }}
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <CheckCircle className="w-8 h-8 text-white" />
              </motion.div>

              <h2 className="text-3xl font-bold text-cyan-400 font-mono mb-2">
                LICENSE VERIFIED
              </h2>
              <p className="text-muted-foreground font-mono">
                Initializing Scorpius Elite Features...
              </p>
            </div>

            {/* Features grid */}
            <div className="grid grid-cols-2 gap-4 mb-6">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.name}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 rounded-xl border border-cyan-400/40 bg-cyan-400/10"
                >
                  <div className="flex items-center gap-3">
                    <motion.div
                      className="w-8 h-8 rounded-lg flex items-center justify-center border-2"
                      style={{
                        backgroundColor: `${feature.color}20`,
                        borderColor: `${feature.color}60`,
                      }}
                      animate={{ rotate: [0, 360] }}
                      transition={{
                        duration: 4,
                        repeat: Infinity,
                        delay: index * 0.2,
                      }}
                    >
                      <feature.icon
                        className="w-4 h-4"
                        style={{ color: feature.color }}
                      />
                    </motion.div>
                    <div>
                      <div className="text-foreground font-mono text-sm">
                        {feature.name}
                      </div>
                      <div className="text-cyan-400 font-mono text-xs">
                        {feature.status}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Loading progress */}
            <div className="mb-6">
              <div className="flex justify-between text-sm font-mono mb-2">
                <span className="text-muted-foreground">
                  System Initialization
                </span>
                <span className="text-cyan-400">100%</span>
              </div>
              <div className="w-full h-2 bg-slate-800 rounded-full overflow-hidden">
                <motion.div
                  className="h-full bg-gradient-to-r from-cyan-400 to-blue-400"
                  initial={{ width: "0%" }}
                  animate={{ width: "100%" }}
                  transition={{ duration: 2, ease: "easeOut" }}
                  style={{
                    boxShadow: "0 0 15px rgba(0, 255, 255, 0.8)",
                  }}
                />
              </div>
            </div>

            <motion.div
              className="text-center text-cyan-400 font-mono text-lg"
              animate={{ opacity: [0.7, 1, 0.7] }}
              transition={{ duration: 1, repeat: Infinity }}
            >
              Welcome to Scorpius X Elite
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
