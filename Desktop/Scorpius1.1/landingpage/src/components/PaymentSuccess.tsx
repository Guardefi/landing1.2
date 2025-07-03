import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { FiCheck, FiMail, FiUser, FiCreditCard } from 'react-icons/fi'

interface PaymentSuccessProps {
  sessionId?: string
}

const PaymentSuccess: React.FC<PaymentSuccessProps> = ({ sessionId }) => {
  const [sessionData, setSessionData] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSessionData = async () => {
      if (!sessionId) return
      
      try {
        // In a real app, you'd fetch session details from your backend
        // const response = await fetch(`/api/stripe/session/${sessionId}`)
        // const data = await response.json()
        
        // Mock data for demo
        setSessionData({
          amount: 29900,
          currency: 'usd',
          customerEmail: 'user@example.com',
          planName: 'Professional',
          subscriptionId: 'sub_1234567890'
        })
      } catch (error) {
        console.error('Error fetching session data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchSessionData()
  }, [sessionId])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background-primary">
        <motion.div
          className="w-8 h-8 border-2 border-cyan-500 border-t-transparent rounded-full"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
        />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background-primary flex items-center justify-center px-6">
      <div className="absolute inset-0 cyber-grid opacity-10" />
      
      <motion.div
        className="relative max-w-2xl mx-auto text-center"
        initial={{ opacity: 0, y: 50 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
      >
        {/* Success Icon */}
        <motion.div
          className="w-24 h-24 mx-auto mb-8 relative"
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
        >
          <div className="absolute inset-0 bg-cyan-500/20 rounded-full animate-ping" />
          <div className="relative w-full h-full bg-cyan-500 rounded-full flex items-center justify-center">
            <FiCheck className="w-12 h-12 text-white" />
          </div>
        </motion.div>

        {/* Success Message */}
        <motion.h1
          className="text-4xl md:text-5xl font-cyber font-bold text-text-primary mb-4"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          Payment Successful!
        </motion.h1>

        <motion.p
          className="text-xl text-text-secondary mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
        >
          Welcome to Scorpius Enterprise. Your subscription is now active.
        </motion.p>

        {/* Payment Details */}
        {sessionData && (
          <motion.div
            className="war-room-card p-6 mb-8 text-left max-w-md mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.9 }}
          >
            <h3 className="text-lg font-tech text-cyan-400 mb-4 flex items-center gap-2">
              <FiCreditCard className="w-5 h-5" />
              Payment Details
            </h3>
            
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-text-secondary">Plan:</span>
                <span className="text-text-primary font-semibold">{sessionData.planName}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Amount:</span>
                <span className="text-text-primary font-semibold">
                  ${(sessionData.amount / 100).toFixed(2)} {sessionData.currency.toUpperCase()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Email:</span>
                <span className="text-text-primary">{sessionData.customerEmail}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Subscription ID:</span>
                <span className="text-cyan-400 font-mono text-xs">{sessionData.subscriptionId}</span>
              </div>
            </div>
          </motion.div>
        )}

        {/* Next Steps */}
        <motion.div
          className="grid md:grid-cols-2 gap-4 mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.1 }}
        >
          <div className="war-room-card p-4 text-center">
            <FiMail className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
            <h4 className="font-tech text-text-primary mb-1">Check Your Email</h4>
            <p className="text-sm text-text-secondary">
              Setup instructions sent to your email
            </p>
          </div>
          
          <div className="war-room-card p-4 text-center">
            <FiUser className="w-8 h-8 text-cyan-400 mx-auto mb-2" />
            <h4 className="font-tech text-text-primary mb-1">Account Setup</h4>
            <p className="text-sm text-text-secondary">
              Complete your profile setup
            </p>
          </div>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          className="flex flex-col sm:flex-row gap-4 justify-center"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3 }}
        >
          <motion.button
            className="neon-button px-8 py-3"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
          >
            Go to Dashboard
          </motion.button>
          
          <motion.button
            className="bg-transparent border-2 border-surface-300 text-text-primary px-8 py-3 rounded-cyber font-tech font-semibold uppercase tracking-wider hover:border-cyan-400 hover:text-cyan-400 transition-all duration-300"
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => window.location.href = '/'}
          >
            Back to Home
          </motion.button>
        </motion.div>

        {/* Floating Elements */}
        <div className="absolute -top-10 -left-10 w-20 h-20 bg-cyan-500/10 rounded-full blur-xl" />
        <div className="absolute -bottom-10 -right-10 w-32 h-32 bg-cyan-500/5 rounded-full blur-xl" />
      </motion.div>
    </div>
  )
}

export default PaymentSuccess
