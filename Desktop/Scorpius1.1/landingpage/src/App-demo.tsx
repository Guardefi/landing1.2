import * as React from 'react'
import { Toaster } from 'react-hot-toast'
import './styles/globals.css'
import LandingHeroDemo from './components/LandingHero-demo'
import PricingTiers from './components/PricingTiers'
import PaymentSuccess from './components/PaymentSuccess'

function App() {
  const [showPaymentSuccess, setShowPaymentSuccess] = React.useState(false)

  if (showPaymentSuccess) {
    return <PaymentSuccess sessionId="demo_session_123" />
  }

  return (
    <div className="relative min-h-screen bg-background-primary overflow-hidden">
      {/* Matrix Rain Effect - CSS Only */}
      <div className="fixed inset-0 z-10 pointer-events-none opacity-30">
        <div className="matrix-rain">
          {Array.from({ length: 20 }).map((_, i) => (
            <div
              key={i}
              className="matrix-column"
              style={{
                left: `${i * 5}%`,
                animationDelay: `${Math.random() * 3}s`,
                animationDuration: `${15 + Math.random() * 10}s`,
              }}
            >
              {Array.from({ length: 20 }).map((_, j) => (
                <div key={j} className="block">
                  {String.fromCharCode(0x30A0 + Math.random() * 96)}
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Scan Line Effect */}
      <div className="fixed inset-0 z-20 pointer-events-none">
        <div className="scan-line-overlay" />
      </div>

      {/* Main Content */}
      <div className="relative z-30">
        {/* Landing Hero Section */}
        <section id="hero" className="relative min-h-screen">
          <LandingHeroDemo />
        </section>

        {/* Pricing Section */}
        <section id="pricing" className="relative min-h-screen bg-surface-100/50">
          <div className="container mx-auto px-6 py-20">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-cyber font-bold text-text-primary mb-4">
                Choose Your Arsenal
              </h2>
              <p className="text-xl text-text-secondary max-w-2xl mx-auto">
                Select the perfect plan for your enterprise warfare needs
              </p>
            </div>
            <PricingTiers onPaymentSuccess={() => setShowPaymentSuccess(true)} />
          </div>
        </section>

        {/* Demo Controls */}
        <div className="fixed bottom-4 right-4 z-50">
          <button
            onClick={() => setShowPaymentSuccess(!showPaymentSuccess)}
            className="neon-button px-4 py-2 text-sm"
          >
            {showPaymentSuccess ? 'Back to Landing' : 'Show Payment Success'}
          </button>
        </div>
      </div>

      {/* Toast Notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#1a1a1a',
            color: '#ffffff',
            border: '1px solid #00f5ff',
          },
        }}
      />
    </div>
  )
}

export default App
