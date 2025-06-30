"use client";

import { Content } from "@prismicio/client";
import { SliceComponentProps } from "@prismicio/react";
import { Bounded } from "@/components/Bounded";

/**
 * Props for `Pricing`.
 */
export type PricingProps = SliceComponentProps<Content.PricingSlice>;

const pricingTiers = [
  {
    icon: "🏁",
    name: "Starter",
    price: "$99/mo",
    description: "For builders who want war-grade security on a ramen budget.",
    features: ["100 contract scans", "Basic dashboards", "Email support"],
  },
  {
    icon: "🛰️",
    name: "Professional",
    price: "$499/mo",
    description:
      "For teams who've already been burned and won't let it happen again.",
    features: [
      "Full platform access",
      "1,000 scans",
      "Priority support",
      "Custom integrations",
    ],
    popular: true,
  },
  {
    icon: "🛡️",
    name: "Enterprise",
    price: "Custom",
    description:
      "For protocols, DAOs, and chains that want to survive the next zero-day.",
    features: [
      "Unlimited scanning & simulations",
      "Private deployment",
      "Dedicated response team",
      "SLA guarantees",
    ],
  },
];

/**
 * Component for "Pricing" Slices.
 */
const Pricing = ({ slice }: PricingProps): JSX.Element => {
  return (
    <Bounded
      data-slice-type={slice.slice_type}
      data-slice-variation={slice.variation}
      className="bg-black text-gray-200"
    >
      <div className="mx-auto max-w-6xl">
        <h2 className="text-center text-6xl font-black uppercase text-cyan-400 mb-4">
          Pricing / Access Tiers
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16">
          {pricingTiers.map((tier, index) => (
            <div
              key={index}
              className={`relative rounded-lg p-8 ${
                tier.popular
                  ? "bg-cyan-500/10 border-2 border-cyan-500"
                  : "bg-gray-900/50 border border-gray-700"
              }`}
            >
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-cyan-500 text-black px-4 py-1 rounded-full text-sm font-bold">
                    MOST POPULAR
                  </span>
                </div>
              )}

              <div className="text-4xl mb-4">{tier.icon}</div>
              <h3 className="text-2xl font-bold text-cyan-400 mb-2">
                {tier.name}
              </h3>
              <div className="text-4xl font-bold text-white mb-4">
                {tier.price}
              </div>
              <p className="text-gray-400 mb-6">{tier.description}</p>

              <ul className="space-y-3 mb-8">
                {tier.features.map((feature, featureIndex) => (
                  <li
                    key={featureIndex}
                    className="flex items-center text-gray-300"
                  >
                    <span className="text-cyan-400 mr-3">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>

              <button
                className={`w-full py-3 px-6 rounded-lg font-bold transition-colors ${
                  tier.popular
                    ? "bg-cyan-500 hover:bg-cyan-600 text-black"
                    : "border border-cyan-500 hover:bg-cyan-500/10 text-cyan-400"
                }`}
              >
                {tier.price === "Custom" ? "Contact Sales" : "Get Started"}
              </button>
            </div>
          ))}
        </div>

        <div className="text-center mt-16">
          <h3 className="text-4xl font-bold text-cyan-400 mb-4">
            Ready to activate your defense grid?
          </h3>
          <p className="text-xl text-gray-300 mb-8">
            Book a live demo or deploy the platform now — your blockchain assets
            deserve battlefield-grade protection.
          </p>
          <div className="flex gap-4 justify-center">
            <button className="bg-cyan-500 hover:bg-cyan-600 text-black font-bold py-4 px-8 rounded-lg transition-colors">
              Launch Terminal
            </button>
            <button className="border border-cyan-500 hover:bg-cyan-500/10 text-cyan-400 font-bold py-4 px-8 rounded-lg transition-colors">
              Schedule Demo
            </button>
          </div>
        </div>
      </div>
    </Bounded>
  );
};

export default Pricing;
