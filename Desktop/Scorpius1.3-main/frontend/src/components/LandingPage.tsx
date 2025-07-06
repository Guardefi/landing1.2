import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import WalletScanner from '@/components/WalletScanner';
import GalaxyHero from '@/components/GalaxyHero';
import {
  Shield,
  Search,
  Zap,
  Brain,
  Globe,
  Users,
  Star,
  CheckCircle2,
  ArrowRight,
  Play,
  ExternalLink,
  Github,
  Twitter,
} from 'lucide-react';
import { Link } from 'react-router-dom';

export function LandingPage() {
  const [showDemo, setShowDemo] = useState(false);

  const features = [
    {
      icon: Shield,
      title: 'Vulnerability Scanner',
      description: 'AI-powered smart contract analysis with real-time threat detection',
      color: 'text-blue-500',
      bgColor: 'bg-blue-500/10',
    },
    {
      icon: Search,
      title: 'Wallet Guard',
      description: 'Monitor token approvals and revoke dangerous permissions',
      color: 'text-purple-500',
      bgColor: 'bg-purple-500/10',
    },
    {
      icon: Zap,
      title: 'MEV Protection',
      description: 'Real-time MEV detection and frontrunning protection',
      color: 'text-amber-500',
      bgColor: 'bg-amber-500/10',
    },
    {
      icon: Brain,
      title: 'Honeypot Radar',
      description: 'ML-driven honeypot detection and risk assessment',
      color: 'text-green-500',
      bgColor: 'bg-green-500/10',
    },
  ];

  const stats = [
    { value: '1M+', label: 'Contracts Scanned' },
    { value: '99.9%', label: 'Accuracy Rate' },
    { value: '24/7', label: 'Monitoring' },
    { value: '500+', label: 'Enterprise Clients' },
  ];

  const testimonials = [
    {
      name: 'Alex Chen',
      role: 'Security Lead at DeFiCorp',
      content: 'Scorpius has revolutionized our security posture. The real-time threat detection saved us from multiple attacks.',
      rating: 5,
    },
    {
      name: 'Sarah Johnson',
      role: 'CTO at BlockChain Ventures',
      content: 'The most comprehensive blockchain security platform we\'ve used. Enterprise-grade features with amazing support.',
      rating: 5,
    },
    {
      name: 'Michael Rodriguez',
      role: 'Founder at CryptoGuard',
      content: 'Scorpius\' AI-powered analysis is incredibly accurate. It\'s like having a team of security experts 24/7.',
      rating: 5,
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Hero Section */}
      <GalaxyHero className="min-h-screen" />

      {/* Features Section */}
      <section className="py-20 px-6 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
              Comprehensive Security Suite
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Protect your blockchain assets with our enterprise-grade security platform
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full border-gray-800 bg-gray-900/50 backdrop-blur-sm hover:border-gray-700 transition-colors">
                  <CardHeader>
                    <div className={`w-12 h-12 rounded-lg ${feature.bgColor} flex items-center justify-center mb-4`}>
                      <feature.icon className={`h-6 w-6 ${feature.color}`} />
                    </div>
                    <CardTitle className="text-white">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-400">{feature.description}</p>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Live Demo Section */}
      <section className="py-20 px-6 bg-gray-900/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-6 text-white">
              Try Our Wallet Scanner
            </h2>
            <p className="text-xl text-gray-400 max-w-3xl mx-auto">
              Experience real-time wallet security analysis
            </p>
            
            {!showDemo && (
              <Button
                onClick={() => setShowDemo(true)}
                className="mt-8 px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
              >
                <Play className="h-5 w-5 mr-2" />
                Launch Live Demo
              </Button>
            )}
          </div>

          {showDemo && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="max-w-4xl mx-auto"
            >
              <WalletScanner 
                defaultAddress="0x742d35Cc7BF1F64DA516d20276B4B08C7b2F3f8a"
                onScanComplete={(result) => {
                  console.log('Demo scan completed:', result);
                }}
              />
            </motion.div>
          )}
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
                className="space-y-2"
              >
                <div className="text-4xl md:text-5xl font-bold text-white">
                  {stat.value}
                </div>
                <div className="text-gray-400">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 px-6 bg-gray-900/30">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold mb-6 text-white">
              Trusted by Industry Leaders
            </h2>
            <p className="text-xl text-gray-400">
              See what our clients say about Scorpius
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                viewport={{ once: true }}
              >
                <Card className="h-full border-gray-800 bg-gray-900/50 backdrop-blur-sm">
                  <CardContent className="p-6">
                    <div className="flex mb-4">
                      {[...Array(testimonial.rating)].map((_, i) => (
                        <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                      ))}
                    </div>
                    <p className="text-gray-300 mb-6">"{testimonial.content}"</p>
                    <div>
                      <div className="font-semibold text-white">{testimonial.name}</div>
                      <div className="text-gray-400 text-sm">{testimonial.role}</div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-5xl font-bold mb-6 text-white">
            Ready to Secure Your Assets?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Join thousands of users protecting their blockchain investments
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              asChild
              className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-600 hover:to-purple-700 transition-all duration-300 transform hover:scale-105"
            >
              <Link to="/scanner">
                <Shield className="h-5 w-5 mr-2" />
                Start Security Scan
              </Link>
            </Button>
            <Button
              variant="outline"
              asChild
              className="px-8 py-4 border-gray-600 text-gray-300 hover:border-gray-500 hover:text-white"
            >
              <Link to="/pricing">
                View Pricing
                <ArrowRight className="h-5 w-5 ml-2" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-800 py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="space-y-4">
              <h3 className="text-xl font-bold text-white">Scorpius</h3>
              <p className="text-gray-400">
                Enterprise-grade blockchain security platform
              </p>
              <div className="flex space-x-4">
                <Button variant="ghost" size="icon">
                  <Github className="h-5 w-5" />
                </Button>
                <Button variant="ghost" size="icon">
                  <Twitter className="h-5 w-5" />
                </Button>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold text-white">Product</h4>
              <div className="space-y-2">
                <Link to="/scanner" className="block text-gray-400 hover:text-white transition-colors">
                  Scanner
                </Link>
                <Link to="/security/elite" className="block text-gray-400 hover:text-white transition-colors">
                  Security Elite
                </Link>
                <Link to="/trading/ai" className="block text-gray-400 hover:text-white transition-colors">
                  MEV Protection
                </Link>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold text-white">Resources</h4>
              <div className="space-y-2">
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">
                  Documentation
                </a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">
                  API Reference
                </a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">
                  Support
                </a>
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold text-white">Company</h4>
              <div className="space-y-2">
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">
                  About Us
                </a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">
                  Contact
                </a>
                <a href="#" className="block text-gray-400 hover:text-white transition-colors">
                  Privacy Policy
                </a>
              </div>
            </div>
          </div>
          
          <Separator className="my-8 border-gray-800" />
          
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400">
              © 2025 Scorpius Security. All rights reserved.
            </p>
            <div className="flex items-center space-x-4 mt-4 md:mt-0">
              <Badge variant="outline" className="border-green-600 text-green-400">
                <CheckCircle2 className="h-3 w-3 mr-1" />
                99.9% Uptime
              </Badge>
              <Badge variant="outline" className="border-blue-600 text-blue-400">
                <Shield className="h-3 w-3 mr-1" />
                SOC 2 Compliant
              </Badge>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default LandingPage;
