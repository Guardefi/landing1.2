import { useState } from "react";
import { motion } from "framer-motion";
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
  UserPlus,
} from "lucide-react";
import { ParticleField, FloatingOrbs } from "@/components/ui/particle-effects";
import { InteractiveGrid } from "@/components/ui/InteractiveGrid";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "sonner";

const Register = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    acceptTerms: false,
    marketingOptIn: false,
  });

  const navigate = useNavigate();
  const { register, isLoading, error } = useAuth();

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const validateForm = () => {
    if (!formData.name.trim()) {
      toast.error("Please enter your full name");
      return false;
    }

    if (!formData.email.trim()) {
      toast.error("Please enter your email address");
      return false;
    }

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      toast.error("Please enter a valid email address");
      return false;
    }

    if (formData.password.length < 8) {
      toast.error("Password must be at least 8 characters long");
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error("Passwords do not match");
      return false;
    }

    if (!formData.acceptTerms) {
      toast.error("Please accept the Terms of Service and Privacy Policy");
      return false;
    }

    return true;
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const result = await register({
      name: formData.name,
      email: formData.email,
      password: formData.password,
      confirmPassword: formData.confirmPassword,
      acceptTerms: formData.acceptTerms,
      marketingOptIn: formData.marketingOptIn,
    });

    if (result.success) {
      toast.success("Registration successful! Welcome to Scorpius X");
      navigate("/");
    } else {
      toast.error(result.error || "Registration failed. Please try again.");
    }
  };

  const passwordStrength = (password: string) => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/[A-Z]/.test(password)) strength++;
    if (/[a-z]/.test(password)) strength++;
    if (/[0-9]/.test(password)) strength++;
    if (/[^A-Za-z0-9]/.test(password)) strength++;
    return strength;
  };

  const getPasswordStrengthColor = (strength: number) => {
    switch (strength) {
      case 0:
      case 1:
        return "bg-red-500";
      case 2:
        return "bg-orange-500";
      case 3:
        return "bg-yellow-500";
      case 4:
        return "bg-green-500";
      case 5:
        return "bg-emerald-500";
      default:
        return "bg-gray-500";
    }
  };

  const getPasswordStrengthText = (strength: number) => {
    switch (strength) {
      case 0:
      case 1:
        return "Weak";
      case 2:
        return "Fair";
      case 3:
        return "Good";
      case 4:
        return "Strong";
      case 5:
        return "Very Strong";
      default:
        return "";
    }
  };

  const strength = passwordStrength(formData.password);

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
        <div className="w-full max-w-4xl grid lg:grid-cols-2 gap-8 items-center">
          {/* Left Side - Branding */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
            className="space-y-8"
          >
            {/* Hero Section */}
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.1 }}
              className="relative rounded-2xl overflow-hidden shadow-2xl border border-cyan-400/20 h-64 lg:h-80"
            >
              {/* Animated Background */}
              <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-cyan-900/20 to-blue-900/30" />
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(0,255,255,0.1),transparent)] animate-pulse" />

              {/* Cyber Grid Pattern */}
              <div className="absolute inset-0 opacity-20">
                <div
                  className="h-full w-full bg-[linear-gradient(rgba(0,255,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(0,255,255,0.1)_1px,transparent_1px)]"
                  style={{ backgroundSize: "20px 20px" }}
                />
              </div>

              {/* Floating Elements */}
              <div className="absolute top-4 right-4 w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
              <div className="absolute top-8 left-8 w-1 h-1 bg-blue-400 rounded-full animate-ping" />
              <div className="absolute bottom-12 right-12 w-3 h-3 border border-cyan-400/50 rounded-full animate-pulse" />

              {/* Content */}
              <div className="absolute bottom-4 left-4 right-4">
                <h1 className="text-2xl lg:text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent">
                  Join Scorpius X
                </h1>
                <p className="text-sm text-white/80">
                  Enterprise Security Platform
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
                Create Your Account
              </h2>
              <p className="text-muted-foreground text-lg leading-relaxed">
                Get started with advanced blockchain security, AI-powered
                trading, and comprehensive threat detection.
              </p>
            </motion.div>

            {/* Features */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.6 }}
              className="space-y-3"
            >
              {[
                { icon: Shield, text: "Enterprise-grade Security" },
                { icon: User, text: "Personal Dashboard & Analytics" },
                { icon: CheckCircle2, text: "24/7 Support & Monitoring" },
              ].map((feature, index) => (
                <motion.div
                  key={feature.text}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.4, delay: 0.8 + index * 0.1 }}
                  className="flex items-center space-x-3 text-muted-foreground"
                >
                  <feature.icon className="h-5 w-5 text-cyan-400" />
                  <span>{feature.text}</span>
                </motion.div>
              ))}
            </motion.div>
          </motion.div>

          {/* Right Side - Registration Form */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <Card className="bg-background/80 backdrop-blur border-cyan-500/20 shadow-2xl">
              <CardHeader className="space-y-4">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-2xl font-bold">
                    Create Account
                  </CardTitle>
                  <Badge
                    variant="outline"
                    className="border-cyan-500/30 text-cyan-400"
                  >
                    <Lock className="h-3 w-3 mr-1" />
                    Secure
                  </Badge>
                </div>
              </CardHeader>

              <CardContent className="space-y-6">
                <motion.form
                  onSubmit={handleRegister}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4"
                >
                  {/* Name Field */}
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-sm font-medium">
                      Full Name
                    </Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="name"
                        type="text"
                        placeholder="Enter your full name"
                        value={formData.name}
                        onChange={(e) =>
                          handleInputChange("name", e.target.value)
                        }
                        className="pl-10 border-cyan-500/20 focus:border-cyan-500 bg-background/50"
                        required
                      />
                    </div>
                  </div>

                  {/* Email Field */}
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
                        value={formData.email}
                        onChange={(e) =>
                          handleInputChange("email", e.target.value)
                        }
                        className="pl-10 border-cyan-500/20 focus:border-cyan-500 bg-background/50"
                        required
                      />
                    </div>
                  </div>

                  {/* Password Field */}
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-sm font-medium">
                      Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Create a strong password"
                        value={formData.password}
                        onChange={(e) =>
                          handleInputChange("password", e.target.value)
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

                    {/* Password Strength Indicator */}
                    {formData.password && (
                      <div className="space-y-1">
                        <div className="flex space-x-1">
                          {[1, 2, 3, 4, 5].map((level) => (
                            <div
                              key={level}
                              className={`h-1 flex-1 rounded-full ${
                                level <= strength
                                  ? getPasswordStrengthColor(strength)
                                  : "bg-gray-600"
                              }`}
                            />
                          ))}
                        </div>
                        <p
                          className={`text-xs ${
                            strength >= 3
                              ? "text-green-400"
                              : strength >= 2
                                ? "text-yellow-400"
                                : "text-red-400"
                          }`}
                        >
                          {getPasswordStrengthText(strength)}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Confirm Password Field */}
                  <div className="space-y-2">
                    <Label
                      htmlFor="confirmPassword"
                      className="text-sm font-medium"
                    >
                      Confirm Password
                    </Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="confirmPassword"
                        type={showConfirmPassword ? "text" : "password"}
                        placeholder="Confirm your password"
                        value={formData.confirmPassword}
                        onChange={(e) =>
                          handleInputChange("confirmPassword", e.target.value)
                        }
                        className="pl-10 pr-10 border-cyan-500/20 focus:border-cyan-500 bg-background/50"
                        required
                      />
                      <button
                        type="button"
                        onClick={() =>
                          setShowConfirmPassword(!showConfirmPassword)
                        }
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-foreground"
                      >
                        {showConfirmPassword ? (
                          <EyeOff className="h-4 w-4" />
                        ) : (
                          <Eye className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Terms and Conditions */}
                  <div className="space-y-3">
                    <div className="flex items-start space-x-2">
                      <Checkbox
                        id="terms"
                        checked={formData.acceptTerms}
                        onCheckedChange={(checked) =>
                          handleInputChange("acceptTerms", !!checked)
                        }
                      />
                      <Label
                        htmlFor="terms"
                        className="text-sm leading-relaxed"
                      >
                        I agree to the{" "}
                        <Link
                          to="/terms"
                          className="text-cyan-400 hover:text-cyan-300 underline"
                        >
                          Terms of Service
                        </Link>{" "}
                        and{" "}
                        <Link
                          to="/privacy"
                          className="text-cyan-400 hover:text-cyan-300 underline"
                        >
                          Privacy Policy
                        </Link>
                      </Label>
                    </div>

                    <div className="flex items-start space-x-2">
                      <Checkbox
                        id="marketing"
                        checked={formData.marketingOptIn}
                        onCheckedChange={(checked) =>
                          handleInputChange("marketingOptIn", !!checked)
                        }
                      />
                      <Label
                        htmlFor="marketing"
                        className="text-sm text-muted-foreground"
                      >
                        Send me updates about new features and security insights
                        (optional)
                      </Label>
                    </div>
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
                        Creating Account...
                      </>
                    ) : (
                      <>
                        <UserPlus className="mr-2 h-4 w-4" />
                        Create Account
                      </>
                    )}
                  </Button>
                </motion.form>

                {/* Login Link */}
                <div className="pt-4 border-t border-cyan-500/20">
                  <div className="text-center text-sm">
                    <span className="text-muted-foreground">
                      Already have an account?{" "}
                    </span>
                    <Link
                      to="/login"
                      className="text-cyan-400 hover:text-cyan-300 transition-colors font-medium"
                    >
                      Sign in here
                    </Link>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Register;
