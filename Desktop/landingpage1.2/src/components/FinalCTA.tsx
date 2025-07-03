'use client';
import { motion } from 'framer-motion';

export default function FinalCTA() {
  return (
    <section className="relative py-32 px-8 z-20 bg-gradient-to-b from-transparent to-war-room-abyss/50">
      <div className="max-w-5xl mx-auto text-center">
        {/* Main CTA */}
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: [0.23, 1, 0.32, 1] }}
          viewport={{ once: true }}
          className="mb-16"
        >
          <h2 className="text-5xl md:text-7xl font-command font-bold cyan-glow mb-8">
            Ready to flip the kill-switch on every attacker in the Dark Forest?
          </h2>
          <p className="text-2xl text-cyan-300 mb-12 leading-relaxed">
            Book a live demo or deploy now—because "maybe secure" is just another way to say 
            <span className="text-red-400 font-bold"> next victim</span>.
          </p>
        </motion.div>

        {/* Action Buttons */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.3, ease: [0.23, 1, 0.32, 1] }}
          viewport={{ once: true }}
          className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16"
        >
          <button className="btn-glow bg-cyan-400 text-black font-bold px-12 py-6 rounded-lg text-xl hover:bg-cyan-300 transition-all duration-300">
            Book Live Demo
          </button>
          <button className="btn-glow bg-transparent border-2 border-cyan-400 text-cyan-400 font-bold px-12 py-6 rounded-lg text-xl hover:bg-cyan-400 hover:text-black transition-all duration-300">
            Deploy Now
          </button>
        </motion.div>

        {/* Emergency Contact */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.6, ease: [0.23, 1, 0.32, 1] }}
          viewport={{ once: true }}
          className="glass-morphism rounded-xl p-8 corner-accent"
        >
          <h3 className="text-2xl font-command font-bold text-white mb-4">
            🚨 Under Active Attack?
          </h3>
          <p className="text-gray-300 mb-6">
            Our emergency response team is standing by 24/7 for immediate deployment.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="tel:+1-555-DEFEND" 
              className="bg-red-500 text-white font-bold px-8 py-4 rounded-lg hover:bg-red-400 transition-all duration-300"
            >
              Emergency Hotline: +1-555-DEFEND
            </a>
            <button className="bg-yellow-500 text-black font-bold px-8 py-4 rounded-lg hover:bg-yellow-400 transition-all duration-300">
              Instant Deployment
            </button>
          </div>
        </motion.div>

        {/* Footer Note */}
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          transition={{ duration: 1, delay: 1 }}
          viewport={{ once: true }}
          className="mt-16"
        >
          <p className="text-gray-400 text-sm">
            ScorpiusCore is battle-tested by Fortune 500 companies and protects over $847B in digital assets.
            <br />
            Join the defense. The Dark Forest is watching.
          </p>
        </motion.div>
      </div>
    </section>
  );
} 