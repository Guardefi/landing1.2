import { useLayoutEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export default function UIOverlay() {
  const heroRef = useRef<HTMLDivElement>(null);
  const featuresRef = useRef<HTMLDivElement>(null);
  const hiveAlertRef = useRef<HTMLDivElement>(null);
  const bytecodeRef = useRef<HTMLDivElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    const timeline = gsap.timeline({});

    // Sync UI animations with camera movements
    
    // Hero section fade in
    timeline.set([heroRef.current], { opacity: 0, y: 50 });
    timeline.to(heroRef.current, { 
      opacity: 1, 
      y: 0, 
      duration: 1,
      ease: "power2.out"
    }, 0.5);
    timeline.to(heroRef.current, { 
      opacity: 0, 
      duration: 0.8,
      ease: "power2.in"
    }, 2.5);

    // Features introduction
    timeline.set(featuresRef.current, { opacity: 0, y: 50 });
    timeline.to(featuresRef.current, { 
      opacity: 1, 
      y: 0, 
      duration: 1,
      ease: "power2.out"
    }, 3.2);
    timeline.to(featuresRef.current, { 
      opacity: 0, 
      duration: 0.8,
      ease: "power2.in"
    }, 4.5);

    // Hive Alert module
    timeline.set(hiveAlertRef.current, { opacity: 0, y: 50 });
    timeline.to(hiveAlertRef.current, { 
      opacity: 1, 
      y: 0, 
      duration: 1,
      ease: "power2.out"
    }, 5.5);
    timeline.to(hiveAlertRef.current, { 
      opacity: 0, 
      duration: 0.8,
      ease: "power2.in"
    }, 6.8);

    // Bytecode Engine module
    timeline.set(bytecodeRef.current, { opacity: 0, y: 50 });
    timeline.to(bytecodeRef.current, { 
      opacity: 1, 
      y: 0, 
      duration: 1,
      ease: "power2.out"
    }, 7.5);
    timeline.to(bytecodeRef.current, { 
      opacity: 0, 
      duration: 0.8,
      ease: "power2.in"
    }, 8.8);

    // Final CTA
    timeline.set(ctaRef.current, { opacity: 0, y: 50 });
    timeline.to(ctaRef.current, { 
      opacity: 1, 
      y: 0, 
      duration: 1.5,
      ease: "power2.out"
    }, 9.5);

    ScrollTrigger.create({
      trigger: '#scroll-container',
      start: 'top top',
      end: 'bottom bottom',
      scrub: 1,
      animation: timeline,
      invalidateOnRefresh: true,
    });

    return () => {
      ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    };
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none z-10">
      {/* Hero Section */}
      <div 
        ref={heroRef}
        className="absolute inset-0 flex items-center justify-center"
      >
        <div className="text-center max-w-4xl px-6">
          <h1 className="text-6xl md:text-8xl font-bold text-scorpius-blue text-glow mb-6">
            SCORPIUS
          </h1>
          <p className="text-xl md:text-2xl text-white/80 font-light tracking-wide">
            Quantum-Enhanced Security Intelligence
          </p>
          <p className="text-lg text-white/60 mt-4 max-w-2xl mx-auto leading-relaxed">
            Step into the Dark Forest. Where every transaction is monitored, 
            every threat is neutralized, and every asset is protected.
          </p>
        </div>
      </div>

      {/* Features Introduction */}
      <div 
        ref={featuresRef}
        className="absolute inset-0 flex items-center justify-center"
      >
        <div className="text-center max-w-3xl px-6">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            The Sentinel Awakens
          </h2>
          <p className="text-lg text-white/70 leading-relaxed">
            Powered by advanced AI and quantum computing, Scorpius monitors 
            the blockchain's dark corners where threats emerge from silence.
          </p>
        </div>
      </div>

      {/* Hive Alert Module */}
      <div 
        ref={hiveAlertRef}
        className="absolute left-8 top-1/2 transform -translate-y-1/2 max-w-md"
      >
        <div className="bg-black/50 backdrop-blur-sm border border-scorpius-blue/30 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <div className="w-3 h-3 bg-scorpius-red rounded-full animate-pulse mr-3"></div>
            <h3 className="text-xl font-bold text-scorpius-blue">HIVE ALERT</h3>
          </div>
          <p className="text-white/80 text-sm leading-relaxed">
            Real-time threat detection across all major blockchains. 
            Our AI swarm identifies malicious patterns before they execute.
          </p>
          <div className="mt-4 text-xs text-scorpius-blue font-mono">
            &gt; 99.7% threat detection accuracy
          </div>
        </div>
      </div>

      {/* Bytecode Engine Module */}
      <div 
        ref={bytecodeRef}
        className="absolute right-8 top-1/2 transform -translate-y-1/2 max-w-md"
      >
        <div className="bg-black/50 backdrop-blur-sm border border-scorpius-blue/30 rounded-lg p-6">
          <div className="flex items-center mb-4">
            <div className="w-3 h-3 bg-scorpius-blue rounded-full animate-pulse mr-3"></div>
            <h3 className="text-xl font-bold text-scorpius-blue">BYTECODE ENGINE</h3>
          </div>
          <p className="text-white/80 text-sm leading-relaxed">
            Deep contract analysis and vulnerability assessment. 
            Every line of code is dissected for hidden exploits.
          </p>
          <div className="mt-4 text-xs text-scorpius-blue font-mono">
            &gt; Quantum-accelerated analysis
          </div>
        </div>
      </div>

      {/* Final CTA Section */}
      <div 
        ref={ctaRef}
        className="absolute inset-0 flex items-center justify-center"
      >
        <div className="text-center max-w-4xl px-6">
          <h2 className="text-5xl md:text-6xl font-bold text-white mb-8">
            Enter the Dark Forest
          </h2>
          <p className="text-xl text-white/70 mb-12 max-w-2xl mx-auto">
            Join the next generation of blockchain security. 
            Where AI meets quantum computing to protect what matters most.
          </p>
          <div className="space-x-6">
            <button className="bg-scorpius-blue text-black px-8 py-4 rounded-lg font-bold text-lg hover:bg-white transition-colors pointer-events-auto">
              Start Your Mission
            </button>
            <button className="border border-scorpius-blue text-scorpius-blue px-8 py-4 rounded-lg font-bold text-lg hover:bg-scorpius-blue hover:text-black transition-colors pointer-events-auto">
              Learn More
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 