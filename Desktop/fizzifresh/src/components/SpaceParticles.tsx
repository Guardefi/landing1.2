"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

type SpaceParticlesProps = {
  count?: number;
  speed?: number;
  repeat?: boolean;
};

export function SpaceParticles({
  count = 300,
  speed = 2,
  repeat = true,
}: SpaceParticlesProps) {
  const meshRef = useRef<THREE.InstancedMesh>(null);

  const particles = useMemo(() => {
    const temp = [];
    for (let i = 0; i < count; i++) {
      const t = Math.random() * 100;
      const factor = 20 + Math.random() * 100;
      const speed = 0.01 + Math.random() / 200;
      const xFactor = -50 + Math.random() * 100;
      const yFactor = -50 + Math.random() * 100;
      const zFactor = -50 + Math.random() * 100;
      temp.push({ t, factor, speed, xFactor, yFactor, zFactor, mx: 0, my: 0 });
    }
    return temp;
  }, [count]);

  const dummy = useMemo(() => new THREE.Object3D(), []);

  useFrame((state, delta) => {
    if (!meshRef.current) return;

    particles.forEach((particle, i) => {
      let { t, factor, speed, xFactor, yFactor, zFactor } = particle;

      // Update time
      t = particle.t += speed / 2;
      const a = Math.cos(t) + Math.sin(t * 1) / 10;
      const b = Math.sin(t) + Math.cos(t * 2) / 10;
      const s = Math.cos(t);

      particle.mx +=
        (state.mouse.x * state.viewport.width - particle.mx) * 0.01;
      particle.my +=
        (state.mouse.y * state.viewport.height - particle.my) * 0.01;

      // Position particles
      dummy.position.set(
        (particle.mx / 10) * a +
          xFactor +
          Math.cos((t / 10) * factor) +
          (Math.sin(t * 1) * factor) / 10,
        (particle.my / 10) * b +
          yFactor +
          Math.sin((t / 10) * factor) +
          (Math.cos(t * 2) * factor) / 10,
        (particle.my / 10) * b +
          zFactor +
          Math.cos((t / 10) * factor) +
          (Math.sin(t * 3) * factor) / 10,
      );

      // Scale based on distance
      const s_factor = Math.max(0.1, Math.min(1, s));
      dummy.scale.set(s_factor, s_factor, s_factor);

      // Rotation
      dummy.rotation.set(s * factor, s * factor, s * factor);

      dummy.updateMatrix();
      meshRef.current.setMatrixAt(i, dummy.matrix);
    });

    meshRef.current.instanceMatrix.needsUpdate = true;
  });

  const starMaterial = useMemo(
    () =>
      new THREE.MeshStandardMaterial({
        color: "#ffffff",
        emissive: "#4f46e5",
        emissiveIntensity: 0.5,
        transparent: true,
        opacity: 0.8,
      }),
    [],
  );

  return (
    <instancedMesh
      ref={meshRef}
      args={[undefined, undefined, count]}
      material={starMaterial}
    >
      <sphereGeometry args={[0.05, 8, 8]} />
    </instancedMesh>
  );
}
