import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { loadStripe } from '@stripe/stripe-js'
import { notifications } from '../lib/notifications'

// Initialize Stripe
const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLISHABLE_KEY || 'pk_test_...')

interface PricingTier {
  id: string
  name: string
  price: number
  period: string
  description: string
  features: string[]
  popular?: boolean
  stripePriceId: string
  maxAgents: string
  support: string
  deployment: string
}

const pricingTiers: PricingTier[] = [
  {
    id: 'starter',
    name: 'Starter',
    price: 99,
    period: 'month',
    description: 'Perfect for small teams getting started with AI automation',
    stripePriceId: 'price_starter_monthly',
    maxAgents: '10 Agents',
    support: 'Email Support',
    deployment: 'Cloud',
    features: [
      '10 AI Agents included',
      '1,000 API calls/month',
      'Basic workflow automation',
      'Email support',
      'Community access',
      'Basic analytics',
      'Standard templates'
    ]
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 299,
    period: 'month',
    description: 'Advanced features for growing businesses',
    stripePriceId: 'price_professional_monthly',
    maxAgents: '50 Agents',
    support: 'Priority Support',
    deployment: 'Cloud + On-Premise',
    popular: true,
    features: [
      '50 AI Agents included',
      '10,000 API calls/month',
      'Advanced workflow automation',
      'Priority support',
      'Custom integrations',
      'Advanced analytics',
      'Custom templates',
      'Multi-environment deployment',
      'Role-based access control'
    ]
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 999,
    period: 'month',
    description: 'Enterprise-grade solution with unlimited scale',
    stripePriceId: 'price_enterprise_monthly',
    maxAgents: 'Unlimited',
    support: '24/7 Dedicated Support',
    deployment: 'Full On-Premise + Private Cloud',
    features: [
      'Unlimited AI Agents',
      'Unlimited API calls',
      'Enterprise workflow automation',
      '24/7 dedicated support',
      'Custom development',
      'Enterprise analytics',
      'White-label solution',
      'Multi-cloud deployment',
      'Advanced security features',
      'SLA guarantees',
      'Dedicated account manager'
    ]
  }
]

const PricingTiers: React.FC = () => {
  const [isAnnual, setIsAnnual] = useState(false)
  const [loading, setLoading] = useState<string | null>(null)

  const handleSubscribe = async (tier: PricingTier) => {
    setLoading(tier.id)
    
    const loadingToast = notifications.loading(`Setting up ${tier.name} subscription...`)
    
    try {
      const stripe = await stripePromise
      if (!stripe) {
        throw new Error('Stripe failed to load')
      }

      // Create checkout session
      const response = await fetch('/api/stripe/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          price_id: tier.stripePriceId,
          success_url: `${window.location.origin}/success?session_id={CHECKOUT_SESSION_ID}`,
          cancel_url: `${window.location.origin}/pricing`,
          metadata: {
            tier: tier.name,
            plan_id: tier.id
          }
        }),
      })

      const session = await response.json()
      
      if (!response.ok) {
        throw new Error(session.detail || 'Failed to create checkout session')
      }
      
      // Dismiss loading toast
      notifications.dismiss(loadingToast)
      
      // Show success message
      notifications.success(`Redirecting to secure checkout for ${tier.name}...`)
      
      // Redirect to Stripe Checkout
      const result = await stripe.redirectToCheckout({
        sessionId: session.sessionId,
      })

      if (result.error) {
        console.error('Stripe error:', result.error)
        notifications.error('Checkout failed. Please try again.')
      }
    } catch (error) {
      console.error('Error:', error)
      notifications.dismiss(loadingToast)
      notifications.error(error instanceof Error ? error.message : 'Something went wrong. Please try again.')
    } finally {
      setLoading(null)
    }
  }

  const getDiscountedPrice = (price: number) => {
    return isAnnual ? Math.round(price * 0.8) : price
  }

  return (
    <section className="py-20 px-6 relative">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-gradient-to-b from-background-primary via-background-secondary to-background-primary" />
      <div className="absolute inset-0 cyber-grid opacity-10" />
      
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
            <span className="text-gradient">ENTERPRISE</span>
            <span className="block text-text-primary">PRICING</span>
          </h2>
          <p className="text-xl text-text-secondary max-w-3xl mx-auto mb-8">
            Choose the perfect plan to scale your AI operations. All plans include our core enterprise features.
          </p>

          {/* Billing Toggle */}
          <motion.div 
            className="flex items-center justify-center gap-4 mb-12"
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
          >
            <span className={`text-sm ${!isAnnual ? 'text-cyan-500' : 'text-text-muted'}`}>Monthly</span>
            <button
              onClick={() => setIsAnnual(!isAnnual)}
              className={`relative w-16 h-8 rounded-full transition-colors duration-300 ${
                isAnnual ? 'bg-cyan-500' : 'bg-surface-300'
              }`}
              aria-label={`Switch to ${isAnnual ? 'monthly' : 'annual'} billing`}
              title={`Switch to ${isAnnual ? 'monthly' : 'annual'} billing`}
              role="switch"
              aria-checked={isAnnual}
            >
              <motion.div
                className="absolute top-1 left-1 w-6 h-6 bg-white rounded-full"
                animate={{ x: isAnnual ? 32 : 0 }}
                transition={{ type: "spring", stiffness: 300 }}
              />
            </button>
            <span className={`text-sm ${isAnnual ? 'text-cyan-500' : 'text-text-muted'}`}>
              Annual 
              <span className="text-cyan-400 ml-1">(20% off)</span>
            </span>
          </motion.div>
        </motion.div>

        {/* Pricing Cards */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {pricingTiers.map((tier, index) => (
            <motion.div
              key={tier.id}
              className={`relative war-room-card p-8 ${
                tier.popular 
                  ? 'border-cyan-500 shadow-neon-cyan scale-105' 
                  : 'border-surface-200'
              }`}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.8, delay: index * 0.2 }}
              whileHover={{ scale: tier.popular ? 1.05 : 1.02, y: -5 }}
            >
              {/* Popular Badge */}
              {tier.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <motion.span 
                    className="bg-cyan-500 text-black px-4 py-1 rounded-full text-sm font-bold uppercase tracking-wider"
                    animate={{ glow: [0, 20, 0] }}
                    transition={{ duration: 2, repeat: Infinity }}
                  >
                    Most Popular
                  </motion.span>
                </div>
              )}

              {/* Plan Header */}
              <div className="text-center mb-8">
                <h3 className="text-2xl font-cyber font-bold text-text-primary mb-2">
                  {tier.name}
                </h3>
                <p className="text-text-secondary text-sm mb-6">
                  {tier.description}
                </p>
                
                {/* Price */}
                <div className="mb-6">
                  <div className="flex items-baseline justify-center">
                    <span className="text-5xl font-cyber font-bold text-cyan-500">
                      ${getDiscountedPrice(tier.price)}
                    </span>
                    <span className="text-text-muted ml-2">/{tier.period}</span>
                  </div>
                  {isAnnual && tier.price !== getDiscountedPrice(tier.price) && (
                    <div className="text-sm text-text-muted line-through">
                      ${tier.price}/{tier.period}
                    </div>
                  )}
                </div>

                {/* Key Stats */}
                <div className="grid grid-cols-1 gap-2 mb-6 text-sm">
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Agents:</span>
                    <span className="text-cyan-400 font-semibold">{tier.maxAgents}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Support:</span>
                    <span className="text-cyan-400 font-semibold">{tier.support}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-text-secondary">Deployment:</span>
                    <span className="text-cyan-400 font-semibold">{tier.deployment}</span>
                  </div>
                </div>
              </div>

              {/* Features List */}
              <div className="mb-8">
                <ul className="space-y-3">
                  {tier.features.map((feature, featureIndex) => (
                    <motion.li
                      key={featureIndex}
                      className="flex items-start gap-3 text-sm"
                      initial={{ opacity: 0, x: -10 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      viewport={{ once: true }}
                      transition={{ delay: index * 0.2 + featureIndex * 0.1 }}
                    >
                      <span className="text-cyan-500 mt-1 flex-shrink-0">✓</span>
                      <span className="text-text-secondary">{feature}</span>
                    </motion.li>
                  ))}
                </ul>
              </div>

              {/* CTA Button */}
              <motion.button
                onClick={() => handleSubscribe(tier)}
                disabled={loading === tier.id}
                className={`w-full py-4 rounded-cyber font-tech font-semibold uppercase tracking-wider transition-all duration-300 ${
                  tier.popular
                    ? 'bg-cyan-500 text-black hover:bg-cyan-400 shadow-neon-cyan'
                    : 'bg-transparent border-2 border-cyan-500 text-cyan-500 hover:bg-cyan-500 hover:text-black'
                } ${loading === tier.id ? 'opacity-50 cursor-not-allowed' : ''}`}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                aria-label={`Subscribe to ${tier.name} plan`}
                title={`Subscribe to ${tier.name} plan`}
              >
                {loading === tier.id ? (
                  <motion.div 
                    className="flex items-center justify-center gap-2"
                    animate={{ opacity: [1, 0.5, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  >
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Processing...
                  </motion.div>
                ) : (
                  `Get Started with ${tier.name}`
                )}
              </motion.button>
            </motion.div>
          ))}
        </div>

        {/* Enterprise Contact */}
        <motion.div 
          className="text-center mt-16"
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8, delay: 0.5 }}
        >
          <div className="war-room-card p-8 max-w-2xl mx-auto">
            <h3 className="text-2xl font-cyber font-bold text-text-primary mb-4">
              Need a Custom Solution?
            </h3>
            <p className="text-text-secondary mb-6">
              Looking for enterprise features, custom deployment, or volume discounts? 
              Our enterprise team is here to help.
            </p>
            <motion.button 
              className="neon-button px-8 py-3"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              aria-label="Contact Enterprise Sales Team"
              title="Contact Enterprise Sales Team"
            >
              Contact Enterprise Sales
            </motion.button>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

export default PricingTiers
