import Scene from './components/Scene';
import UIOverlay from './components/UIOverlay';

function App() {
  return (
    <div className="relative">
      {/* WebGL Scene - Fixed background */}
      <Scene />
      
      {/* UI Overlay - Text content that appears over the 3D scene */}
      <UIOverlay />
      
      {/* Scroll Container - Creates the scrollable area that drives animations */}
      <div id="scroll-container" className="relative" style={{ height: '600vh' }}>
        {/* This div is intentionally mostly empty - its height creates scroll space */}
        <div className="h-screen" />
        <div className="h-screen" />
        <div className="h-screen" />
        <div className="h-screen" />
        <div className="h-screen" />
        <div className="h-screen" />
      </div>
    </div>
  );
}

export default App;
