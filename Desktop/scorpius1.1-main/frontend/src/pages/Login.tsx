import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import {
  Shield,
  Eye,
  EyeOff,
  Lock,
  User,
  Mail,
  AlertTriangle,
  CheckCircle2,
  Loader2,
  Scan,
  Zap,
  Globe,
  Database,
  Brain,
} from "lucide-react";
import { ParticleField, FloatingOrbs } from "@/components/ui/particle-effects";
import { InteractiveGrid } from "@/components/ui/InteractiveGrid";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

const Login = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [showPassword, setShowPassword] = useState(false);
  const [loginMethod, setLoginMethod] = useState<"credentials" | "license">(
    "credentials",
  );
  const [credentials, setCredentials] = useState({
    email: "",
    password: "",
    rememberMe: false,
  });

  const navigate = useNavigate();
  const { login, isLoading, error } = useAuth();

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!credentials.email || !credentials.password) {
      toast.error("Please enter both email and password");
      return;
    }

    const result = await login({
      email: credentials.email,
      password: credentials.password,
      rememberMe: credentials.rememberMe,
    });

    if (result.success) {
      toast.success("Login successful! Welcome to Scorpius X");
      navigate("/");
    } else {
      toast.error(result.error || "Login failed. Please try again.");
    }
  };

  const systemStats = [
    {
      label: "Security Level",
      value: "Elite",
      icon: Shield,
      color: "text-green-400",
    },
    {
      label: "Uptime",
      value: "99.97%",
      icon: Zap,
      color: "text-blue-400",
    },
  ];

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-slate-800 to-cyan-900/20" />
      <ParticleField
        particleCount={60}
        colors={["#00ffff", "#35d7f0", "#22c55e", "#8b5cf6"]}
        className="opacity-40"
      />
      <FloatingOrbs orbCount={4} className="opacity-30" />

      {/* Interactive Grid Pattern */}
      <InteractiveGrid className="opacity-20" />

      <div className="relative z-10 flex items-center justify-center min-h-screen p-4">
        <div className="w-full max-w-6xl grid lg:grid-cols-2 gap-8 items-center">
          {/* Left Side - Video & Branding */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            {/* Video Section */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="relative rounded-2xl overflow-hidden shadow-2xl border border-cyan-400/20"
            >
              <video
                autoPlay
                loop
                muted
                playsInline
                className="w-full h-64 lg:h-80 object-cover"
              >
                <source src="/videos/scorpiuslive.mp4" type="video/mp4" />
                Your browser does not support the video tag.
              </video>
              <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent pointer-events-none" />

              {/* Video Overlay Text */}
              <div className="absolute bottom-4 left-4 right-4">
                <h1 className="text-2xl lg:text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  Scorpius X
                </h1>
                <p className="text-sm text-white/80">
                  Scorpius Security Platform
                </p>
              </div>
            </motion.div>

            {/* Welcome Text */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              className="text-center lg:text-left space-y-4"
            >
              <h2 className="text-2xl font-semibold text-foreground">
                Welcome to the Future of Security
              </h2>
              <p className="text-muted-foreground text-lg leading-relaxed">
                Advanced threat detection, real-time monitoring, and AI-powered
                protection for the modern digital landscape.
              </p>
            </motion.div>

            {/* System Stats */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="grid grid-cols-2 gap-4"
            >
              {systemStats.map((stat, index) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ duration: 0.4, delay: 0.8 + index * 0.1 }}
                  className="bg-background/50 backdrop-blur border border-cyan-500/20 rounded-xl p-4 hover:border-cyan-500/40 transition-all duration-300"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`p-2 rounded-lg bg-background/50 ${stat.color}`}
                    >
                      <stat.icon className="h-4 w-4" />
                    </div>
                    <div>
                      <div className="font-bold text-foreground">
                        {stat.value}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {stat.label}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Features */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.0 }}
              className="space-y-3"
            >
              {[
                { icon: Brain, text: "AI-Powered Threat Detection" },
                { icon: Database, text: "Real-time Data Analysis" },
                { icon: Shield, text: "Enterprise Security Protection" },
              ].map((feature, index) => (
                <motion.div
                  key={feature.text}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 1.2 + index * 0.1 }}
                  className="flex items-center space-x-3 text-muted-foreground"
                >
                  <feature.icon className="h-5 w-5 text-cyan-400" />
                  <span>{feature.text}</span>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>

          {/* Right Side - Login Form */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <Card className="bg-background/80 backdrop-blur border-cyan-500/20 shadow-2xl">
              <CardHeader className="space-y-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-2xl font-bold">
                    Secure Access
                  </CardTitle>
                  <Badge
                    variant="outline"
                    className="border-cyan-500/30 text-cyan-400"
                  >
                    <Lock className="h-3 w-3 mr-1" />
                    Encrypted
                  </Badge>
                </div>

                {/* Auth Method Selector */}
                <div className="flex space-x-2 p-1 bg-background/50 rounded-lg">
                  {[
                    { id: "credentials", label: "Password", icon: Lock },
                    { id: "license", label: "License", icon: Scan },
                  ].map((method) => (
                    <button
                      key={method.id}
                      onClick={() => setLoginMethod(method.id as any)}
                      className={`flex-1 flex items-center justify-center space-x-2 py-2 px-3 rounded-md text-sm font-medium transition-all duration-200 ${
                        loginMethod === method.id
                          ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                          : "text-muted-foreground hover:text-foreground hover:bg-background/50"
                      }`}
                    >
                      <method.icon className="h-4 w-4" />
                      <span>{method.label}</span>
                    </button>
                  ))}
                </div>
              </CardHeader>

              <CardContent className="space-y-6">
                <AnimatePresence mode="wait">
                  {loginMethod === "credentials" && (
                    <motion.form
                      onSubmit={handleLogin}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-4"
                    >
                      <div className="space-y-2">
                        <Label htmlFor="email" className="text-sm font-medium">
                          Email Address
                        </Label>
                        <div className="relative">
                          <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                          <Input
                            id="email"
                            type="email"
                            placeholder="Enter your email"
                            value={credentials.email}
                            onChange={(e) =>
                              setCredentials((prev) => ({
                                ...prev,
                                email: e.target.value,
                              }))
                            }
                            className="pl-10 border-cyan-500/20 focus:border-cyan-500 bg-background/50"
                            required
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <Label
                          htmlFor="password"
                          className="text-sm font-medium"
                        >
                          Password
                        </Label>
                        <div className="relative">
                          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                          <Input
                            id="password"
                            type={showPassword ? "text" : "password"}
                            placeholder="Enter your password"
                            value={credentials.password}
                            onChange={(e) =>
                              setCredentials((prev) => ({
                                ...prev,
                                password: e.target.value,
                              }))
                            }
                            className="pl-10 pr-10 border-cyan-500/20 focus:border-cyan-500 bg-background/50"
                            required
                          />
                          <button
                            type="button"
                            onClick={() => setShowPassword(!showPassword)}
                            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                          >
                            {showPassword ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </button>
                        </div>
                      </div>

                      <div className="flex items-center space-x-2">
                        <Checkbox
                          id="remember"
                          checked={credentials.rememberMe}
                          onCheckedChange={(checked) =>
                            setCredentials((prev) => ({
                              ...prev,
                              rememberMe: !!checked,
                            }))
                          }
                        />
                        <Label htmlFor="remember" className="text-sm">
                          Remember me for 30 days
                        </Label>
                      </div>

                      {error && (
                        <Alert className="border-red-500/20 bg-red-500/10">
                          <AlertTriangle className="h-4 w-4 text-red-500" />
                          <AlertDescription className="text-red-400">
                            {error}
                          </AlertDescription>
                        </Alert>
                      )}

                      <Button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-gradient-to-r from-cyan-500 to-blue-500 hover:from-cyan-600 hover:to-blue-600 text-white font-medium py-2.5"
                      >
                        {isLoading ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Signing In...
                          </>
                        ) : (
                          <>
                            <Lock className="mr-2 h-4 w-4" />
                            Sign In Securely
                          </>
                        )}
                      </Button>

                      {import.meta.env.VITE_DEMO_MODE === "true" && (
                        <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-lg p-3">
                          <div className="text-xs text-cyan-300 font-medium mb-1">
                            🎯 Demo Instructions
                          </div>
                          <div className="text-xs text-cyan-200 space-y-1">
                            <div>
                              • Email: <code>demo@scorpius.io</code>
                            </div>
                            <div>
                              • Password: <code>demo123</code>
                            </div>
                            <div className="text-cyan-400 mt-1">
                              (Any email/password combination works for demo)
                            </div>
                          </div>
                        </div>
                      )}
                    </motion.form>
                  )}

                  {loginMethod === "license" && (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -20 }}
                      transition={{ duration: 0.3 }}
                      className="space-y-4 text-center"
                    >
                      <Link
                        to="/license-verification"
                        className="block w-full p-6 border border-cyan-500/20 rounded-lg hover:border-cyan-500/40 transition-all duration-300"
                      >
                        <Scan className="mx-auto h-8 w-8 text-cyan-400 mb-4" />
                        <h3 className="font-semibold text-foreground mb-2">
                          License Verification
                        </h3>
                        <p className="text-sm text-muted-foreground">
                          Click to proceed to license verification page
                        </p>
                      </Link>
                    </motion.div>
                  )}
                </AnimatePresence>

                {/* Additional Options */}
                <div className="pt-4 border-t border-cyan-500/20">
                  <div className="flex items-center justify-between text-sm">
                    <Link
                      to="/forgot-password"
                      className="text-cyan-400 hover:text-cyan-300 transition-colors"
                    >
                      Forgot password?
                    </Link>
                    <Link
                      to="/register"
                      className="text-cyan-400 hover:text-cyan-300 transition-colors"
                    >
                      Create account
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Security Notice */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 1.2 }}
              className="mt-6 text-center"
            >
              <div className="flex items-center justify-center space-x-2 text-xs text-muted-foreground">
                <CheckCircle2 className="h-3 w-3 text-green-400" />
                <span>256-bit SSL encryption • SOC 2 Type II compliant</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>

      {/* Time Display */}
      <div className="absolute top-4 right-4 text-xs text-muted-foreground bg-background/50 backdrop-blur rounded-lg px-3 py-2 border border-cyan-500/20">
        {currentTime.toLocaleTimeString()} UTC
      </div>
    </div>
  );
};

export default Login;
