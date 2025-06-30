"use client";

import { Content } from "@prismicio/client";
import { SliceComponentProps } from "@prismicio/react";
import { Bounded } from "@/components/Bounded";

/**
 * Props for `ThreatReporting`.
 */
export type ThreatReportingProps =
  SliceComponentProps<Content.ThreatReportingSlice>;

const reportingFeatures = [
  {
    icon: "📄",
    title: "Executive Summaries",
    description:
      "Explained like you're talking to a boardroom, not a dev team.",
    details: "One-click C-level PDFs.",
  },
  {
    icon: "🛠️",
    title: "Technical Deep Dives",
    description: "Every line of the exploit, every variable. Annotated.",
    details: "Source-diffed. Transaction-traced. No hand-waving.",
  },
  {
    icon: "📊",
    title: "Compliance Mapping",
    description: "We mapped it so you don't have to.",
    details:
      "NIST, OWASP, ISO27001 — all crosswalked, exportable, and audit-ready.",
  },
  {
    icon: "🧨",
    title: "Incident Response",
    description: "When shit hits the fan, this hits back.",
    details:
      "Automated breach analysis, impact breakdowns, and recovery playbooks.",
  },
];

/**
 * Component for "ThreatReporting" Slices.
 */
const ThreatReporting = ({ slice }: ThreatReportingProps): JSX.Element => {
  return (
    <Bounded
      data-slice-type={slice.slice_type}
      data-slice-variation={slice.variation}
      className="bg-gray-900 text-gray-200"
    >
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-6xl font-black uppercase text-red-400 mb-4">
          📄 Threat Reporting System
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-16">
          {reportingFeatures.map((feature, index) => (
            <div
              key={index}
              className="bg-black/50 border border-red-500/20 rounded-lg p-6 hover:border-red-500/50 transition-colors"
            >
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-bold text-red-400 mb-2">
                {feature.title}
              </h3>
              <p className="text-gray-300 mb-3 font-medium">
                {feature.description}
              </p>
              <p className="text-gray-400 text-sm">{feature.details}</p>
            </div>
          ))}
        </div>
      </div>
    </Bounded>
  );
};

export default ThreatReporting;
