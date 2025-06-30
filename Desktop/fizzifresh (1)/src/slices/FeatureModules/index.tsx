"use client";

import { Content } from "@prismicio/client";
import { SliceComponentProps } from "@prismicio/react";
import { Bounded } from "@/components/Bounded";

/**
 * Props for `FeatureModules`.
 */
export type FeatureModulesProps =
  SliceComponentProps<Content.FeatureModulesSlice>;

const modules = [
  {
    icon: "🐝",
    title: "Hive Alert",
    description: "They won't know they've been flagged — until it's too late.",
    details:
      "Real-time bait contracts, ML threat detection, and gas-pattern sniping.",
  },
  {
    icon: "🧬",
    title: "Bytecode Similarity Engine",
    description: "Copy-paste contracts don't stand a chance.",
    details: "Detect clones. Map exploit trails. Out-evolve them.",
  },
  {
    icon: "🤖",
    title: "AI Trading Bot",
    description: "Front-runs the frontrunners.",
    details:
      "Simulates flash loans, identifies anomalies, and predicts MEV traps before they deploy.",
  },
  {
    icon: "🌉",
    title: "Cross-Chain Bridge Network",
    description: "No more bridge hacks on your watch.",
    details:
      "Scans Ethereum, BSC, Arbitrum, and Polygon for liquidity leaks and bridge logic flaws.",
  },
  {
    icon: "🔐",
    title: "Wallet Guard",
    description: "Approve a token, get drained. Not anymore.",
    details: "Detect and revoke malicious token approvals instantly.",
  },
  {
    icon: "📊",
    title: "Enterprise Reporting System",
    description: "Finally… an audit report that doesn't cost $50K.",
    details: "Branded PDF reports, generated in minutes — not months.",
  },
  {
    icon: "📡",
    title: "Mempool Monitoring",
    description: "See the attack coming before the attacker clicks send.",
    details:
      "Tracks malicious gas behavior, sandwich setup patterns, and toxic bundles live.",
  },
];

/**
 * Component for "FeatureModules" Slices.
 */
const FeatureModules = ({ slice }: FeatureModulesProps): JSX.Element => {
  return (
    <Bounded
      data-slice-type={slice.slice_type}
      data-slice-variation={slice.variation}
      className="bg-black text-gray-200"
    >
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-6xl font-black uppercase text-cyan-400 mb-16">
          System Modules Online
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {modules.map((module, index) => (
            <div
              key={index}
              className="bg-gray-900/50 border border-cyan-500/20 rounded-lg p-6 hover:border-cyan-500/50 transition-colors"
            >
              <div className="text-4xl mb-4">{module.icon}</div>
              <h3 className="text-xl font-bold text-cyan-400 mb-2">
                {module.title}
              </h3>
              <p className="text-gray-300 mb-3 font-medium">
                {module.description}
              </p>
              <p className="text-gray-400 text-sm">{module.details}</p>
            </div>
          ))}
        </div>
      </div>
    </Bounded>
  );
};

export default FeatureModules;
