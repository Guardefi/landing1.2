export type TierType = "PRO" | "ELITE" | "ENTERPRISE";

export interface TierLimits {
  smartContracts: number;
  apiCalls: number;
  scanEngines: string[];
  features: string[];
  support: string;
  mevProtection: boolean;
  exploitSimulation: boolean;
  aiForensics: boolean;
  quantumCrypto: boolean;
  whiteLabel: boolean;
  onPremise: boolean;
  customIntegrations: boolean;
  realTimeMonitoring: boolean;
  advancedAnalytics: boolean;
  unlimitedAccess: boolean;
}

export interface Tier {
  id: TierType;
  name: string;
  price: number;
  description: string;
  target: string;
  limits: TierLimits;
  features: string[];
  highlighted?: boolean;
}

export interface Usage {
  smartContracts: number;
  apiCalls: number;
  currentPeriodStart: string;
  currentPeriodEnd: string;
}

export interface Subscription {
  id: string;
  userId: string;
  tier: TierType;
  status: "active" | "inactive" | "cancelled" | "past_due";
  currentPeriodStart: string;
  currentPeriodEnd: string;
  cancelAtPeriodEnd: boolean;
  usage: Usage;
  createdAt: string;
  updatedAt: string;
}

export const TIER_DEFINITIONS: Record<TierType, Tier> = {
  PRO: {
    id: "PRO",
    name: "Pro Tier",
    price: 299,
    description: "Perfect for individual developers and small teams",
    target: "Individual developers, small teams, startups",
    limits: {
      smartContracts: 5,
      apiCalls: 1000,
      scanEngines: ["slither", "mythril"],
      features: ["basic_scanning", "pdf_reports", "community_support"],
      support: "community",
      mevProtection: false,
      exploitSimulation: false,
      aiForensics: false,
      quantumCrypto: false,
      whiteLabel: false,
      onPremise: false,
      customIntegrations: false,
      realTimeMonitoring: false,
      advancedAnalytics: false,
      unlimitedAccess: false,
    },
    features: [
      "Basic vulnerability scanning (Slither + Mythril)",
      "Standard threat detection",
      "Basic reporting (PDF exports)",
      "Community support",
      "API access (1,000 calls/month)",
      "Up to 5 smart contracts/month",
    ],
  },
  ELITE: {
    id: "ELITE",
    name: "Elite Tier",
    price: 1299,
    description: "Advanced features for growing protocols",
    target: "Growing DeFi protocols, mid-market companies",
    highlighted: true,
    limits: {
      smartContracts: 25,
      apiCalls: 10000,
      scanEngines: ["slither", "mythril", "securify", "manticore"],
      features: [
        "advanced_scanning",
        "real_time_monitoring",
        "mev_basic",
        "exploit_sim_limited",
        "priority_support",
        "advanced_analytics",
        "custom_integrations",
      ],
      support: "priority",
      mevProtection: true,
      exploitSimulation: true,
      aiForensics: false,
      quantumCrypto: false,
      whiteLabel: false,
      onPremise: false,
      customIntegrations: true,
      realTimeMonitoring: true,
      advancedAnalytics: true,
      unlimitedAccess: false,
    },
    features: [
      "Everything in Pro +",
      "Advanced scanner (all 4 engines)",
      "Real-time monitoring & alerts",
      "MEV protection (basic)",
      "Exploit simulation (limited)",
      "Priority support",
      "Advanced analytics dashboard",
      "API access (10,000 calls/month)",
      "Up to 25 smart contracts/month",
      "Custom integrations",
    ],
  },
  ENTERPRISE: {
    id: "ENTERPRISE",
    name: "Enterprise Tier",
    price: 4999,
    description: "Complete solution for large organizations",
    target: "Major protocols, institutions, large enterprises",
    limits: {
      smartContracts: -1, // unlimited
      apiCalls: -1, // unlimited
      scanEngines: ["slither", "mythril", "securify", "manticore"],
      features: ["all"],
      support: "dedicated",
      mevProtection: true,
      exploitSimulation: true,
      aiForensics: true,
      quantumCrypto: true,
      whiteLabel: true,
      onPremise: true,
      customIntegrations: true,
      realTimeMonitoring: true,
      advancedAnalytics: true,
      unlimitedAccess: true,
    },
    features: [
      "Everything in Elite +",
      "Full AI forensics & compliance suite",
      "Quantum cryptography features",
      "Advanced MEV protection with ML",
      "Unlimited exploit simulation",
      "White-label deployment",
      "Dedicated support & training",
      "Custom compliance reports",
      "On-premise deployment options",
      "Unlimited API access",
      "Unlimited smart contracts",
      "SLA guarantees",
    ],
  },
};

export const DEFAULT_USAGE: Usage = {
  smartContracts: 0,
  apiCalls: 0,
  currentPeriodStart: new Date().toISOString(),
  currentPeriodEnd: new Date(
    Date.now() + 30 * 24 * 60 * 60 * 1000,
  ).toISOString(),
};
