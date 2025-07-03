'use client';
import React, { useRef, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
// Simplified imports for better compatibility

// Generate realistic star field with proper distribution
function generateStarPositions(count = 800, radius = 150) {
  const positions = [];
  const colors = [];
  const sizes = [];
  
  for (let i = 0; i < count; i++) {
    // More realistic star distribution
    const r = radius * (0.3 + Math.random() * 0.7);
    const theta = Math.random() * 2 * Math.PI;
    const phi = Math.acos(2 * Math.random() - 1);
    
    positions.push(
      r * Math.sin(phi) * Math.cos(theta),
      r * Math.sin(phi) * Math.sin(theta),
      r * Math.cos(phi)
    );
    
    // Realistic star colors and sizes based on stellar classification
    const temp = Math.random();
    const brightness = 0.3 + Math.random() * 0.7;
    
    if (temp < 0.1) {
      // Blue giants (rare, bright)
      colors.push(0.6, 0.8, 1.0);
      sizes.push(1.2 + Math.random() * 0.8);
    } else if (temp < 0.3) {
      // White stars
      colors.push(1.0, 1.0, 1.0);
      sizes.push(0.8 + Math.random() * 0.6);
    } else if (temp < 0.7) {
      // Yellow stars (like our sun)
      colors.push(1.0, 1.0, 0.8);
      sizes.push(0.6 + Math.random() * 0.4);
    } else if (temp < 0.9) {
      // Orange stars
      colors.push(1.0, 0.8, 0.6);
      sizes.push(0.4 + Math.random() * 0.3);
    } else {
      // Red dwarfs (common, dim)
      colors.push(1.0, 0.6, 0.4);
      sizes.push(0.3 + Math.random() * 0.2);
    }
  }
  
  return {
    positions: new Float32Array(positions),
    colors: new Float32Array(colors),
    sizes: new Float32Array(sizes)
  };
}

// Main star field component with twinkling
export function AnimatedStars() {
  const ref = useRef<THREE.Points>(null);
  const { positions, colors, sizes } = useMemo(() => generateStarPositions(800, 150), []);
  
  useFrame((state) => {
    if (ref.current) {
      // Very subtle rotation for depth
      ref.current.rotation.y += 0.00005;
      ref.current.rotation.x += 0.00002;
      
      // Realistic twinkling effect
      const material = ref.current.material as THREE.PointsMaterial;
      const time = state.clock.getElapsedTime();
      material.opacity = 0.6 + 0.3 * Math.sin(time * 0.3);
    }
  });

  return (
    <points ref={ref} frustumCulled={false}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          array={positions}
          count={positions.length / 3}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          array={colors}
          count={colors.length / 3}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-size"
          array={sizes}
          count={sizes.length}
          itemSize={1}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.5}
        sizeAttenuation
        transparent
        opacity={0.9}
        vertexColors
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

// Animated meteor system
function randomMeteor() {
  const angle = Math.random() * 2 * Math.PI;
  const radius = 120 + Math.random() * 40;
  const speed = 0.5 + Math.random() * 1.2;
  
  return {
    x: Math.cos(angle) * radius,
    y: Math.random() * 60 - 30,
    z: Math.sin(angle) * radius,
    dx: -Math.cos(angle) * speed,
    dy: -0.2 - Math.random() * 0.3,
    dz: -Math.sin(angle) * speed,
    life: 0,
    maxLife: 100 + Math.random() * 80,
    tail: 2 + Math.random() * 3,
    brightness: 0.8 + Math.random() * 0.4,
  };
}

export function Meteors({ count = 2 }) {
  const [meteors] = useState(() => Array.from({ length: count }, randomMeteor));
  
  useFrame(() => {
    for (let meteor of meteors) {
      meteor.x += meteor.dx;
      meteor.y += meteor.dy;
      meteor.z += meteor.dz;
      meteor.life++;
      
      if (meteor.life > meteor.maxLife) {
        Object.assign(meteor, randomMeteor());
      }
    }
  });

  return (
    <>
      {meteors.map((meteor, index) => (
        <group key={index} position={[meteor.x, meteor.y, meteor.z]}>
          {/* Meteor head */}
          <mesh>
            <sphereGeometry args={[0.15, 8, 8]} />
            <meshBasicMaterial 
              color="#ffffff" 
              emissive="#ffeeaa" 
              emissiveIntensity={m.brightness}
            />
          </mesh>
          
          {/* Meteor tail */}
          <mesh
            position={[m.dx * -m.tail * 0.5, m.dy * -m.tail * 0.5, m.dz * -m.tail * 0.5]}
            lookAt={[m.x + m.dx, m.y + m.dy, m.z + m.dz]}
          >
            <cylinderGeometry args={[0.08, 0.02, m.tail, 8]} />
            <meshBasicMaterial 
              color="#ffddaa" 
              transparent 
              opacity={0.7 * m.brightness}
              emissive="#ffaa44"
              emissiveIntensity={0.3}
            />
          </mesh>
          
          {/* Tail glow */}
          <mesh
            position={[m.dx * -m.tail * 0.7, m.dy * -m.tail * 0.7, m.dz * -m.tail * 0.7]}
            lookAt={[m.x + m.dx, m.y + m.dy, m.z + m.dz]}
          >
            <cylinderGeometry args={[0.12, 0.04, m.tail * 1.2, 8]} />
            <meshBasicMaterial 
              color="#ffddaa" 
              transparent 
              opacity={0.3 * m.brightness}
              emissive="#ff8844"
              emissiveIntensity={0.2}
            />
          </mesh>
        </group>
      ))}
    </>
  );
}

// Distant galaxy layer
export function DistantGalaxies() {
  const ref = useRef<THREE.Points>(null);
  
  const galaxyPositions = useMemo(() => {
    const positions = [];
    for (let i = 0; i < 50; i++) {
      const radius = 200 + Math.random() * 100;
      const theta = Math.random() * 2 * Math.PI;
      const phi = Math.acos(2 * Math.random() - 1);
      
      positions.push(
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.sin(phi) * Math.sin(theta),
        radius * Math.cos(phi)
      );
    }
    return new Float32Array(positions);
  }, []);
  
  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.y += 0.00005;
    }
  });

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          array={galaxyPositions}
          count={galaxyPositions.length / 3}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={3}
        sizeAttenuation
        transparent
        opacity={0.4}
        color="#8844ff"
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
}

// Main space background component
export default function SpaceBackground() {
  return (
    <>
      <fog attach="fog" args={['#050510', 100, 200]} />
      <AnimatedStars />
      <DistantGalaxies />
      <Meteors />
    </>
  );
} 