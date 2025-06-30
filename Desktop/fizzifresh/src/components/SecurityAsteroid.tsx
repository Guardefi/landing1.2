"use client";

import { useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

// Realistic asteroid material
const asteroidMaterial = new THREE.MeshStandardMaterial({
  roughness: 0.9,
  metalness: 0.1,
  color: "#2c1810",
  map: null, // We'll add procedural roughness
});

// Fire glow material
const fireMaterial = new THREE.MeshStandardMaterial({
  transparent: true,
  opacity: 0.8,
  emissive: "#ff4500",
  emissiveIntensity: 1.5,
  color: "#ff6b35",
});

// Inner fire core
const coreFireMaterial = new THREE.MeshStandardMaterial({
  transparent: true,
  opacity: 0.6,
  emissive: "#ffff00",
  emissiveIntensity: 2,
  color: "#ff8c00",
});

export type SecurityAsteroidProps = {
  variant?: "hive" | "bytecode" | "ai" | "bridge" | "wallet";
  scale?: number;
};

export function SecurityAsteroid({
  variant = "hive",
  scale = 0.15,
  ...props
}: SecurityAsteroidProps) {
  const groupRef = useRef<THREE.Group>(null);
  const fireRef = useRef<THREE.Group>(null);
  const flameRef1 = useRef<THREE.Mesh>(null);
  const flameRef2 = useRef<THREE.Mesh>(null);
  const flameRef3 = useRef<THREE.Mesh>(null);

  const variantFireColors = {
    hive: { emissive: "#ff8c00", color: "#ff6b35" },
    bytecode: { emissive: "#9f7aea", color: "#8b5cf6" },
    ai: { emissive: "#f56565", color: "#ef4444" },
    bridge: { emissive: "#48bb78", color: "#10b981" },
    wallet: { emissive: "#4299e1", color: "#3b82f6" },
  };

  const fireColors = variantFireColors[variant];

  // Animated fire effect
  useFrame((state) => {
    if (fireRef.current) {
      fireRef.current.rotation.y += 0.02;
      fireRef.current.scale.setScalar(1 + Math.sin(state.clock.elapsedTime * 3) * 0.1);
    }

    if (flameRef1.current) {
      flameRef1.current.scale.y = 1 + Math.sin(state.clock.elapsedTime * 4) * 0.3;
      flameRef1.current.material.emissiveIntensity = 1.5 + Math.sin(state.clock.elapsedTime * 5) * 0.5;
    }

    if (flameRef2.current) {
      flameRef2.current.scale.y = 1 + Math.sin(state.clock.elapsedTime * 3.5) * 0.2;
      flameRef2.current.material.emissiveIntensity = 1.2 + Math.sin(state.clock.elapsedTime * 4.5) * 0.4;
    }

    if (flameRef3.current) {
      flameRef3.current.scale.y = 1 + Math.sin(state.clock.elapsedTime * 4.5) * 0.25;
      flameRef3.current.material.emissiveIntensity = 1.8 + Math.sin(state.clock.elapsedTime * 6) * 0.6;
    }
  });

  // Custom fire material for this variant
  const customFireMaterial = new THREE.MeshStandardMaterial({
    transparent: true,
    opacity: 0.8,
    emissive: fireColors.emissive,
    emissiveIntensity: 1.5,
    color: fireColors.color,
  });

  const customCoreMaterial = new THREE.MeshStandardMaterial({
    transparent: true,
    opacity: 0.6,
    emissive: fireColors.emissive,
    emissiveIntensity: 2,
    color: fireColors.color,
  });

  return (
    <group ref={groupRef} {...props} dispose={null} scale={scale}>
      {/* Main realistic asteroid shape - irregular */}
      <mesh castShadow receiveShadow material={asteroidMaterial}>
        <icosahedronGeometry args={[1, 1]} />
      </mesh>

      {/* Secondary rough chunks */}
      <mesh
        position={[0.3, 0.2, 0.4]}
        rotation={[0.3, 0.7, 0.2]}
        castShadow
        receiveShadow
        material={asteroidMaterial}
      >
        <dodecahedronGeometry args={[0.3, 0]} />
      </mesh>

      <mesh
        position={[-0.4, -0.3, 0.2]}
        rotation={[0.8, 0.2, 0.5]}
        castShadow
        receiveShadow
        material={asteroidMaterial}
      >
        <octahedronGeometry args={[0.25]} />
      </mesh>

      <mesh
        position={[0.1, -0.4, -0.3]}
        rotation={[0.5, 1.2, 0.8]}
        castShadow
        receiveShadow
        material={asteroidMaterial}
      >
        <tetrahedronGeometry args={[0.2]} />
      </mesh>

      {/* Fire effects group */}
      <group ref={fireRef}>
        {/* Inner fire core */}
        <mesh material={customCoreMaterial}>
          <sphereGeometry args={[0.4, 8, 8]} />
        </mesh>

        {/* Flame jets */}
        <mesh
          ref={flameRef1}
          position={[0.6, 0.3, 0.2]}
          rotation={[0.2, 0, 0.3]}
          material={customFireMaterial}
        >
          <coneGeometry args={[0.15, 0.8, 6]} />
        </mesh>

        <mesh
          ref={flameRef2}
          position={[-0.5, 0.4, -0.1]}
          rotation={[0.1, 0.8, -0.2]}
          material={customFireMaterial}
        >
          <coneGeometry args={[0.12, 0.6, 6]} />
        </mesh>

        <mesh
          ref={flameRef3}
          position={[0.2, -0.6, 0.4]}
          rotation={[0.7, 0.3, 0.1]}
          material={customFireMaterial}
        >
          <coneGeometry args={[0.1, 0.5, 6]} />
        </mesh>

        {/* Outer fire glow */}
        <mesh material={customFireMaterial}>
          <sphereGeometry args={[0.7, 8, 8]} />
        </mesh>

        {/* Hot spots */}
        <mesh
          position={[0.3, 0.2, 0.5]}
          material={customCoreMaterial}
        >
          <sphereGeometry args={[0.08, 6, 6]} />
        </mesh>

        <mesh
          position={[-0.4, -0.2, 0.3]}
          material={customCoreMaterial}
        >
          <sphereGeometry args={[0.06, 6, 6]} />
        </mesh>

        <mesh
          position={[0.1, 0.5, -0.4]}
          material={customCoreMaterial}
        >
          <sphereGeometry args={[0.07, 6, 6]} />
        </mesh>
      </group>

      {/* Point light for fire illumination */}
      <pointLight
        intensity={2}
        color={fireColors.color}
        distance={3}
        decay={2}
      />
    </group>
  );
}
