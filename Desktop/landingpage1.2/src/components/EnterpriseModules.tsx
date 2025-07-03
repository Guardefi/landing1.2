'use client';
import { motion } from 'framer-motion';

const enterpriseModules = [
  {
    icon: '🔮',
    name: 'Quantum Security',
    readiness: 'CRYSTALS-Kyber / Dilithium baked-in. Future-proof signatures, QKD simulation, quantum threat audits.',
    tier: 'CLASSIFIED'
  },
  {
    icon: '🧪',
    name: 'Simulation Sandbox',
    readiness: 'Multi-chain forks, private mempools, flash-loan + oracle-manip hack lab, time-travel block warp, chaos-engineering toggles.',
    tier: 'ADVANCED'
  },
  {
    icon: '📋',
    name: 'Compliance Grid',
    readiness: 'SOC 2 Type II, GDPR, PCI DSS, ISO 27001 autopilot. Evidence harvesting + exportable mappings.',
    tier: 'ENTERPRISE'
  },
  {
    icon: '🛂',
    name: 'Access Control Matrix',
    readiness: 'Zero-trust RBAC, ABAC, MFA hardware tokens, anomaly-aware session watchdog.',
    tier: 'FORTRESS'
  },
  {
    icon: '🧯',
    name: 'Recovery Engine',
    readiness: '15-min RTO hot-standby, point-in-time restore, immutable triple-region backups, chaos-tested weekly.',
    tier: 'IMMORTAL'
  },
  {
    icon: '📄',
    name: 'Threat Reporting System',
    readiness: 'Exec-level ROI dashboards, MITRE & NIST crosswalks, PoC-verified exploits, remediation runbooks.',
    tier: 'EXECUTIVE'
  }
];

export default function EnterpriseModules() {
  return (
    <section className="relative py-32 px-8 z-20 bg-gradient-to-b from-transparent via-war-room-abyss/30 to-transparent">
      <div className="max-w-7xl mx-auto">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
          viewport={{ once: true }}
          className="text-center mb-20"
        >
          <div className="inline-block px-6 py-2 bg-gradient-to-r from-cyber-cyan-dim to-cyber-cyan-base rounded-full text-black font-terminal text-sm font-bold mb-6">
            🧠 ENTERPRISE MODULES
          </div>
          <h2 className="text-5xl md:text-6xl font-command font-bold cyan-glow mb-6">
            Advanced Tier Capabilities
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            When Fortune 500 meets medieval war tactics. These modules separate the knights from the peasants.
          </p>
        </motion.div>

        {/* Enterprise Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {enterpriseModules.map((module, index) => (
            <motion.div
              key={module.name}
              initial={{ opacity: 0, x: index % 2 === 0 ? -60 : 60 }}
              whileInView={{ opacity: 1, x: 0 }}
              whileHover={{ scale: 1.02, boxShadow: "0 20px 40px rgba(0, 255, 247, 0.3)" }}
              transition={{ 
                duration: 0.8, 
                delay: index * 0.15,
                ease: [0.23, 1, 0.32, 1] 
              }}
              viewport={{ once: true }}
              className="glass-morphism rounded-xl p-8 corner-accent relative overflow-hidden"
            >
              {/* Tier Badge */}
              <div className="absolute top-4 right-4">
                <span className="px-3 py-1 bg-gradient-to-r from-cyan-400 to-cyan-600 text-black text-xs font-terminal font-bold rounded-full">
                  {module.tier}
                </span>
              </div>

              {/* Content */}
              <div className="flex items-start gap-4">
                <div className="text-4xl">{module.icon}</div>
                <div className="flex-1">
                  <h3 className="text-2xl font-command font-bold text-white mb-4">
                    {module.name}
                  </h3>
                  <p className="text-gray-300 leading-relaxed">
                    {module.readiness}
                  </p>
                </div>
              </div>

              {/* Combat Readiness Bar */}
              <div className="mt-6 pt-4 border-t border-cyan-400/20">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-terminal text-cyan-400 uppercase">Combat Readiness</span>
                  <span className="text-xs font-terminal text-green-400">OPERATIONAL</span>
                </div>
                <div className="w-full bg-war-room-steel rounded-full h-2">
                  <div className="bg-gradient-to-r from-cyan-400 to-green-400 h-full rounded-full w-full pulse-glow"></div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
} 