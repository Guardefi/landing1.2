"use client";

import { Content } from "@prismicio/client";
import { SliceComponentProps } from "@prismicio/react";
import { Bounded } from "@/components/Bounded";

/**
 * Props for `EnterpriseModules`.
 */
export type EnterpriseModulesProps =
  SliceComponentProps<Content.EnterpriseModulesSlice>;

const enterpriseModules = [
  {
    icon: "🔮",
    title: "Quantum Security",
    description: "Post-quantum ready.",
    details: "Your encryption is already outdated — we fixed that.",
  },
  {
    icon: "🧪",
    title: "Simulation Sandbox",
    description: "Run the exploit before they do.",
    details:
      "Forked-chain environments for attack modeling, impact testing, and validation.",
  },
  {
    icon: "📋",
    title: "Compliance Grid",
    description: "SOC2, GDPR, ISO... handled.",
    details:
      "Audit logs, exportable mappings, and automated compliance workflows.",
  },
  {
    icon: "🛂",
    title: "Access Control Matrix",
    description: "Decentralized ops. Centralized control.",
    details: "Fine-grained RBAC for security teams that actually scale.",
  },
  {
    icon: "📡",
    title: "Monitoring & Logs",
    description: "Dashboards for real-time paranoia.",
    details: "Node metrics, attack telemetry, Slack/webhook alerts — all live.",
  },
  {
    icon: "🧯",
    title: "Recovery Engine",
    description: "Chaos-engineered disaster recovery.",
    details: "15-minute RTO. Full backups. Bulletproof fallback routines.",
  },
];

/**
 * Component for "EnterpriseModules" Slices.
 */
const EnterpriseModules = ({ slice }: EnterpriseModulesProps): JSX.Element => {
  return (
    <Bounded
      data-slice-type={slice.slice_type}
      data-slice-variation={slice.variation}
      className="bg-gray-900 text-gray-200"
    >
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-6xl font-black uppercase text-amber-400 mb-4">
          Enterprise Modules
        </h2>
        <p className="text-center text-xl text-gray-400 mb-16">
          Optional Add-On Tier
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {enterpriseModules.map((module, index) => (
            <div
              key={index}
              className="bg-black/50 border border-amber-500/20 rounded-lg p-6 hover:border-amber-500/50 transition-colors"
            >
              <div className="text-4xl mb-4">{module.icon}</div>
              <h3 className="text-xl font-bold text-amber-400 mb-2">
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

export default EnterpriseModules;
