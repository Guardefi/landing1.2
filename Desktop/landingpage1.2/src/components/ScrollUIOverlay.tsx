'use client';
import React, { useEffect } from 'react';
import AnimatedSection from './AnimatedSection';
import { useScrollSync } from './useScrollSync';

// Section data with all landing page content converted to scroll-driven format
const sections = [
  {
    id: 'intro',
    title: 'Hello Dark Forest,',
    subtitle: 'Meet Scorpius.',
    description: 'In the vast expanse of the digital cosmos, where threats lurk in every shadow, a new guardian awakens.',
    align: 'center',
    theme: 'intro',
    minimal: true
  },
  {
    id: 'scorpius-core',
    title: 'ScorpiusCore',
    subtitle: 'The Next-Gen Cyber Defense Engine',
    description: 'A living, breathing core of wireframe intelligence and pulsing quantum energy. The heart of your medieval high-tech alien war room.',
    metrics: [
      { label: 'Threats Neutralized', value: '2,847,293', trend: '+12.3%' },
      { label: 'Assets Protected', value: '$847B', trend: '+98.7%' },
      { label: 'Zero-Days Stopped', value: '15,847', trend: '+156%' }
    ],
    align: 'center',
    theme: 'primary'
  },
  {
    id: 'quantum-detection',
    title: 'Quantum Threat Detection',
    subtitle: 'See the Unseen',
    description: 'AI-powered, zero-latency threat recognition that maps every anomaly and shadow, instantly neutralizing attacks before they manifest.',
    features: [
      'Sub-100ms response time',
      'ML threat classification ≈95%',
      'Real-time bait contracts',
      'Private mempool mirroring'
    ],
    align: 'left',
    theme: 'detection'
  },
  {
    id: 'adaptive-defense',
    title: 'Adaptive Defense Layers',
    subtitle: 'Multi-Protocol. Multi-Chain. Multi-Reality.',
    description: 'Dynamic energy shields and protocol firewalls that adapt in real-time to the evolving threatscape across all blockchain networks.',
    features: [
      'Cross-chain monitoring (ETH/BSC/ARB/Polygon)',
      'Flash-loan executor integration',
      'Sandwich counter-measures',
      'Validator-quorum checks'
    ],
    align: 'right',
    theme: 'defense'
  },
  {
    id: 'enterprise-command',
    title: 'Enterprise Command',
    subtitle: 'Total Control. Infinite Insight.',
    description: 'Executive dashboards, compliance automation, and instant incident response. Everything you need for Fortune 500-grade security management.',
    features: [
      'SOC 2 Type II compliance',
      'Real-time threat intelligence',
      'Automated incident response',
      'Executive-level reporting'
    ],
    align: 'center',
    theme: 'enterprise'
  },
  {
    id: 'defense-protocol',
    title: 'Defense Protocol',
    subtitle: 'Activated',
    description: 'Medieval high-tech alien war room meets Fortune 500 cybersecurity. Your quantum defense against the Dark Forest.',
    metrics: [
      { label: 'Threats Neutralized', value: '2,847,293', trend: '+12.3%' },
      { label: 'Assets Protected', value: '$847B', trend: '+98.7%' },
      { label: 'Zero-Days Stopped', value: '15,847', trend: '+156%' }
    ],
    align: 'center',
    theme: 'hero',
    cta: ['Deploy Defense Core', 'Live Demo']
  },
  {
    id: 'firepower-modules',
    title: 'Under-the-Hood Firepower',
    subtitle: 'Medieval Precision Meets Alien Technology',
    description: 'Each module is a weapon forged in the quantum fires of cybersecurity excellence. Seven combat-ready systems.',
    modules: [
      { icon: '🐝', name: 'Hive Alert', uptime: '99.99%', response: '<100ms' },
      { icon: '🧬', name: 'Bytecode Engine', uptime: '99.97%', response: '<50ms' },
      { icon: '🤖', name: 'AI Trading Bot', uptime: '99.98%', response: '<25ms' },
      { icon: '📡', name: 'Mempool Monitor', uptime: '99.99%', response: '<15s' },
      { icon: '🌉', name: 'Bridge Network', uptime: '99.96%', response: '<200ms' },
      { icon: '🔐', name: 'Wallet Guard', uptime: '99.99%', response: '<10ms' },
      { icon: '📊', name: 'Enterprise Reports', uptime: '99.95%', response: '<5min' }
    ],
    align: 'left',
    theme: 'modules'
  },
  {
    id: 'enterprise-tier',
    title: 'Advanced Tier Capabilities',
    subtitle: 'When Fortune 500 Meets Medieval War Tactics',
    description: 'These modules separate the knights from the peasants. Enterprise-grade capabilities for the digital battlefield.',
    enterpriseModules: [
      { icon: '🔮', name: 'Quantum Security', tier: 'CLASSIFIED' },
      { icon: '🧪', name: 'Simulation Sandbox', tier: 'ADVANCED' },
      { icon: '📋', name: 'Compliance Grid', tier: 'ENTERPRISE' },
      { icon: '🛂', name: 'Access Control Matrix', tier: 'FORTRESS' },
      { icon: '🧯', name: 'Recovery Engine', tier: 'IMMORTAL' },
      { icon: '📄', name: 'Threat Reporting', tier: 'EXECUTIVE' }
    ],
    align: 'right',
    theme: 'enterprise-advanced'
  },
  {
    id: 'pricing-tiers',
    title: 'Pricing / Access Tiers',
    subtitle: 'Choose Your Level of Defense',
    description: 'From indie builders to Fortune 500 fortresses. Every tier built for the digital battlefield.',
    pricing: [
      { icon: '🏁', name: 'Starter', price: '$99/month', description: 'Builders on ramen budgets who still want war-grade armor.' },
      { icon: '🛰️', name: 'Professional', price: '$499/month', description: 'Teams that tasted fire and refuse a round two.', popular: true },
      { icon: '🛡️', name: 'Enterprise', price: 'Custom', description: 'Protocols, DAOs & L2s bent on surviving the next zero-day.' }
    ],
    align: 'center',
    theme: 'pricing'
  },
  {
    id: 'battle-tested',
    title: 'Battle-Tested by Leaders',
    subtitle: 'Trusted by Fortune 500 & DeFi Protocols',
    description: 'ScorpiusCore protects over $847B in digital assets. Join the defense against the Dark Forest.',
    testimonials: [
      { quote: 'ScorpiusCore detected a flash loan attack 3 seconds before execution. Saved us $2.3M.', author: 'Marcus Chen', role: 'CTO, DeFi Protocol' },
      { quote: 'The medieval aesthetic with Fortune 500 functionality is exactly what our board needed.', author: 'Sarah Williams', role: 'CISO, TechFlow Industries' },
      { quote: 'Finally, a security platform that doesn\'t look like it was built in 2015.', author: 'Alex Rodriguez', role: 'Security Lead, CryptoVault' }
    ],
    align: 'left',
    theme: 'social-proof'
  },
  {
    id: 'deploy-now',
    title: 'Ready to Deploy?',
    subtitle: 'The Dark Forest is Watching',
    description: 'Book a live demo or deploy now—because "maybe secure" is just another way to say next victim.',
    cta: ['Book Live Demo', 'Deploy Now'],
    emergency: true,
    align: 'center',
    theme: 'final-cta'
  }
];

// Metric display component
function MetricCard({ label, value, trend }: { label: string; value: string; trend: string }) {
  return (
    <div className="glass-morphism rounded-lg p-4 text-center corner-accent">
      <div className="text-2xl font-command text-cyan-400 mb-1">{value}</div>
      <div className="text-xs text-gray-400 mb-1">{label}</div>
      <div className={`text-xs font-bold ${trend.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
        {trend}
      </div>
    </div>
  );
}

// Feature list component
function FeatureList({ features }: { features: string[] }) {
  return (
    <ul className="space-y-2 mt-4">
      {features.map((feature, index) => (
        <li key={index} className="flex items-center text-sm text-gray-300">
          <div className="w-2 h-2 bg-cyan-400 rounded-full mr-3 pulse-glow"></div>
          {feature}
        </li>
      ))}
    </ul>
  );
}

// Module grid component
function ModuleGrid({ modules }: { modules: any[] }) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
      {modules.map((module, index) => (
        <div key={index} className="glass-morphism rounded-lg p-3 text-center corner-accent">
          <div className="text-2xl mb-2">{module.icon}</div>
          <div className="text-xs text-cyan-400 font-bold mb-1">{module.name}</div>
          <div className="text-xs text-gray-400">{module.response}</div>
        </div>
      ))}
    </div>
  );
}

// Main overlay component
export default function ScrollUIOverlay() {
  const { scroll, isAutoScrolling, toggleAutoScroll } = useScrollSync();
  const activeIndex = Math.floor(scroll * (sections.length - 1) + 0.5);
  const activeSection = sections[activeIndex];

  // Keyboard navigation
  useEffect(() => {
    function handleKeyDown(e: KeyboardEvent) {
      if (e.key === 'ArrowDown' || e.key === ' ') {
        e.preventDefault();
        const nextSection = Math.min(activeIndex + 1, sections.length - 1);
        const scrollTarget = (nextSection / (sections.length - 1)) * (document.body.scrollHeight - window.innerHeight);
        window.scrollTo({ top: scrollTarget, behavior: 'smooth' });
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        const prevSection = Math.max(activeIndex - 1, 0);
        const scrollTarget = (prevSection / (sections.length - 1)) * (document.body.scrollHeight - window.innerHeight);
        window.scrollTo({ top: scrollTarget, behavior: 'smooth' });
      }
    }

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [activeIndex]);

  return (
    <>
      {/* Navigation dots */}
      <nav className="fixed right-8 top-1/2 transform -translate-y-1/2 z-30" role="navigation" aria-label="Section navigation">
        <div className="flex flex-col space-y-2">
          {sections.map((section, index) => (
            <button
              key={section.id}
              onClick={() => {
                const scrollTarget = (index / (sections.length - 1)) * (document.body.scrollHeight - window.innerHeight);
                window.scrollTo({ top: scrollTarget, behavior: 'smooth' });
              }}
              className={`w-3 h-3 rounded-full transition-all duration-300 ${
                index === activeIndex 
                  ? 'bg-cyan-400 scale-125 shadow-lg shadow-cyan-400/50' 
                  : 'bg-gray-600 hover:bg-gray-400'
              }`}
              aria-label={`Go to ${section.title} section`}
            />
          ))}
        </div>
      </nav>

      {/* Section indicator and auto-scroll control */}
      <div className="fixed top-8 left-8 z-30 flex flex-col space-y-2">
        <div className="glass-morphism rounded-lg px-4 py-2">
          <div className="text-xs text-gray-400 font-terminal">
            {String(activeIndex + 1).padStart(2, '0')} / {String(sections.length).padStart(2, '0')}
          </div>
          <div className="text-sm text-cyan-400 font-command">
            {activeSection?.id.toUpperCase()}
          </div>
        </div>
        
        {/* Auto-scroll toggle */}
        <button
          onClick={toggleAutoScroll}
          className={`glass-morphism rounded-lg px-4 py-2 btn-glow transition-all duration-300 ${
            isAutoScrolling 
              ? 'bg-cyan-400 text-black' 
              : 'text-cyan-400 hover:bg-cyan-400/20'
          }`}
        >
          <div className="text-xs font-terminal">
            {isAutoScrolling ? '⏸️ PAUSE' : '▶️ AUTO'}
          </div>
        </button>
      </div>

      {/* Main content overlay - always visible */}
      <div className="pointer-events-none fixed inset-0 flex flex-col items-center justify-center z-20">
        {sections.map((section, index) => (
          <AnimatedSection 
            key={section.id} 
            active={activeIndex === index} 
            align={section.align as 'left' | 'center' | 'right'}
          >
            {section.minimal ? (
              // Minimal intro section
              <div className="text-center">
                <h1 className="text-5xl md:text-7xl lg:text-8xl font-command font-bold cyan-glow mb-6">
                  {section.title}
                </h1>
                <h2 className="text-3xl md:text-4xl lg:text-5xl text-cyan-400 mb-8 font-light">
                  {section.subtitle}
                </h2>
                <p className="text-lg md:text-xl lg:text-2xl text-gray-300 leading-relaxed max-w-3xl mx-auto">
                  {section.description}
                </p>
              </div>
            ) : (
              // Regular sections
              <div className={`
                max-w-5xl mx-auto p-8 glass-morphism rounded-xl corner-accent
                ${section.align === 'left' ? 'ml-0 md:ml-16' : ''}
                ${section.align === 'right' ? 'mr-0 md:mr-16' : ''}
                ${section.align === 'center' ? 'mx-auto' : ''}
              `}>
                {/* Header */}
                <div className={`mb-6 ${section.align === 'center' ? 'text-center' : section.align === 'right' ? 'text-right' : 'text-left'}`}>
                  <h1 className="text-4xl md:text-6xl lg:text-7xl font-command font-bold cyan-glow mb-4">
                    {section.title}
                  </h1>
                  <h2 className="text-xl md:text-2xl lg:text-3xl text-cyan-400 mb-4 font-light">
                    {section.subtitle}
                  </h2>
                  <p className="text-base md:text-lg lg:text-xl text-gray-200 leading-relaxed">
                    {section.description}
                  </p>
                </div>

                {/* Metrics */}
                {section.metrics && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                    {section.metrics.map((metric, idx) => (
                      <MetricCard key={idx} {...metric} />
                    ))}
                  </div>
                )}

                {/* Features */}
                {section.features && (
                  <FeatureList features={section.features} />
                )}

                {/* Modules */}
                {section.modules && (
                  <ModuleGrid modules={section.modules} />
                )}

                {/* Enterprise Modules */}
                {section.enterpriseModules && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-6">
                    {section.enterpriseModules.map((module, idx) => (
                      <div key={idx} className="glass-morphism rounded-lg p-4 corner-accent">
                        <div className="text-2xl mb-2">{module.icon}</div>
                        <div className="text-sm text-cyan-400 font-bold mb-1">{module.name}</div>
                        <div className="text-xs text-gray-400">{module.tier}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Pricing */}
                {section.pricing && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                    {section.pricing.map((tier, idx) => (
                      <div key={idx} className={`glass-morphism rounded-lg p-4 corner-accent ${tier.popular ? 'ring-2 ring-cyan-400' : ''}`}>
                        <div className="text-2xl mb-2">{tier.icon}</div>
                        <div className="text-lg text-cyan-400 font-bold mb-1">{tier.name}</div>
                        <div className="text-sm text-white font-bold mb-2">{tier.price}</div>
                        <div className="text-xs text-gray-400">{tier.description}</div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Testimonials */}
                {section.testimonials && (
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                    {section.testimonials.map((testimonial, idx) => (
                      <article key={idx} className="glass-morphism rounded-lg p-4 corner-accent">
                        <blockquote className="text-xs text-gray-300 italic mb-2">"{testimonial.quote}"</blockquote>
                        <cite className="text-xs text-cyan-400 font-bold block">{testimonial.author}</cite>
                        <span className="text-xs text-gray-400">{testimonial.role}</span>
                      </article>
                    ))}
                  </div>
                )}

                {/* Call to action */}
                <div className={`mt-8 ${section.align === 'center' ? 'text-center' : section.align === 'right' ? 'text-right' : 'text-left'}`}>
                  {section.cta && (
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                      <button className="btn-glow bg-cyan-400 text-black font-bold px-8 py-3 rounded-lg hover:bg-cyan-300 transition-all duration-300 pointer-events-auto">
                        {section.cta[0]}
                      </button>
                      {section.cta[1] && (
                        <button className="btn-glow bg-transparent border-2 border-cyan-400 text-cyan-400 font-bold px-8 py-3 rounded-lg hover:bg-cyan-400 hover:text-black transition-all duration-300 pointer-events-auto">
                          {section.cta[1]}
                        </button>
                      )}
                    </div>
                  )}
                  
                  {section.emergency && (
                    <div className="glass-morphism rounded-lg p-4 corner-accent mt-6">
                      <div className="text-lg font-bold text-red-400 mb-2">🚨 Under Active Attack?</div>
                      <div className="text-sm text-gray-300 mb-4">Emergency response team standing by 24/7</div>
                      <button className="bg-red-500 text-white font-bold px-6 py-2 rounded-lg hover:bg-red-400 transition-all duration-300 pointer-events-auto">
                        Emergency Hotline
                      </button>
                    </div>
                  )}
                  
                  {!section.cta && !section.emergency && (
                    <button className="btn-glow bg-cyan-400 text-black font-bold px-8 py-3 rounded-lg hover:bg-cyan-300 transition-all duration-300 pointer-events-auto">
                      Explore {section.title}
                    </button>
                  )}
                </div>
              </div>
            )}
          </AnimatedSection>
        ))}
      </div>

      {/* Skip to content link for accessibility */}
      <a 
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-cyan-400 text-black px-4 py-2 rounded z-50"
      >
        Skip to main content
      </a>
    </>
  );
} 