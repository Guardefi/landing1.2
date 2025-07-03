'use client';
import dynamic from 'next/dynamic';
import LandingHero from '@/components/LandingHero';
import ModulesShowcase from '@/components/ModulesShowcase';
import EnterpriseModules from '@/components/EnterpriseModules';
import PricingTiers from '@/components/PricingTiers';
import SocialProof from '@/components/SocialProof';
import FinalCTA from '@/components/FinalCTA';

const ScorpiusCore = dynamic(() => import('@/components/ScorpiusCore'), { 
  ssr: false,
  loading: () => (
    <div className="fixed inset-0 flex items-center justify-center bg-war-room-void">
      <div className="text-cyan-400 font-terminal text-lg">
        Initializing War Room<span className="loading-dots"></span>
      </div>
    </div>
  )
});

export default function Home() {
  return (
    <div className="relative">
      {/* 3D Sphere Experience Section */}
      <div className="relative h-[500vh]">
        {/* 3D + Space Background, sticky for sphere section */}
        <div className="fixed inset-0 z-0 pointer-events-none">
          <ScorpiusCore />
        </div>
        
        {/* Progress indicator */}
        <div className="fixed top-0 left-0 w-full h-1 z-50 bg-war-room-steel">
          <div className="h-full bg-cyan-400 transition-all duration-150 progress-bar" />
        </div>
        
        {/* Invisible scroll sections for sphere interaction */}
        <section className="scroll-section opacity-0" id="greeting" data-scroll-animate="fade-in">
          <div className="h-screen"></div>
        </section>
        <section className="scroll-section opacity-0" id="hero" data-scroll-animate="fade-in">
          <div className="h-screen"></div>
        </section>
        <section className="scroll-section opacity-0" id="modules" data-scroll-animate="fade-in">
          <div className="h-screen"></div>
        </section>
        <section className="scroll-section opacity-0" id="enterprise" data-scroll-animate="fade-in">
          <div className="h-screen"></div>
        </section>
        <section className="scroll-section opacity-0" id="cta" data-scroll-animate="fade-in">
          <div className="h-screen"></div>
        </section>
      </div>
      
      {/* Actual Page Content Sections */}
      <div className="relative z-10 bg-war-room-void">
        <section className="min-h-screen" data-scroll-animate="fade-in">
          <LandingHero />
        </section>
        <section className="min-h-screen" data-scroll-animate="fade-in">
          <ModulesShowcase />
        </section>
        <section className="min-h-screen" data-scroll-animate="fade-in">
          <EnterpriseModules />
        </section>
        <section className="min-h-screen" data-scroll-animate="fade-in">
          <PricingTiers />
        </section>
        <section className="min-h-screen" data-scroll-animate="fade-in">
          <SocialProof />
        </section>
        <section className="min-h-screen" data-scroll-animate="fade-in">
          <FinalCTA />
        </section>
      </div>
    </div>
  );
} 