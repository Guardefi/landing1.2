"use client";

import { useRef } from "react";
import * as THREE from "three";

const baseMaterial = new THREE.MeshStandardMaterial({
  roughness: 0.1,
  metalness: 0.9,
  color: "#1f2937",
});

const glowMaterial = new THREE.MeshStandardMaterial({
  roughness: 0.1,
  metalness: 0.8,
  emissive: "#0ea5e9",
  emissiveIntensity: 0.5,
  transparent: true,
  opacity: 0.8,
});

const edgeMaterial = new THREE.MeshStandardMaterial({
  roughness: 0.1,
  metalness: 0.9,
  emissive: "#06b6d4",
  emissiveIntensity: 0.3,
  color: "#0ea5e9",
});

export type SecurityCubeProps = {
  variant?: "hive" | "bytecode" | "ai" | "bridge" | "wallet";
  scale?: number;
};

export function SecurityCube({
  variant = "hive",
  scale = 2,
  ...props
}: SecurityCubeProps) {
  const groupRef = useRef<THREE.Group>(null);

  const variantColors = {
    hive: "#f59e0b",
    bytecode: "#8b5cf6",
    ai: "#ef4444",
    bridge: "#10b981",
    wallet: "#3b82f6",
  };

  const coreMaterial = new THREE.MeshStandardMaterial({
    roughness: 0.2,
    metalness: 0.8,
    color: variantColors[variant],
    emissive: variantColors[variant],
    emissiveIntensity: 0.2,
  });

  return (
    <group ref={groupRef} {...props} dispose={null} scale={scale}>
      {/* Main cube */}
      <mesh castShadow receiveShadow material={baseMaterial}>
        <boxGeometry args={[1, 1, 1]} />
      </mesh>

      {/* Inner glowing core */}
      <mesh castShadow receiveShadow material={coreMaterial}>
        <boxGeometry args={[0.6, 0.6, 0.6]} />
      </mesh>

      {/* Outer glow effect */}
      <mesh castShadow receiveShadow material={glowMaterial}>
        <boxGeometry args={[1.1, 1.1, 1.1]} />
      </mesh>

      {/* Edge details */}
      <group>
        {/* Horizontal edges */}
        <mesh
          position={[0, 0.55, 0]}
          castShadow
          receiveShadow
          material={edgeMaterial}
        >
          <boxGeometry args={[1.05, 0.02, 0.02]} />
        </mesh>
        <mesh
          position={[0, -0.55, 0]}
          castShadow
          receiveShadow
          material={edgeMaterial}
        >
          <boxGeometry args={[1.05, 0.02, 0.02]} />
        </mesh>

        {/* Vertical edges */}
        <mesh
          position={[0.55, 0, 0]}
          castShadow
          receiveShadow
          material={edgeMaterial}
        >
          <boxGeometry args={[0.02, 1.05, 0.02]} />
        </mesh>
        <mesh
          position={[-0.55, 0, 0]}
          castShadow
          receiveShadow
          material={edgeMaterial}
        >
          <boxGeometry args={[0.02, 1.05, 0.02]} />
        </mesh>

        {/* Depth edges */}
        <mesh
          position={[0, 0, 0.55]}
          castShadow
          receiveShadow
          material={edgeMaterial}
        >
          <boxGeometry args={[0.02, 0.02, 1.05]} />
        </mesh>
        <mesh
          position={[0, 0, -0.55]}
          castShadow
          receiveShadow
          material={edgeMaterial}
        >
          <boxGeometry args={[0.02, 0.02, 1.05]} />
        </mesh>
      </group>

      {/* Corner nodes */}
      <group>
        {[
          [0.5, 0.5, 0.5],
          [-0.5, 0.5, 0.5],
          [0.5, -0.5, 0.5],
          [-0.5, -0.5, 0.5],
          [0.5, 0.5, -0.5],
          [-0.5, 0.5, -0.5],
          [0.5, -0.5, -0.5],
          [-0.5, -0.5, -0.5],
        ].map((position, index) => (
          <mesh
            key={index}
            position={position as [number, number, number]}
            castShadow
            receiveShadow
            material={coreMaterial}
          >
            <sphereGeometry args={[0.05, 8, 8]} />
          </mesh>
        ))}
      </group>

      {/* Center core indicator */}
      <mesh castShadow receiveShadow material={coreMaterial}>
        <sphereGeometry args={[0.1, 16, 16]} />
      </mesh>
    </group>
  );
}
