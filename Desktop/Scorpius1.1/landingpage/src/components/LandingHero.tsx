import React, { useEffect, useRef } from 'react'
import { motion } from 'framer-motion'
import { gsap } from 'gsap'

const LandingHero: React.FC = () => {
  const heroRef = useRef<HTMLDivElement>(null)
  const particlesRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Advanced GSAP animations for hero elements
    const tl = gsap.timeline()
    
    // Animate hero content on load
    tl.from('.hero-pretitle', { 
      opacity: 0, 
      y: 30, 
      duration: 0.8, 
      ease: 'power3.out' 
    })
    .from('.hero-title-main', { 
      opacity: 0, 
      y: 50, 
      duration: 1, 
      ease: 'power3.out' 
    }, '-=0.6')
    .from('.hero-title-sub', { 
      opacity: 0, 
      y: 30, 
      duration: 0.8, 
      ease: 'power3.out' 
    }, '-=0.4')
    .from('.hero-subtitle', { 
      opacity: 0, 
      y: 20, 
      duration: 0.8, 
      ease: 'power3.out' 
    }, '-=0.3')
    .from('.hero-buttons', { 
      opacity: 0, 
      y: 20, 
      duration: 0.6, 
      ease: 'power3.out' 
    }, '-=0.2')
    .from('.hero-stats', { 
      opacity: 0, 
      y: 20, 
      duration: 0.6, 
      ease: 'power3.out' 
    }, '-=0.1')

    // Floating particle animation
    if (particlesRef.current) {
      const particles = particlesRef.current.children
      Array.from(particles).forEach((particle, i) => {
        gsap.to(particle, {
          y: 'random(-50, 50)',
          x: 'random(-30, 30)',
          duration: 'random(3, 6)',
          repeat: -1,
          yoyo: true,
          ease: 'sine.inOut',
          delay: i * 0.1
        })
      })
    }
  }, [])

  return (
    <div ref={heroRef} className="relative h-screen flex items-center justify-center overflow-hidden">
      {/* Enhanced Background effects */}
      <div className="absolute inset-0">
        {/* Animated cyber grid with glow */}
        <div className="cyber-grid opacity-30 animate-pulse-neon" />
        
        {/* Enhanced floating particles */}
        <div ref={particlesRef} className="absolute inset-0">
          {Array.from({ length: 80 }).map((_, i) => (
            <motion.div
              key={i}
              className="absolute rounded-full opacity-70"
              style={{
                width: Math.random() * 4 + 1 + 'px',
                height: Math.random() * 4 + 1 + 'px',
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
                background: i % 3 === 0 ? '#00ffff' : i % 3 === 1 ? '#22d3ee' : '#0891b2',
                boxShadow: `0 0 ${Math.random() * 10 + 5}px currentColor`,
              }}
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.7, 1, 0.7],
              }}
              transition={{
                duration: Math.random() * 3 + 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>

        {/* Radial gradient overlay */}
        <div className="absolute inset-0 bg-gradient-radial from-transparent via-background-primary/50 to-background-primary" />
      </div>

      {/* Enhanced Main hero content */}
      <div className="relative z-10 text-center max-w-6xl mx-auto px-6">
        {/* Pre-title with enhanced glow */}
        <div className="mb-6 hero-pretitle">
          <motion.span 
            className="inline-block px-6 py-3 bg-surface-100/80 border border-cyan-500 rounded-cyber text-cyan-500 text-sm font-tech uppercase tracking-wider backdrop-blur-sm glow-on-hover"
            whileHover={{ scale: 1.05, boxShadow: "0 0 30px rgba(0, 255, 255, 0.5)" }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            ⚡ Enterprise AI Command Center ⚡
          </motion.span>
        </div>

        {/* Enhanced Main title with split animation */}
        <h1 className="text-7xl md:text-8xl lg:text-9xl font-cyber font-black mb-8">
          <motion.span 
            className="block text-gradient hologram-text hero-title-main"
            initial={{ opacity: 0, rotateX: -90 }}
            animate={{ opacity: 1, rotateX: 0 }}
            transition={{ duration: 1.2, delay: 0.3 }}
          >
            SCORPIUS
          </motion.span>
          <motion.span 
            className="block text-text-primary text-5xl md:text-6xl lg:text-7xl mt-4 hero-title-sub"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            ENTERPRISE
          </motion.span>
        </h1>

        {/* Enhanced Subtitle with typewriter effect */}
        <motion.p 
          className="text-xl md:text-2xl text-text-secondary mb-12 max-w-4xl mx-auto leading-relaxed hero-subtitle"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.9 }}
        >
          The most advanced AI agent orchestration platform for enterprise operations. 
          Deploy autonomous agents, manage complex workflows, and scale intelligence across your organization.
        </motion.p>

        {/* Enhanced CTA Buttons with micro-interactions */}
        <motion.div 
          className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16 hero-buttons"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.1 }}
        >
          <motion.button 
            className="neon-button text-lg px-8 py-4 group relative overflow-hidden"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            transition={{ type: "spring", stiffness: 400, damping: 10 }}
          >
            <span className="relative z-10 flex items-center gap-2">
              🚀 Deploy Now
            </span>
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-cyan-400 opacity-0 group-hover:opacity-20 transition-opacity duration-300" />
          </motion.button>
          
          <motion.button 
            className="bg-transparent border-2 border-surface-300 text-text-primary px-8 py-4 rounded-cyber font-tech font-semibold uppercase tracking-wider hover:border-cyan-400 hover:text-cyan-400 transition-all duration-300 group"
            whileHover={{ scale: 1.05, borderColor: "#00ffff" }}
            whileTap={{ scale: 0.95 }}
          >
            <span className="flex items-center gap-2">
              📺 Watch Demo
            </span>
          </motion.button>
        </motion.div>

        {/* Enhanced Status indicators with hover effects */}
        <motion.div 
          className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto hero-stats"
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 1.3 }}
        >
          <motion.div 
            className="war-room-card text-center p-6 group cursor-pointer"
            whileHover={{ scale: 1.05, y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <motion.div 
              className="text-3xl font-cyber font-bold text-cyan-500 mb-2"
              animate={{ textShadow: ["0 0 10px #00ffff", "0 0 20px #00ffff", "0 0 10px #00ffff"] }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              99.9%
            </motion.div>
            <div className="text-text-secondary group-hover:text-cyan-400 transition-colors">Uptime</div>
            <div className="mt-2 h-1 bg-surface-200 rounded-full overflow-hidden">
              <motion.div 
                className="h-full bg-gradient-to-r from-cyan-500 to-cyan-300"
                initial={{ width: 0 }}
                animate={{ width: "99.9%" }}
                transition={{ duration: 2, delay: 1.5 }}
              />
            </div>
          </motion.div>
          
          <motion.div 
            className="war-room-card text-center p-6 group cursor-pointer"
            whileHover={{ scale: 1.05, y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <motion.div 
              className="text-3xl font-cyber font-bold text-cyan-400 mb-2"
              animate={{ scale: [1, 1.05, 1] }}
              transition={{ duration: 3, repeat: Infinity }}
            >
              50K+
            </motion.div>
            <div className="text-text-secondary group-hover:text-cyan-400 transition-colors">Active Agents</div>
            <div className="mt-2 flex justify-center space-x-1">
              {Array.from({ length: 5 }).map((_, i) => (
                <motion.div
                  key={i}
                  className="w-2 h-2 bg-cyan-400 rounded-full"
                  animate={{ opacity: [0.3, 1, 0.3] }}
                  transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.2 }}
                />
              ))}
            </div>
          </motion.div>
          
          <motion.div 
            className="war-room-card text-center p-6 group cursor-pointer"
            whileHover={{ scale: 1.05, y: -5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <motion.div 
              className="text-3xl font-cyber font-bold text-cyan-300 mb-2"
              animate={{ color: ["#67e8f9", "#22d3ee", "#67e8f9"] }}
              transition={{ duration: 4, repeat: Infinity }}
            >
              24/7
            </motion.div>
            <div className="text-text-secondary group-hover:text-cyan-400 transition-colors">Operations</div>
            <div className="mt-2 flex justify-center">
              <motion.div
                className="w-3 h-3 bg-cyan-500 rounded-full"
                animate={{ scale: [1, 1.3, 1], opacity: [1, 0.5, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </div>
          </motion.div>
        </motion.div>
      </div>

      {/* Enhanced Animated arrows pointing down */}
      <motion.div 
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        animate={{ y: [0, 10, 0] }}
        transition={{ duration: 2, repeat: Infinity }}
      >
        <div className="flex flex-col items-center space-y-2">
          <motion.div 
            className="w-6 h-6 border-r-2 border-b-2 border-cyan-500 transform rotate-45"
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: 0 }}
          />
          <motion.div 
            className="w-4 h-4 border-r-2 border-b-2 border-cyan-500 transform rotate-45"
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
          />
          <motion.div 
            className="w-2 h-2 border-r-2 border-b-2 border-cyan-500 transform rotate-45"
            animate={{ opacity: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity, delay: 0.4 }}
          />
        </div>
      </motion.div>

      {/* Enhanced Terminal window preview with animations */}
      <motion.div 
        className="absolute bottom-20 right-8 w-96 terminal-window hidden lg:block shadow-neon-cyan"
        initial={{ opacity: 0, x: 50 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 1, delay: 1.8 }}
        whileHover={{ scale: 1.02, boxShadow: "0 0 40px rgba(0, 255, 255, 0.3)" }}
      >
        <div className="terminal-header">
          <div className="flex space-x-2">
            <motion.div 
              className="terminal-dot red"
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <motion.div 
              className="terminal-dot yellow"
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.3 }}
            />
            <motion.div 
              className="terminal-dot green"
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 0.6 }}
            />
          </div>
          <div className="text-text-muted text-xs ml-4 font-mono">scorpius-enterprise-v2.1</div>
        </div>
        <div className="p-4 space-y-2 font-mono">
          <motion.div 
            className="text-cyan-500"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 2 }}
          >
            $ scorpius agent deploy --model gpt-4o --env production
          </motion.div>
          <motion.div 
            className="text-text-secondary"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2.3 }}
          >
            → Initializing enterprise deployment...
          </motion.div>
          <motion.div 
            className="text-cyan-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2.6 }}
          >
            → Agent deployed successfully ✓
          </motion.div>
          <motion.div 
            className="text-cyan-500"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 2.9 }}
          >
            → Status: OPERATIONAL 🚀
          </motion.div>
          <motion.div 
            className="text-green-400"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 3.2 }}
          >
            → Performance: 99.9% efficiency
          </motion.div>
          <div className="flex items-center">
            <span className="text-text-secondary">$</span>
            <motion.span 
              className="ml-2 w-2 h-4 bg-cyan-500"
              animate={{ opacity: [1, 0, 1] }}
              transition={{ duration: 1, repeat: Infinity }}
            />
          </div>
        </div>
      </motion.div>

      {/* Additional floating UI elements */}
      <motion.div 
        className="absolute top-20 left-8 hidden xl:block"
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: 2 }}
      >
        <div className="bg-surface-100/80 backdrop-blur-sm border border-cyan-500/30 rounded-cyber p-4 w-64">
          <div className="text-sm text-cyan-400 font-tech uppercase tracking-wider mb-2">System Status</div>
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-text-secondary">CPU Usage</span>
              <span className="text-cyan-500">23%</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-text-secondary">Memory</span>
              <span className="text-cyan-500">1.2GB / 8GB</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-text-secondary">Active Agents</span>
              <span className="text-cyan-500">247</span>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  )
}

export default LandingHero
