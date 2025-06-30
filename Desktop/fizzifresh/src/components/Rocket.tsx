"use client";

import { useRef } from "react";
import * as THREE from "three";

const metalMaterial = new THREE.MeshStandardMaterial({
  roughness: 0.2,
  metalness: 0.9,
  color: "#e5e7eb",
});

const engineMaterial = new THREE.MeshStandardMaterial({
  roughness: 0.1,
  metalness: 0.8,
  color: "#ef4444",
  emissive: "#dc2626",
  emissiveIntensity: 0.3,
});

const windowMaterial = new THREE.MeshStandardMaterial({
  roughness: 0.1,
  metalness: 0.1,
  color: "#3b82f6",
  transparent: true,
  opacity: 0.8,
});

export type RocketProps = {
  variant?: "explorer" | "fighter" | "cargo" | "scout" | "interceptor";
  scale?: number;
};

export function Rocket({
  variant = "explorer",
  scale = 2,
  ...props
}: RocketProps) {
  const groupRef = useRef<THREE.Group>(null);

  const variantColors = {
    explorer: "#6366f1",
    fighter: "#ef4444",
    cargo: "#f59e0b",
    scout: "#10b981",
    interceptor: "#8b5cf6",
  };

  const bodyMaterial = new THREE.MeshStandardMaterial({
    roughness: 0.3,
    metalness: 0.7,
    color: variantColors[variant],
  });

  return (
    <group ref={groupRef} {...props} dispose={null} scale={scale}>
      {/* Main body */}
      <mesh castShadow receiveShadow material={bodyMaterial}>
        <cylinderGeometry args={[0.3, 0.4, 2, 16]} />
      </mesh>

      {/* Nose cone */}
      <mesh
        position={[0, 1.2, 0]}
        castShadow
        receiveShadow
        material={metalMaterial}
      >
        <coneGeometry args={[0.3, 0.8, 16]} />
      </mesh>

      {/* Engine nozzle */}
      <mesh
        position={[0, -1.3, 0]}
        castShadow
        receiveShadow
        material={engineMaterial}
      >
        <cylinderGeometry args={[0.2, 0.35, 0.6, 16]} />
      </mesh>

      {/* Windows */}
      <mesh
        position={[0, 0.3, 0.31]}
        castShadow
        receiveShadow
        material={windowMaterial}
      >
        <sphereGeometry args={[0.15, 16, 16]} />
      </mesh>

      {/* Wings/fins */}
      <group position={[0, -0.5, 0]}>
        <mesh
          position={[0.5, 0, 0]}
          rotation={[0, 0, Math.PI / 6]}
          castShadow
          receiveShadow
          material={metalMaterial}
        >
          <boxGeometry args={[0.6, 0.1, 0.05]} />
        </mesh>
        <mesh
          position={[-0.5, 0, 0]}
          rotation={[0, 0, -Math.PI / 6]}
          castShadow
          receiveShadow
          material={metalMaterial}
        >
          <boxGeometry args={[0.6, 0.1, 0.05]} />
        </mesh>
        <mesh
          position={[0, 0, 0.5]}
          rotation={[Math.PI / 6, 0, 0]}
          castShadow
          receiveShadow
          material={metalMaterial}
        >
          <boxGeometry args={[0.05, 0.1, 0.6]} />
        </mesh>
        <mesh
          position={[0, 0, -0.5]}
          rotation={[-Math.PI / 6, 0, 0]}
          castShadow
          receiveShadow
          material={metalMaterial}
        >
          <boxGeometry args={[0.05, 0.1, 0.6]} />
        </mesh>
      </group>

      {/* Detail panels */}
      <mesh
        position={[0.31, 0, 0]}
        castShadow
        receiveShadow
        material={metalMaterial}
      >
        <boxGeometry args={[0.02, 1.8, 0.1]} />
      </mesh>
      <mesh
        position={[-0.31, 0, 0]}
        castShadow
        receiveShadow
        material={metalMaterial}
      >
        <boxGeometry args={[0.02, 1.8, 0.1]} />
      </mesh>
    </group>
  );
}
