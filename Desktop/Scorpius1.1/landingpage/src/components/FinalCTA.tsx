import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { toast } from 'react-hot-toast'

const FinalCTA: React.FC = () => {
  const [email, setEmail] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleNewsletterSignup = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email) return

    setIsLoading(true)
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      toast.success('Successfully subscribed to updates!')
      setEmail('')
    } catch (error) {
      toast.error('Failed to subscribe. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const companies = [
    { name: 'TechCorp', logo: '🏢' },
    { name: 'Innovation Labs', logo: '🔬' },
    { name: 'Future Systems', logo: '🚀' },
    { name: 'AI Dynamics', logo: '🤖' },
    { name: 'CloudTech', logo: '☁️' },
    { name: 'DataFlow', logo: '📊' }
  ]

  const stats = [
    { value: '50K+', label: 'Active Agents Deployed', icon: '🤖' },
    { value: '99.9%', label: 'Uptime Guarantee', icon: '⚡' },
    { value: '10M+', label: 'Tasks Automated', icon: '⚙️' },
    { value: '24/7', label: 'Enterprise Support', icon: '🛡️' }
  ]

  return (
    <section className="py-20 px-6 relative">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-t from-background-primary via-background-secondary to-background-primary" />
      <div className="absolute inset-0 cyber-grid opacity-20" />
      
      {/* Animated scan lines */}
      <div className="absolute inset-0">
        {Array.from({ length: 5 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-full h-px bg-gradient-to-r from-transparent via-cyan-500 to-transparent opacity-30"
            style={{ top: `${20 + i * 20}%` }}
            animate={{ 
              x: ['-100%', '100%'],
              opacity: [0, 0.5, 0]
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              delay: i * 0.8,
              ease: 'linear'
            }}
          />
        ))}
      </div>

      <div className="relative max-w-7xl mx-auto">
        {/* Social Proof - Companies */}
        <motion.div 
          className="text-center mb-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
        >
          <p className="text-sm text-text-muted uppercase tracking-wider mb-8">
            Trusted by leading enterprises worldwide
          </p>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-12">
            {companies.map((company, index) => (
              <motion.div
                key={company.name}
                className="flex items-center gap-3 text-text-secondary hover:text-cyan-400 transition-colors cursor-pointer"
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ scale: 1.1 }}
              >
                <span className="text-2xl">{company.logo}</span>
                <span className="font-tech font-semibold">{company.name}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Main CTA Section */}
        <motion.div 
          className="text-center mb-16"
          initial={{ opacity: 0, y: 50 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 1 }}
        >
          <h2 className="text-6xl md:text-7xl lg:text-8xl font-cyber font-black mb-8">
            <motion.span 
              className="block text-gradient hologram-text"
              animate={{ 
                backgroundPosition: ['0% 50%', '100% 50%', '0% 50%']
              }}
              transition={{ duration: 5, repeat: Infinity }}
            >
              DEPLOY
            </motion.span>
            <motion.span 
              className="block text-text-primary"
              initial={{ opacity: 0, x: -50 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.3 }}
            >
              THE FUTURE
            </motion.span>
          </h2>
          
          <motion.p 
            className="text-xl md:text-2xl text-text-secondary max-w-4xl mx-auto mb-12 leading-relaxed"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.5 }}
          >
            Join thousands of enterprises already using Scorpius to revolutionize their operations 
            with autonomous AI agents. Start your transformation today.
          </motion.p>

          {/* CTA Buttons */}
          <motion.div 
            className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16"
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.7 }}
          >
            <motion.button 
              className="neon-button text-lg px-10 py-4 group relative overflow-hidden"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="Start Free Trial of Scorpius Enterprise"
              title="Start Free Trial of Scorpius Enterprise"
            >
              <span className="relative z-10 flex items-center gap-3">
                🚀 Start Free Trial
              </span>
              <motion.div 
                className="absolute inset-0 bg-gradient-to-r from-cyan-600 to-cyan-400 opacity-0 group-hover:opacity-20"
                whileHover={{ opacity: 0.2 }}
                transition={{ duration: 0.3 }}
              />
            </motion.button>
            
            <motion.button 
              className="bg-transparent border-2 border-surface-300 text-text-primary px-10 py-4 rounded-cyber font-tech font-semibold uppercase tracking-wider hover:border-cyan-400 hover:text-cyan-400 transition-all duration-300 group"
              whileHover={{ scale: 1.05, borderColor: "#00ffff" }}
              whileTap={{ scale: 0.95 }}
              aria-label="Contact Scorpius Enterprise Sales Team"
              title="Contact Scorpius Enterprise Sales Team"
            >
              <span className="flex items-center gap-3">
                📞 Contact Sales
              </span>
            </motion.button>
          </motion.div>
        </motion.div>

        {/* Stats Section */}
        <motion.div 
          className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-16"
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.3 }}
        >
          {stats.map((stat, index) => (
            <motion.div
              key={stat.label}
              className="text-center war-room-card p-6 group cursor-pointer"
              whileHover={{ scale: 1.05, y: -5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <div className="text-3xl mb-2">{stat.icon}</div>
              <motion.div 
                className="text-3xl md:text-4xl font-cyber font-bold text-cyan-500 mb-2"
                animate={{ 
                  textShadow: [
                    "0 0 10px #00ffff", 
                    "0 0 20px #00ffff", 
                    "0 0 10px #00ffff"
                  ]
                }}
                transition={{ duration: 2, repeat: Infinity, delay: index * 0.5 }}
              >
                {stat.value}
              </motion.div>
              <div className="text-sm text-text-secondary group-hover:text-cyan-400 transition-colors">
                {stat.label}
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Newsletter Signup */}
        <motion.div 
          className="text-center"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          <div className="war-room-card p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-cyber font-bold text-text-primary mb-4">
              Stay Updated with Scorpius
            </h3>
            <p className="text-text-secondary mb-6">
              Get the latest updates on new features, enterprise AI insights, and exclusive early access to beta modules.
            </p>
            
            <form onSubmit={handleNewsletterSignup} className="flex flex-col sm:flex-row gap-4">
              <motion.input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your enterprise email"
                className="cyber-input flex-1 bg-background-secondary border border-surface-200 rounded-cyber px-4 py-3 text-text-primary placeholder-text-muted focus:border-cyan-500 focus:outline-none transition-all duration-300"
                required
                whileFocus={{ scale: 1.02, boxShadow: "0 0 20px rgba(0, 255, 255, 0.2)" }}
                aria-label="Enter your enterprise email address"
                id="newsletter-email"
                name="email"
              />
              <motion.button
                type="submit"
                disabled={isLoading}
                className="bg-cyan-500 text-black px-8 py-3 rounded-cyber font-tech font-semibold uppercase tracking-wider hover:bg-cyan-400 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                whileHover={!isLoading ? { scale: 1.05 } : {}}
                whileTap={!isLoading ? { scale: 0.95 } : {}}
                aria-label="Subscribe to Scorpius Enterprise Newsletter"
                title="Subscribe to Scorpius Enterprise Newsletter"
              >
                {isLoading ? (
                  <motion.div 
                    className="flex items-center gap-2"
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  >
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Subscribing...
                  </motion.div>
                ) : (
                  'Subscribe'
                )}
              </motion.button>
            </form>
            
            <p className="text-xs text-text-muted mt-4">
              We respect your privacy. Unsubscribe at any time.
            </p>
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div 
          className="text-center mt-16 pt-8 border-t border-surface-200"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.7 }}
        >
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="text-text-muted text-sm">
              © 2024 Scorpius Enterprise. All rights reserved.
            </div>
            <div className="flex items-center gap-6">
              <a 
                href="#" 
                className="text-text-muted hover:text-cyan-400 transition-colors text-sm"
                aria-label="View Privacy Policy"
                title="View Privacy Policy"
              >
                Privacy Policy
              </a>
              <a 
                href="#" 
                className="text-text-muted hover:text-cyan-400 transition-colors text-sm"
                aria-label="View Terms of Service"
                title="View Terms of Service"
              >
                Terms of Service
              </a>
              <a 
                href="#" 
                className="text-text-muted hover:text-cyan-400 transition-colors text-sm"
                aria-label="Contact Scorpius Enterprise"
                title="Contact Scorpius Enterprise"
              >
                Contact
              </a>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default FinalCTA
