import * as React from 'react'
import { motion } from 'framer-motion'
import { FiTarget, FiShield, FiZap, FiCode, FiDatabase, FiMonitor } from 'react-icons/fi'

const LandingHeroDemo: React.FC = () => {
  return (
    <div className="relative min-h-screen flex items-center justify-center px-6">
      {/* Background Grid */}
      <div className="absolute inset-0 cyber-grid opacity-20" />
      
      {/* Floating Particles */}
      <div className="absolute inset-0 overflow-hidden">
        {Array.from({ length: 30 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-cyan-500/50 rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              y: [-20, 20],
              opacity: [0.2, 0.8, 0.2],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
          />
        ))}
      </div>

      <div className="relative max-w-7xl mx-auto">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Side - Hero Content */}
          <motion.div
            className="text-center lg:text-left"
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8 }}
          >
            {/* Status Badge */}
            <motion.div
              className="inline-flex items-center gap-2 bg-cyan-500/10 border border-cyan-500/30 rounded-cyber px-4 py-2 mb-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
              <span className="text-cyan-400 font-tech text-sm">SYSTEM ONLINE</span>
            </motion.div>

            {/* Main Heading */}
            <motion.h1
              className="text-5xl md:text-7xl font-cyber font-bold text-text-primary mb-6 leading-tight"
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
            >
              SCORPIUS
              <span className="block text-cyan-400 glow-text">ENTERPRISE</span>
            </motion.h1>

            {/* Subtitle */}
            <motion.p
              className="text-xl md:text-2xl text-text-secondary mb-8 max-w-2xl"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              Next-generation blockchain warfare platform. Deploy, monitor, and dominate the MEV battlefield.
            </motion.p>

            {/* Key Features */}
            <motion.div
              className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-8"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              {[
                { icon: FiTarget, label: 'MEV Targeting' },
                { icon: FiShield, label: 'Security First' },
                { icon: FiZap, label: 'Lightning Fast' },
                { icon: FiCode, label: 'Smart Contracts' },
                { icon: FiDatabase, label: 'Real-time Data' },
                { icon: FiMonitor, label: 'Live Dashboard' },
              ].map((feature, i) => (
                <motion.div
                  key={i}
                  className="flex items-center gap-2 text-sm"
                  whileHover={{ scale: 1.05 }}
                >
                  <feature.icon className="w-4 h-4 text-cyan-400" />
                  <span className="text-text-secondary">{feature.label}</span>
                </motion.div>
              ))}
            </motion.div>

            {/* CTA Buttons */}
            <motion.div
              className="flex flex-col sm:flex-row gap-4"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 }}
            >
              <motion.button
                className="neon-button px-8 py-4 text-lg"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Deploy Arsenal
              </motion.button>
              
              <motion.button
                className="bg-transparent border-2 border-surface-300 text-text-primary px-8 py-4 rounded-cyber font-tech font-semibold uppercase tracking-wider hover:border-cyan-400 hover:text-cyan-400 transition-all duration-300"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                Watch Demo
              </motion.button>
            </motion.div>
          </motion.div>

          {/* Right Side - Terminal/Stats */}
          <motion.div
            className="space-y-6"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            {/* Terminal Window */}
            <div className="war-room-card p-6">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-3 h-3 bg-red-500 rounded-full" />
                <div className="w-3 h-3 bg-yellow-500 rounded-full" />
                <div className="w-3 h-3 bg-green-500 rounded-full" />
                <span className="ml-4 text-xs text-text-secondary font-mono">
                  scorpius-terminal
                </span>
              </div>
              
              <div className="font-mono text-sm space-y-2">
                <div className="text-cyan-400">$ scorpius --status</div>
                <div className="text-green-400">✓ MEV Bot Network: ONLINE</div>
                <div className="text-green-400">✓ Arbitrage Engine: ACTIVE</div>
                <div className="text-green-400">✓ Security Protocols: ENABLED</div>
                <div className="text-cyan-400">$ profit --today</div>
                <div className="text-text-primary">
                  <span className="text-green-400">+$127,430.52</span> ETH extracted
                </div>
                <div className="text-cyan-400 animate-pulse">█</div>
              </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-4">
              {[
                { label: 'Active Bots', value: '24/7', color: 'text-green-400' },
                { label: 'Success Rate', value: '97.3%', color: 'text-cyan-400' },
                { label: 'Total Volume', value: '$2.1M', color: 'text-yellow-400' },
                { label: 'Uptime', value: '99.99%', color: 'text-green-400' },
              ].map((stat, i) => (
                <motion.div
                  key={i}
                  className="war-room-card p-4 text-center"
                  whileHover={{ scale: 1.05 }}
                  transition={{ type: "spring", stiffness: 300 }}
                >
                  <div className={`text-2xl font-bold ${stat.color} mb-1`}>
                    {stat.value}
                  </div>
                  <div className="text-xs text-text-secondary uppercase tracking-wide">
                    {stat.label}
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Floating Glow Effects */}
      <div className="absolute top-1/4 left-10 w-32 h-32 bg-cyan-500/10 rounded-full blur-xl" />
      <div className="absolute bottom-1/4 right-10 w-48 h-48 bg-cyan-500/5 rounded-full blur-xl" />
    </div>
  )
}

export default LandingHeroDemo
