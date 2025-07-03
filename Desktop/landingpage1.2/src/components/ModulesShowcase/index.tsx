'use client';
import { motion } from 'framer-motion';
import ModuleCard from './ModuleCard';

const modules = [
  {
    icon: '🐝',
    name: 'Hive Alert',
    pitch: 'They won\'t know they\'ve been flagged—until the funds evaporate.',
    firepower: 'Real-time bait contracts, ML threat detection, gas-pattern sniping, private mempool mirroring.',
    uptime: '99.99%',
    response: '<100ms',
    specs: [
      'Sub-millisecond detection',
      'Private mempool monitoring',
      'ML threat classification',
      'Automated honeypot deployment'
    ]
  },
  {
    icon: '🧬',
    name: 'Bytecode Similarity Engine',
    pitch: 'Copy-paste devs get publicly executed.',
    firepower: 'AST diffing, opcode graph clustering, zero-day clone detection, exploit-trail heat-maps.',
    uptime: '99.97%',
    response: '<50ms',
    specs: [
      'AST differential analysis',
      'Opcode graph clustering',
      'Zero-day clone detection',
      'Exploit trail mapping'
    ]
  },
  {
    icon: '🤖',
    name: 'AI Trading Bot',
    pitch: 'Front-runs the frontrunners.',
    firepower: 'Sub-100 ms mempool scan (Rust), ML profit classifier ≈95%, flash-loan executor (Aave/Balancer/dYdX), cross-DEX arb & sandwich counter-measures.',
    uptime: '99.98%',
    response: '<25ms',
    specs: [
      'Rust-powered mempool scanning',
      '95% ML profit classification',
      'Flash-loan integration',
      'Cross-DEX arbitrage'
    ]
  },
  {
    icon: '📡',
    name: 'Mempool Monitoring',
    pitch: 'See the strike before the attacker clicks send.',
    firepower: 'Multi-chain feed (ETH/BSC/Arb/Polygon), toxic-bundle radar, whale-move tracker, 15s sandwich pre-alerts.',
    uptime: '99.99%',
    response: '<15s',
    specs: [
      'Multi-chain monitoring',
      'Toxic bundle detection',
      'Whale movement tracking',
      'Real-time pre-alerts'
    ]
  },
  {
    icon: '🌉',
    name: 'Cross-Chain Bridge Network',
    pitch: 'Bridge hacks get smothered in-flight.',
    firepower: 'Liquidity leak radar, validator-quorum checks, emergency auto-pause, health scoring across ETH↔BSC↔Arb↔Polygon↔Solana.',
    uptime: '99.96%',
    response: '<200ms',
    specs: [
      'Liquidity leak detection',
      'Validator quorum monitoring',
      'Emergency pause protocols',
      'Cross-chain health scoring'
    ]
  },
  {
    icon: '🔐',
    name: 'Wallet Guard',
    pitch: 'Approve a token, get drained? Not on our watch.',
    firepower: 'Infinite-approval detector, proxy-risk scoring, one-click revocation, insurance API hooks.',
    uptime: '99.99%',
    response: '<10ms',
    specs: [
      'Infinite approval detection',
      'Proxy risk assessment',
      'One-click revocation',
      'Insurance integration'
    ]
  },
  {
    icon: '📊',
    name: 'Enterprise Reporting',
    pitch: 'An audit report that doesn\'t cost $50K—or suck.',
    firepower: 'Branded PDFs in minutes, CVSS 3.1 scoring with chain-specific modifiers, board-ready summaries + diff-annotated tech deep dives.',
    uptime: '99.95%',
    response: '<5min',
    specs: [
      'Automated PDF generation',
      'CVSS 3.1 scoring',
      'Executive summaries',
      'Technical deep dives'
    ]
  }
];

export default function ModulesShowcase() {
  return (
    <section className="relative py-32 px-8 z-20" id="modules">
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
            Under-the-Hood Firepower
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Each module is a weapon forged in the quantum fires of cybersecurity excellence. 
            Medieval precision meets alien technology.
          </p>
        </motion.div>

        {/* Modules Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {modules.map((module, index) => (
            <motion.div
              key={module.name}
              initial={{ opacity: 0, y: 60 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ 
                duration: 0.8, 
                delay: index * 0.1,
                ease: [0.23, 1, 0.32, 1] 
              }}
              viewport={{ once: true }}
            >
              <ModuleCard {...module} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
} 