export default function Loading() {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-war-room-void z-50">
      <div className="text-center">
        <div className="relative">
          <div className="w-16 h-16 border-4 border-war-room-steel rounded-full animate-spin border-t-cyan-400 mx-auto mb-4"></div>
          <div className="absolute inset-0 w-16 h-16 border-2 border-cyan-400 rounded-full animate-ping opacity-20 mx-auto"></div>
        </div>
        <h2 className="text-cyan-400 font-command text-xl mb-2">Initializing War Room</h2>
        <p className="text-gray-400 font-terminal text-sm">
          Loading quantum defense protocols<span className="loading-dots"></span>
        </p>
      </div>
    </div>
  );
} 