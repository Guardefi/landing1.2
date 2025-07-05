import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { gsap } from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'

gsap.registerPlugin(ScrollTrigger)

interface Module {
  id: string
  name: string
  description: string
  icon: string
  features: string[]
  status: 'active' | 'beta' | 'coming-soon'
  color: string
}

const modules: Module[] = [
  {
    id: 'autonomous-agents',
    name: 'Autonomous Agents',
    description: 'Deploy intelligent agents that can learn, adapt, and execute complex tasks without human intervention.',
    icon: '🤖',
    color: 'from-cyan-500 to-blue-500',
    status: 'active',
    features: [
      'Self-learning capabilities',
      'Multi-modal processing',
      'Real-time decision making',
      'Cross-platform integration'
    ]
  },
  {
    id: 'workflow-orchestration',
    name: 'Workflow Orchestration',
    description: 'Create sophisticated workflows that connect multiple AI agents and external systems seamlessly.',
    icon: '⚡',
    color: 'from-cyan-400 to-teal-500',
    status: 'active',
    features: [
      'Visual workflow builder',
      'Conditional logic',
      'Error handling & retries',
      'Performance monitoring'
    ]
  },
  {
    id: 'real-time-analytics',
    name: 'Real-time Analytics',
    description: 'Monitor and analyze your AI operations with comprehensive dashboards and insights.',
    icon: '📊',
    color: 'from-cyan-600 to-blue-600',
    status: 'active',
    features: [
      'Live performance metrics',
      'Custom dashboards',
      'Predictive insights',
      'Export capabilities'
    ]
  },
  {
    id: 'enterprise-security',
    name: 'Enterprise Security',
    description: 'Bank-grade security with end-to-end encryption, audit trails, and compliance management.',
    icon: '🔒',
    color: 'from-cyan-500 to-indigo-500',
    status: 'active',
    features: [
      'End-to-end encryption',
      'Role-based access',
      'Audit logging',
      'Compliance reporting'
    ]
  },
  {
    id: 'api-gateway',
    name: 'API Gateway',
    description: 'Unified API layer with rate limiting, authentication, and intelligent routing.',
    icon: '🌐',
    color: 'from-cyan-400 to-blue-400',
    status: 'beta',
    features: [
      'Rate limiting',
      'API versioning',
      'Load balancing',
      'Request transformation'
    ]
  },
  {
    id: 'quantum-processing',
    name: 'Quantum Processing',
    description: 'Next-generation quantum-enhanced AI processing for complex optimization problems.',
    icon: '⚛️',
    color: 'from-cyan-600 to-purple-600',
    status: 'coming-soon',
    features: [
      'Quantum algorithms',
      'Optimization engines',
      'Hybrid processing',
      'Research collaboration'
    ]
  }
]

const ModulesShowcase: React.FC = () => {
  const containerRef = useRef<HTMLDivElement>(null)
  const modulesRef = useRef<HTMLDivElement[]>([])

  useEffect(() => {
    if (!containerRef.current) return

    // Create scroll-triggered animations
    modulesRef.current.forEach((module, index) => {
      if (module) {
        gsap.fromTo(module, {
          opacity: 0,
          y: 100,
          scale: 0.8
        }, {
          opacity: 1,
          y: 0,
          scale: 1,
          duration: 1,
          ease: 'power3.out',
          scrollTrigger: {
            trigger: module,
            start: 'top 80%',
            end: 'bottom 20%',
            toggleActions: 'play none none reverse'
          }
        })

        // Add floating animation
        gsap.to(module, {
          y: 'random(-10, 10)',
          duration: 'random(3, 5)',
          repeat: -1,
          yoyo: true,
          ease: 'sine.inOut',
          delay: index * 0.2
        })
      }
    })

    // Cleanup
    return () => {
      ScrollTrigger.getAll().forEach(trigger => trigger.kill())
    }
  }, [])

  const getStatusBadge = (status: Module['status']) => {
    const badges = {
      active: { text: 'LIVE', color: 'bg-cyan-500', glow: 'shadow-neon-cyan' },
      beta: { text: 'BETA', color: 'bg-yellow-500', glow: 'shadow-yellow-500/30' },
      'coming-soon': { text: 'SOON', color: 'bg-purple-500', glow: 'shadow-purple-500/30' }
    }
    return badges[status]
  }

  return (
    <section ref={containerRef} className="py-20 px-6 relative">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-background-secondary via-background-primary to-background-secondary" />
      <div className="absolute inset-0 cyber-grid opacity-20" />
      <div className="absolute inset-0 scan-lines opacity-30" />

      <div className="relative max-w-7xl mx-auto">
        {/* Section Header */}
        <motion.div 
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <h2 className="text-5xl md:text-6xl font-cyber font-bold mb-6">
            <span className="text-text-primary">ENTERPRISE</span>
            <span className="block text-gradient">MODULES</span>
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto">
            Powerful AI modules designed for enterprise-scale operations. 
            Each module is built with scalability, security, and performance in mind.
          </p>
        </motion.div>

        {/* Modules Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
          {modules.map((module, index) => {
            const badge = getStatusBadge(module.status)
            
            return (
              <motion.div
                key={module.id}
                ref={el => modulesRef.current[index] = el!}
                className="group relative"
                initial={{ opacity: 0, y: 50 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.8, delay: index * 0.1 }}
                whileHover={{ scale: 1.02, y: -5 }}
              >
                {/* Module Card */}
                <div className="war-room-card h-full p-6 group-hover:border-cyan-500 transition-all duration-300">
                  {/* Status Badge */}
                  <div className="flex justify-between items-start mb-4">
                    <div className="text-4xl">{module.icon}</div>
                    <motion.span 
                      className={`px-3 py-1 rounded-cyber text-xs font-bold uppercase tracking-wider text-black ${badge.color} ${badge.glow}`}
                      animate={{ 
                        boxShadow: [
                          '0 0 10px rgba(0, 255, 255, 0.3)',
                          '0 0 20px rgba(0, 255, 255, 0.5)', 
                          '0 0 10px rgba(0, 255, 255, 0.3)'
                        ]
                      }}
                      transition={{ duration: 2, repeat: Infinity }}
                    >
                      {badge.text}
                    </motion.span>
                  </div>

                  {/* Module Info */}
                  <h3 className="text-xl font-cyber font-bold text-text-primary mb-3 group-hover:text-cyan-400 transition-colors">
                    {module.name}
                  </h3>
                  <p className="text-text-secondary mb-6 leading-relaxed">
                    {module.description}
                  </p>

                  {/* Features */}
                  <div className="space-y-2 mb-6">
                    {module.features.map((feature, featureIndex) => (
                      <motion.div
                        key={featureIndex}
                        className="flex items-start gap-2 text-sm"
                        initial={{ opacity: 0, x: -10 }}
                        whileInView={{ opacity: 1, x: 0 }}
                        viewport={{ once: true }}
                        transition={{ delay: index * 0.1 + featureIndex * 0.05 }}
                      >
                        <span className="text-cyan-500 mt-0.5 flex-shrink-0">▶</span>
                        <span className="text-text-secondary group-hover:text-text-primary transition-colors">
                          {feature}
                        </span>
                      </motion.div>
                    ))}
                  </div>

                  {/* Action Button */}
                  <motion.button 
                    className={`w-full py-3 rounded-cyber font-tech font-semibold uppercase tracking-wider transition-all duration-300 ${
                      module.status === 'active' 
                        ? 'bg-transparent border-2 border-cyan-500 text-cyan-500 hover:bg-cyan-500 hover:text-black'
                        : module.status === 'beta'
                        ? 'bg-transparent border-2 border-yellow-500 text-yellow-500 hover:bg-yellow-500 hover:text-black'
                        : 'bg-transparent border-2 border-purple-500 text-purple-500 hover:bg-purple-500 hover:text-black'
                    }`}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    aria-label={`${
                      module.status === 'active' ? `Learn more about ${module.name}` :
                      module.status === 'beta' ? `Join beta program for ${module.name}` :
                      `Get notified when ${module.name} is available`
                    }`}
                    title={`${
                      module.status === 'active' ? `Learn more about ${module.name}` :
                      module.status === 'beta' ? `Join beta program for ${module.name}` :
                      `Get notified when ${module.name} is available`
                    }`}
                  >
                    {module.status === 'active' && 'Learn More'}
                    {module.status === 'beta' && 'Join Beta'}
                    {module.status === 'coming-soon' && 'Get Notified'}
                  </motion.button>

                  {/* Hover Glow Effect */}
                  <div className={`absolute inset-0 bg-gradient-to-r ${module.color} opacity-0 group-hover:opacity-10 transition-opacity duration-300 rounded-war-room pointer-events-none`} />
                </div>

                {/* Floating particles for active modules */}
                {module.status === 'active' && (
                  <div className="absolute inset-0 pointer-events-none">
                    {Array.from({ length: 5 }).map((_, particleIndex) => (
                      <motion.div
                        key={particleIndex}
                        className="absolute w-1 h-1 bg-cyan-500 rounded-full opacity-60"
                        style={{
                          left: `${Math.random() * 100}%`,
                          top: `${Math.random() * 100}%`,
                        }}
                        animate={{
                          scale: [1, 1.5, 1],
                          opacity: [0.6, 1, 0.6],
                          x: [0, Math.random() * 20 - 10, 0],
                          y: [0, Math.random() * 20 - 10, 0],
                        }}
                        transition={{
                          duration: Math.random() * 3 + 2,
                          repeat: Infinity,
                          delay: particleIndex * 0.5,
                        }}
                      />
                    ))}
                  </div>
                )}
              </motion.div>
            )
          })}
        </div>

        {/* Call to Action */}
        <motion.div 
          className="text-center mt-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          <div className="war-room-card p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-cyber font-bold text-text-primary mb-4">
              Ready to Deploy Enterprise AI?
            </h3>
            <p className="text-text-secondary mb-6">
              Start with our comprehensive suite of AI modules and scale your operations 
              to enterprise levels with advanced automation and intelligence.
            </p>
            <motion.button 
              className="neon-button px-8 py-3 mr-4"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="Start Free Trial of Scorpius Enterprise"
              title="Start Free Trial of Scorpius Enterprise"
            >
              Start Free Trial
            </motion.button>
            <motion.button 
              className="bg-transparent border-2 border-surface-300 text-text-primary px-8 py-3 rounded-cyber font-tech font-semibold uppercase tracking-wider hover:border-cyan-400 hover:text-cyan-400 transition-all duration-300"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="View Scorpius Enterprise Documentation"
              title="View Scorpius Enterprise Documentation"
            >
              View Documentation
            </motion.button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default ModulesShowcase
