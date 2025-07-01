import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import { Mesh } from 'three';

export function ScorpiusCore() {
  const meshRef = useRef<Mesh>(null);

  // Animate the core with subtle rotation and pulsing
  useFrame((state) => {
    if (meshRef.current) {
      // Slow rotation for the living energy effect
      meshRef.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.3) * 0.1;
      meshRef.current.rotation.y += 0.005;
      meshRef.current.rotation.z = Math.cos(state.clock.elapsedTime * 0.2) * 0.05;
      
      // Subtle scale pulsing like a heartbeat
      const pulse = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.05;
      meshRef.current.scale.setScalar(pulse);
    }
  });

  return (
    <group>
      {/* Main core geometry */}
      <mesh ref={meshRef} position={[0, 0, 0]}>
        <icosahedronGeometry args={[1.5, 1]} />
        <meshPhongMaterial 
          color="#00ffff"
          emissive="#004444"
          wireframe={true}
          transparent={true}
          opacity={0.8}
        />
      </mesh>
      
      {/* Inner energy core */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[0.8, 32, 32]} />
        <meshBasicMaterial 
          color="#00ffff"
          transparent={true}
          opacity={0.3}
        />
      </mesh>
      
      {/* Outer energy field */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[2.2, 32, 32]} />
        <meshBasicMaterial 
          color="#00ccff"
          transparent={true}
          opacity={0.1}
          wireframe={true}
        />
      </mesh>
    </group>
  );
} 