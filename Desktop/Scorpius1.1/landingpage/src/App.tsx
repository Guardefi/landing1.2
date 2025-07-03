import React, { useEffect } from 'react'
import { Toaster } from 'react-hot-toast'
import './styles/globals.css'
import Scene from './components/Scene'
import LandingHero from './components/LandingHero'
import ModulesShowcase from './components/ModulesShowcase'
import PricingTiers from './components/PricingTiers'
import FinalCTA from './components/FinalCTA'

// Scroll-triggered UI Overlay for the 3D experience
const ScrollUIOverlay = () => {
  useEffect(() => {
    const handleScroll = () => {
      const scrollTop = window.scrollY
      const windowHeight = window.innerHeight
      const documentHeight = document.documentElement.scrollHeight

      // Simple scroll progress calculation (0-100%)
      const scrollProgress = Math.max(0, Math.min(100, 
        (scrollTop / (documentHeight - windowHeight)) * 100
      ))

      // Debug: Show scroll progress in console (remove this later)
      console.log('Scroll Progress:', scrollProgress.toFixed(1) + '%')

      // Animate each scroll section based on progress with simpler logic
      const sections = document.querySelectorAll('.scroll-section')
      sections.forEach((section) => {
        const element = section as HTMLElement
        const scrollRange = element.dataset.scroll
        if (!scrollRange) return

        const [start, end] = scrollRange.split('-').map(Number)
        
        if (scrollProgress >= start && scrollProgress <= end) {
          // Section is active - show it
          element.style.opacity = '1'
          element.style.transform = 'translateY(0px)'
          element.style.visibility = 'visible'
        } else if (scrollProgress < start) {
          // Before section - hide below
          element.style.opacity = '0'
          element.style.transform = 'translateY(30px)'
          element.style.visibility = 'hidden'
        } else {
          // After section - hide above
          element.style.opacity = '0'
          element.style.transform = 'translateY(-30px)'
          element.style.visibility = 'hidden'
        }
      })

      // Update scroll progress indicator
      const progressBar = document.getElementById('scroll-progress-bar')
      if (progressBar) {
        progressBar.style.height = `${scrollProgress}%`
      }

      // Update debug info
      const debugInfo = document.getElementById('debug-scroll')
      if (debugInfo) {
        debugInfo.textContent = `Scroll: ${scrollProgress.toFixed(1)}%`
      }
    }

    window.addEventListener('scroll', handleScroll)
    handleScroll() // Initial call

    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="fixed inset-0 pointer-events-none z-20">
      {/* Hero Section - Stay visible throughout entire scroll */}
      <div className="absolute inset-0 flex items-center justify-center scroll-section transition-all duration-1000" data-scroll="0-100">
        <div className="text-center max-w-6xl px-6 pointer-events-auto">
          {/* Pre-title with enhanced glow */}
          <div className="mb-6">
            <span className="inline-block px-6 py-3 bg-gray-900/80 border border-cyan-500 rounded text-cyan-500 text-sm font-mono uppercase tracking-wider backdrop-blur-sm hover:shadow-neon-cyan transition-all duration-300">
              ⚡ Enterprise AI Command Center ⚡
            </span>
          </div>

          {/* Enhanced Main title with holographic effect */}
          <h1 className="text-7xl md:text-8xl lg:text-9xl font-black mb-8" style={{fontFamily: 'Orbitron, monospace'}}>
            <span 
              className="block text-gradient hologram-text"
              style={{
                background: 'linear-gradient(45deg, #00ffff, #22d3ee, #0891b2)',
                backgroundSize: '200% 200%',
                WebkitBackgroundClip: 'text',
                backgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                animation: 'hologram-shift 3s ease-in-out infinite',
                textShadow: '0 0 30px rgba(0, 255, 255, 0.5), 0 0 60px rgba(0, 255, 255, 0.3)'
              }}
            >
              SCORPIUS
            </span>
            <span className="block text-white text-5xl md:text-6xl lg:text-7xl mt-4">
              ENTERPRISE
            </span>
          </h1>

          {/* Enhanced Subtitle */}
          <p className="text-xl md:text-2xl text-gray-300 mb-8 max-w-4xl mx-auto leading-relaxed">
            The most advanced AI agent orchestration platform for enterprise operations. 
            Deploy autonomous agents, manage complex workflows, and scale intelligence across your organization.
          </p>

          {/* Dark Forest Description */}
          <p className="text-lg text-cyan-400 mb-12 max-w-3xl mx-auto leading-relaxed" style={{textShadow: '0 0 20px rgba(0, 255, 255, 0.4)'}}>
            Step into the Dark Forest. Where every transaction is monitored, 
            every threat is neutralized, and every asset is protected by quantum-enhanced security intelligence.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
            <button 
              className="neon-button text-lg px-8 py-4 group relative overflow-hidden"
              aria-label="Deploy Scorpius Enterprise Platform"
              title="Deploy Scorpius Enterprise Platform"
            >
              <span className="relative z-10 flex items-center gap-2">
                🚀 Deploy Now
              </span>
            </button>
            
            <button 
              className="bg-transparent border-2 border-cyan-500 text-cyan-400 px-8 py-4 rounded-lg font-semibold uppercase tracking-wider hover:bg-cyan-500 hover:text-black transition-all duration-300"
              aria-label="Watch Scorpius Enterprise Demo Video"
              title="Watch Scorpius Enterprise Demo Video"
            >
              <span className="flex items-center gap-2">
                📺 Watch Demo
              </span>
            </button>
          </div>

          {/* Status indicators */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="war-room-card text-center p-6">
              <div className="text-3xl font-bold text-cyan-500 mb-2 optimized-pulse" style={{textShadow: '0 0 20px rgba(0, 255, 255, 0.6)'}}>
                99.9%
              </div>
              <div className="text-gray-400">Uptime</div>
            </div>
            <div className="war-room-card text-center p-6">
              <div className="text-3xl font-bold text-cyan-500 mb-2 optimized-pulse" style={{textShadow: '0 0 20px rgba(0, 255, 255, 0.6)'}}>
                1M+
              </div>
              <div className="text-gray-400">Threats Blocked</div>
            </div>
            <div className="war-room-card text-center p-6">
              <div className="text-3xl font-bold text-cyan-500 mb-2 optimized-pulse" style={{textShadow: '0 0 20px rgba(0, 255, 255, 0.6)'}}>
                24/7
              </div>
              <div className="text-gray-400">AI Monitoring</div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Introduction */}
      <div className="absolute inset-0 flex items-center justify-center scroll-section opacity-0 transition-all duration-1000" data-scroll="40-60">
        <div className="text-center max-w-3xl px-6">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6" style={{textShadow: '0 0 20px rgba(255, 255, 255, 0.3)'}}>
            The Sentinel Awakens
          </h2>
          <p className="text-lg text-white/70 leading-relaxed">
            Powered by advanced AI and quantum computing, Scorpius monitors 
            the blockchain's dark corners where threats emerge from silence.
          </p>
        </div>
      </div>

      {/* Hive Alert Module */}
      <div className="absolute left-8 top-1/2 transform -translate-y-1/2 max-w-md scroll-section opacity-0 transition-all duration-1000" data-scroll="60-80">
        <div className="war-room-card pointer-events-auto">
          <div className="flex items-center mb-4">
            <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse mr-3"></div>
            <h3 className="text-xl font-bold text-cyan-400">HIVE ALERT</h3>
          </div>
          <p className="text-white/80 text-sm leading-relaxed mb-4">
            Real-time threat detection across all major blockchains. 
            Our AI swarm identifies malicious patterns before they execute.
          </p>
          <div className="text-xs text-cyan-400 font-mono">
            &gt; 99.7% threat detection accuracy
          </div>
          <div className="text-xs text-cyan-400 font-mono">
            &gt; 24/7 autonomous monitoring
          </div>
        </div>
      </div>

      {/* Bytecode Engine Module */}
      <div className="absolute right-8 top-1/2 transform -translate-y-1/2 max-w-md scroll-section opacity-0 transition-all duration-1000" data-scroll="80-95">
        <div className="war-room-card pointer-events-auto">
          <div className="flex items-center mb-4">
            <div className="w-3 h-3 bg-cyan-500 rounded-full animate-pulse mr-3"></div>
            <h3 className="text-xl font-bold text-cyan-400">BYTECODE ENGINE</h3>
          </div>
          <p className="text-white/80 text-sm leading-relaxed mb-4">
            Deep contract analysis and vulnerability assessment. 
            Every line of code is dissected for hidden exploits.
          </p>
          <div className="text-xs text-cyan-400 font-mono">
            &gt; Quantum-accelerated analysis
          </div>
          <div className="text-xs text-cyan-400 font-mono">
            &gt; Smart contract forensics
          </div>
        </div>
      </div>

      {/* Final CTA Section */}
      <div className="absolute inset-0 flex items-center justify-center scroll-section opacity-0 transition-all duration-1000" data-scroll="95-100">
        <div className="text-center max-w-4xl px-6">
          <h2 className="text-5xl md:text-6xl font-bold text-white mb-8" style={{textShadow: '0 0 20px rgba(255, 255, 255, 0.3)'}}>
            Enter the Dark Forest
          </h2>
          <p className="text-xl text-white/70 mb-12 max-w-2xl mx-auto">
            Join the next generation of blockchain security. 
            Where AI meets quantum computing to protect what matters most.
          </p>
          <div className="space-x-6">
            <button 
              className="neon-button text-lg px-8 py-4 pointer-events-auto"
              aria-label="Start Your Security Mission with Scorpius"
              title="Start Your Security Mission with Scorpius"
            >
              Start Your Mission
            </button>
            <button 
              className="border border-cyan-500 text-cyan-500 px-8 py-4 rounded-lg font-bold text-lg hover:bg-cyan-500 hover:text-black transition-colors pointer-events-auto"
              aria-label="Learn More About Scorpius Enterprise"
              title="Learn More About Scorpius Enterprise"
            >
              Learn More
            </button>
          </div>
        </div>
      </div>

      {/* Scroll Progress Indicator */}
      <div className="fixed bottom-20 right-8 z-50">
        <div className="text-cyan-400 text-sm font-mono">
          <div className="mb-2">SCROLL PROGRESS</div>
          <div className="w-1 h-20 bg-gray-800 rounded">
            <div 
              id="scroll-progress-bar"
              className="w-full bg-cyan-500 rounded transition-all duration-300"
              style={{ height: '0%' }}
            />
          </div>
        </div>
      </div>

      {/* Debug Info - Remove this later */}
      <div className="fixed top-4 left-4 z-50 text-cyan-400 text-xs font-mono bg-black/80 p-2 rounded">
        <div id="debug-scroll">Scroll: 0%</div>
      </div>
    </div>
  )
}

// Simple Enterprise Modules component
const EnterpriseModules = () => (
  <div className="container mx-auto px-6">
    <div className="text-center mb-16">
      <h2 className="text-4xl font-bold text-white mb-6">Enterprise Features</h2>
      <p className="text-xl text-gray-300 max-w-3xl mx-auto">
        Advanced security modules designed for enterprise-scale blockchain operations
      </p>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      <div className="war-room-card">
        <h3 className="text-xl font-semibold text-cyan-400 mb-4">Advanced Analytics</h3>
        <p className="text-gray-300">Deep insights into blockchain transactions and security patterns</p>
      </div>
      <div className="war-room-card">
        <h3 className="text-xl font-semibold text-cyan-400 mb-4">Custom Integrations</h3>
        <p className="text-gray-300">Seamless integration with existing enterprise infrastructure</p>
      </div>
      <div className="war-room-card">
        <h3 className="text-xl font-semibold text-cyan-400 mb-4">24/7 Support</h3>
        <p className="text-gray-300">Dedicated support team for mission-critical operations</p>
      </div>
    </div>
  </div>
)

function App() {
  return (
    <div className="relative bg-black">
      {/* 3D Background Scene with Interactive Camera */}
      <div className="fixed inset-0 z-0">
        <Scene />
      </div>

      {/* Scroll-triggered UI Overlays for 3D Experience */}
      <ScrollUIOverlay />

      {/* Floating Navigation */}
      <nav className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
        <div className="floating-panel px-6 py-3">
          <div className="flex space-x-6">
            <a 
              href="#3d-experience" 
              className="text-gray-300 hover:text-cyan-400 transition-colors duration-200"
              aria-label="Navigate to 3D Experience Section"
              title="3D Experience Section"
            >
              Experience
            </a>
            <a 
              href="#modules" 
              className="text-gray-300 hover:text-cyan-400 transition-colors duration-200"
              aria-label="Navigate to Security Modules Section"
              title="Security Modules Section"
            >
              Modules
            </a>
            <a 
              href="#enterprise" 
              className="text-gray-300 hover:text-cyan-400 transition-colors duration-200"
              aria-label="Navigate to Enterprise Features Section"
              title="Enterprise Features Section"
            >
              Enterprise
            </a>
            <a 
              href="#pricing" 
              className="text-gray-300 hover:text-cyan-400 transition-colors duration-200"
              aria-label="Navigate to Pricing Section"
              title="Pricing Section"
            >
              Pricing
            </a>
            <button 
              className="neon-button text-sm px-4 py-2"
              aria-label="Get Started with Scorpius Enterprise"
              title="Get Started with Scorpius Enterprise"
            >
              Get Started
            </button>
          </div>
        </div>
      </nav>

      {/* Corner Status Indicators */}
      <div className="fixed top-4 right-4 z-50">
        <div className="flex space-x-2">
          <div className="w-3 h-3 rounded-full bg-cyan-500 animate-pulse" />
          <div className="w-3 h-3 rounded-full bg-cyan-400 opacity-60" />
          <div className="w-3 h-3 rounded-full bg-cyan-300 opacity-40" />
        </div>
      </div>

      {/* Bottom Status Bar */}
      <div className="fixed bottom-0 left-0 right-0 z-40">
        <div className="bg-black/80 backdrop-blur-sm border-t border-cyan-500/20 px-6 py-2">
          <div className="flex justify-between items-center text-sm text-gray-400">
            <div className="flex space-x-4">
              <span>Status: <span className="text-cyan-400">OPERATIONAL</span></span>
              <span>Load: <span className="text-cyan-400">78%</span></span>
              <span>Agents: <span className="text-cyan-400">12 ACTIVE</span></span>
            </div>
            <div className="flex space-x-4">
              <span>© 2024 Scorpius Enterprise</span>
              <span className="text-cyan-400">v2.1.0</span>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive 3D Scroll Experience */}
      <div id="scroll-container" className="relative" style={{ height: '600vh' }}>
        <section id="3d-experience" className="h-full">
          {/* This creates the scroll space for the 3D camera movements */}
        </section>
      </div>

      {/* Traditional Sections Below the 3D Experience */}
      <div className="relative z-10">
        {/* Modules Showcase Section */}
        <section id="modules" className="min-h-screen py-20 relative bg-gray-900/30 backdrop-blur-sm">
          <ModulesShowcase />
        </section>

        {/* Enterprise Features Section */}
        <section id="enterprise" className="min-h-screen py-20 relative">
          <EnterpriseModules />
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="min-h-screen py-20 relative bg-gray-900/30 backdrop-blur-sm">
          <PricingTiers />
        </section>

        {/* Final CTA Section */}
        <section id="cta" className="min-h-screen py-20 relative">
          <FinalCTA />
        </section>
      </div>

      {/* Subtle overlay effects */}
      <div className="fixed inset-0 z-5 pointer-events-none">
        {/* Cyber grid background */}
        <div className="cyber-grid opacity-5 w-full h-full" />
        
        {/* Scan line effect */}
        <div className="scan-line-overlay" />
      </div>

      {/* Toast Notifications */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1a1a2e',
            color: '#00ffff',
            border: '1px solid #00ffff',
            borderRadius: '8px',
            fontFamily: 'monospace',
          },
        }}
      />
    </div>
  )
}

export default App
