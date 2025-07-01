import { Canvas } from '@react-three/fiber';
import { Stars } from '@react-three/drei';
import { ScorpiusCore } from './ScorpiusCore';
import { CameraRig } from './CameraRig';

export default function Scene() {
  return (
    <Canvas 
      style={{ 
        position: 'fixed', 
        top: 0, 
        left: 0, 
        zIndex: -1,
        width: '100vw',
        height: '100vh'
      }}
      camera={{ position: [0, 0, 10], fov: 75 }}
    >
      {/* Dark space background */}
      <color attach="background" args={['#050505']} />
      
      {/* Ambient lighting for subtle illumination */}
      <ambientLight intensity={0.2} />
      
      {/* Point light for the core's energy glow */}
      <pointLight position={[0, 0, 0]} intensity={1} color="#00ffff" />
      
      {/* The Dark Forest - particle field representing transactions */}
      <Stars 
        radius={100} 
        depth={50} 
        count={5000} 
        factor={4} 
        saturation={0} 
        fade 
        speed={0.5}
      />
      
      {/* The Scorpius Core - our central sentinel */}
      <ScorpiusCore />
      
      {/* Camera animation controller */}
      <CameraRig />
    </Canvas>
  );
} 