import { Shield, Github, Mail, Heart, ExternalLink } from "lucide-react";
import { Link } from "react-router-dom";

const ScorpiusFooter = () => {
  const quickLinks = [
    { name: "Security", href: "/security/elite" },
    { name: "Trading", href: "/trading/ai" },
    { name: "Analytics", href: "/analytics/enterprise" },
    { name: "Bridge", href: "/bridge/network" },
    { name: "Computing", href: "/computing/cluster" },
    { name: "Monitoring", href: "/monitoring/health" },
  ];

  const supportLinks = [
    { name: "Documentation", href: "#", external: true },
    { name: "Support", href: "mailto:support@scorpius.dev", external: true },
    { name: "GitHub", href: "#", external: true },
    { name: "Status", href: "#", external: true },
  ];

  const legalLinks = [
    { name: "Privacy Policy", href: "#" },
    { name: "Terms of Service", href: "#" },
    { name: "Security", href: "#" },
  ];

  return (
    <footer className="bg-slate-900/50 border-t border-slate-700/50 mt-auto">
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand Section */}
          <div className="space-y-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600">
                <Shield className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="font-bold text-white">Scorpius X</h3>
                <p className="text-xs text-slate-400">Security Platform</p>
              </div>
            </div>
            <p className="text-sm text-slate-400 max-w-xs">
              Enterprise-grade security and trading platform for the modern DeFi
              ecosystem.
            </p>
            <div className="flex space-x-3">
              <a
                href="#"
                className="text-slate-400 hover:text-white transition-colors"
                aria-label="GitHub"
              >
                <Github className="h-5 w-5" />
              </a>
              <a
                href="mailto:support@scorpius.dev"
                className="text-slate-400 hover:text-white transition-colors"
                aria-label="Email Support"
              >
                <Mail className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold text-white mb-4">Platform</h4>
            <ul className="space-y-2">
              {quickLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-slate-400 hover:text-white text-sm transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Support Links */}
          <div>
            <h4 className="font-semibold text-white mb-4">Support</h4>
            <ul className="space-y-2">
              {supportLinks.map((link) => (
                <li key={link.name}>
                  {link.external ? (
                    <a
                      href={link.href}
                      target={
                        link.href.startsWith("http") ? "_blank" : undefined
                      }
                      rel={
                        link.href.startsWith("http")
                          ? "noopener noreferrer"
                          : undefined
                      }
                      className="text-slate-400 hover:text-white text-sm transition-colors flex items-center space-x-1"
                    >
                      <span>{link.name}</span>
                      {link.href.startsWith("http") && (
                        <ExternalLink className="h-3 w-3" />
                      )}
                    </a>
                  ) : (
                    <Link
                      to={link.href}
                      className="text-slate-400 hover:text-white text-sm transition-colors"
                    >
                      {link.name}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>

          {/* Legal Links */}
          <div>
            <h4 className="font-semibold text-white mb-4">Legal</h4>
            <ul className="space-y-2">
              {legalLinks.map((link) => (
                <li key={link.name}>
                  <Link
                    to={link.href}
                    className="text-slate-400 hover:text-white text-sm transition-colors"
                  >
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-slate-700/50 mt-8 pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 text-slate-400 text-sm">
              <span>Built with</span>
              <Heart className="h-4 w-4 text-red-500" />
              <span>by the Scorpius Security Team</span>
            </div>
            <div className="text-slate-500 text-sm mt-4 md:mt-0">
              © 2024 Scorpius Security. All rights reserved.
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default ScorpiusFooter;
