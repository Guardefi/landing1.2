'use client';
import { motion } from 'framer-motion';
import { useEffect, useState } from 'react';

export default function LandingHero() {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <section className="relative min-h-screen flex items-center justify-center z-20 pointer-events-none">
      <div className="text-center max-w-6xl mx-auto px-8">
        {/* Hello Dark Forest Greeting */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.23, 1, 0.32, 1] }}
          className="mb-8"
        >
          <p className="text-lg md:text-xl text-gray-400 font-terminal">
            Hello, Dark Forest
          </p>
        </motion.div>

        {/* Main Title */}
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1.2, delay: 0.3, ease: [0.23, 1, 0.32, 1] }}
          className="mb-12 scale-in-scroll"
        >
          <h1 className="text-6xl md:text-8xl lg:text-9xl font-command font-bold cyan-glow mb-6 shake-on-scroll">
            Defense Protocol
          </h1>
          <div className="text-4xl md:text-6xl lg:text-7xl font-command text-cyan-400 mb-8">
            <span className="pulse-glow glow-pulse-scroll">Activated</span>
          </div>
          <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto leading-relaxed slide-in-left">
            Medieval high-tech alien war room meets Fortune 500 cybersecurity. 
            Your quantum defense against the Dark Forest.
          </p>
        </motion.div>

        {/* Real-time Metrics */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, delay: 0.3, ease: [0.23, 1, 0.32, 1] }}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16"
        >
          <div className="glass-morphism rounded-xl p-6 corner-accent slide-in-left">
            <div className="text-3xl md:text-4xl font-command text-cyan-400 mb-2 rotate-in-scroll">
              2,847,293
            </div>
            <div className="text-sm text-gray-400 mb-1">Threats Neutralized</div>
            <div className="text-xs text-green-400 font-bold">+12.3% ↗</div>
          </div>
          
          <div className="glass-morphism rounded-xl p-6 corner-accent scale-in-scroll">
            <div className="text-3xl md:text-4xl font-command text-cyan-400 mb-2 rotate-in-scroll">
              $847B
            </div>
            <div className="text-sm text-gray-400 mb-1">Assets Protected</div>
            <div className="text-xs text-green-400 font-bold">+98.7% ↗</div>
          </div>
          
          <div className="glass-morphism rounded-xl p-6 corner-accent slide-in-right">
            <div className="text-3xl md:text-4xl font-command text-cyan-400 mb-2 rotate-in-scroll">
              15,847
            </div>
            <div className="text-sm text-gray-400 mb-1">Zero-Days Stopped</div>
            <div className="text-xs text-green-400 font-bold">+156% ↗</div>
          </div>
        </motion.div>

        {/* Call to Action */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6, ease: [0.23, 1, 0.32, 1] }}
          className="flex flex-col sm:flex-row gap-6 justify-center items-center pointer-events-auto"
        >
          <button className="btn-glow bg-cyan-400 text-black font-bold px-8 py-4 rounded-lg text-lg hover:bg-cyan-300 transition-all duration-300 glow-pulse-scroll">
            Deploy Defense Core
          </button>
          <button className="btn-glow bg-transparent border-2 border-cyan-400 text-cyan-400 font-bold px-8 py-4 rounded-lg text-lg hover:bg-cyan-400 hover:text-black transition-all duration-300 scale-in-scroll">
            Live Demo
          </button>
        </motion.div>

        {/* Scroll Indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1.5 }}
          className="absolute bottom-8 left-1/2 transform -translate-x-1/2 scale-in-scroll"
        >
          <div className="flex flex-col items-center text-gray-400">
            <span className="text-xs font-terminal mb-2">SCROLL TO EXPLORE</span>
            <div className="w-0.5 h-12 bg-gradient-to-b from-cyan-400 to-transparent animate-pulse"></div>
          </div>
        </motion.div>
      </div>
    </section>
  );
} 