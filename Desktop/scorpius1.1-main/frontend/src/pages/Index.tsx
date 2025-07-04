import React from "react";
import { Shield } from "lucide-react";
import SystemStatusWidget from "@/components/SystemStatusWidget";

const Index = () => {
  console.log("Index component rendering");

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Bright test element */}
      <div className="bg-cyan-500 text-black p-8 text-center font-bold text-2xl">
        🚀 SCORPIUS PLATFORM LOADED SUCCESSFULLY! 🚀
      </div>
      
      <div className="container mx-auto p-8">
        <div className="flex items-center gap-4 mb-6">
          <Shield className="h-12 w-12 text-cyan-400" />
          <h1 className="text-4xl font-bold text-white">
            Scorpius Enterprise Platform
          </h1>
        </div>
        
        <p className="text-xl text-gray-300 mb-8">
          Your comprehensive blockchain security and trading platform
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-slate-800 border border-cyan-500/20 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-cyan-400 mb-2">Security Scanner</h3>
            <p className="text-gray-400">Advanced threat detection</p>
          </div>
          
          <div className="bg-slate-800 border border-green-500/20 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-green-400 mb-2">Trading AI</h3>
            <p className="text-gray-400">Intelligent trading algorithms</p>
          </div>
          
          <div className="bg-slate-800 border border-purple-500/20 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-purple-400 mb-2">Bridge Network</h3>
            <p className="text-gray-400">Cross-chain monitoring</p>
          </div>
          
          <div className="bg-slate-800 border border-orange-500/20 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-orange-400 mb-2">Analytics</h3>
            <p className="text-gray-400">Data analysis & reporting</p>
          </div>
        </div>

        <div className="my-8">
          <SystemStatusWidget />
        </div>

        <div className="mt-12 text-center">
          <p className="text-green-400 text-lg">
            ✅ Frontend loaded successfully!
          </p>
          <p className="text-gray-400 mt-2">
            All library files created and components rendering properly.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Index;
