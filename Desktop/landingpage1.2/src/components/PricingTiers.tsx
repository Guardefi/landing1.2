'use client';
import { motion } from 'framer-motion';

const tiers = [
  {
    icon: '🏁',
    name: 'Starter',
    price: '$99',
    period: '/month',
    description: 'Builders on ramen budgets who still want war-grade armor.',
    features: [
      '100 scans per month',
      'Basic threat dashboard',
      'Email support',
      'Core module access',
      'Standard SLA'
    ],
    cta: 'Deploy Starter',
    popular: false
  },
  {
    icon: '🛰️',
    name: 'Professional',
    price: '$499',
    period: '/month',
    description: 'Teams that tasted fire and refuse a round two.',
    features: [
      '1,000 scans per month',
      'Full platform access',
      'Priority support',
      'Custom integrations',
      'Advanced analytics',
      'API access'
    ],
    cta: 'Deploy Professional',
    popular: true
  },
  {
    icon: '🛡️',
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'Protocols, DAOs & L2s bent on surviving the next zero-day.',
    features: [
      'Unlimited everything',
      'On-premise deployment',
      'Dedicated strike team',
      'SLA guarantees',
      'Custom modules',
      'White-label options'
    ],
    cta: 'Contact Command',
    popular: false
  }
];

export default function PricingTiers() {
  return (
    <section className="relative py-32 px-8 z-20" id="pricing">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <h2 className="text-5xl md:text-6xl font-command font-bold cyan-glow mb-6">
            Pricing / Access Tiers
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Choose your level of defense. From indie builders to Fortune 500 fortresses.
          </p>
        </motion.div>

        {/* Pricing Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {tiers.map((tier, index) => (
            <motion.div
              key={tier.name}
              initial={{ opacity: 0, y: 60 }}
              whileInView={{ opacity: 1, y: 0 }}
              whileHover={{ 
                scale: 1.05, 
                boxShadow: tier.popular 
                  ? "0 30px 60px rgba(0, 255, 247, 0.4)" 
                  : "0 20px 40px rgba(0, 255, 247, 0.2)"
              }}
              transition={{ 
                duration: 0.8, 
                delay: index * 0.2,
                ease: [0.23, 1, 0.32, 1] 
              }}
              viewport={{ once: true }}
              className={`
                relative glass-morphism rounded-xl p-8 corner-accent
                ${tier.popular ? 'ring-2 ring-cyan-400 scale-105' : ''}
              `}
            >
              {/* Popular Badge */}
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-cyan-400 to-cyan-600 text-black px-6 py-2 rounded-full text-sm font-terminal font-bold">
                    MOST POPULAR
                  </span>
                </div>
              )}

              {/* Header */}
              <div className="text-center mb-8">
                <div className="text-5xl mb-4">{tier.icon}</div>
                <h3 className="text-2xl font-command font-bold text-white mb-2">
                  {tier.name}
                </h3>
                <div className="flex items-baseline justify-center gap-1 mb-4">
                  <span className="text-4xl font-command text-cyan-400">{tier.price}</span>
                  <span className="text-gray-400">{tier.period}</span>
                </div>
                <p className="text-sm text-gray-300 italic">
                  "{tier.description}"
                </p>
              </div>

              {/* Features */}
              <div className="mb-8">
                <h4 className="text-sm font-terminal text-cyan-400 mb-4 uppercase tracking-wide">
                  What You Get
                </h4>
                <ul className="space-y-3">
                  {tier.features.map((feature, i) => (
                    <li key={i} className="flex items-center text-sm text-gray-300">
                      <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3 pulse-glow"></div>
                      {feature}
                    </li>
                  ))}
                </ul>
              </div>

              {/* CTA Button */}
              <button className={`
                w-full py-4 rounded-lg font-bold text-lg transition-all duration-300
                ${tier.popular 
                  ? 'bg-cyan-400 text-black hover:bg-cyan-300 btn-glow' 
                  : 'bg-transparent border-2 border-cyan-400 text-cyan-400 hover:bg-cyan-400 hover:text-black'
                }
              `}>
                {tier.cta}
              </button>
            </motion.div>
          ))}
        </div>

        {/* Additional Info */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.4, ease: [0.23, 1, 0.32, 1] }}
          viewport={{ once: true }}
          className="text-center mt-16"
        >
          <p className="text-gray-400 text-sm">
            All plans include quantum-grade encryption, 24/7 monitoring, and our legendary support team.
            <br />
            Enterprise customers get dedicated war room access and custom threat intelligence.
          </p>
        </motion.div>
      </div>
    </section>
  );
} 