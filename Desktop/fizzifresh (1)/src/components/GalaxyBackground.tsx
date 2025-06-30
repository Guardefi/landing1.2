"use client";

import { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

type GalaxyBackgroundProps = {
  count?: number;
};

export function GalaxyBackground({ count = 8000 }: GalaxyBackgroundProps) {
  const starsRef = useRef<THREE.Points>(null);
  const galaxyRef = useRef<THREE.Points>(null);

  // Create star field
  const starGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);
    const sizes = new Float32Array(count);

    for (let i = 0; i < count; i++) {
      // Spread stars in a large sphere
      const radius = Math.random() * 100 + 50;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI;

      positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
      positions[i * 3 + 2] = radius * Math.cos(phi);

      // Star colors - mix of white, blue, yellow, and red
      const starType = Math.random();
      if (starType < 0.6) {
        // White/blue stars
        colors[i * 3] = 0.8 + Math.random() * 0.2;
        colors[i * 3 + 1] = 0.8 + Math.random() * 0.2;
        colors[i * 3 + 2] = 1;
      } else if (starType < 0.8) {
        // Yellow stars
        colors[i * 3] = 1;
        colors[i * 3 + 1] = 0.8 + Math.random() * 0.2;
        colors[i * 3 + 2] = 0.3 + Math.random() * 0.3;
      } else {
        // Red stars
        colors[i * 3] = 1;
        colors[i * 3 + 1] = 0.3 + Math.random() * 0.2;
        colors[i * 3 + 2] = 0.1 + Math.random() * 0.2;
      }

      sizes[i] = Math.random() * 0.5 + 0.1;
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute("size", new THREE.BufferAttribute(sizes, 1));

    return geometry;
  }, [count]);

  // Create galaxy spiral arms
  const galaxyGeometry = useMemo(() => {
    const geometry = new THREE.BufferGeometry();
    const positions = new Float32Array(15000 * 3);
    const colors = new Float32Array(15000 * 3);
    const sizes = new Float32Array(15000);

    for (let i = 0; i < 15000; i++) {
      const angle = (i / 15000) * Math.PI * 8; // 4 spiral arms
      const radius = (i / 15000) * 30 + 5;
      const spiralOffset = Math.sin(angle * 2) * 2;

      positions[i * 3] =
        Math.cos(angle) * (radius + spiralOffset) + (Math.random() - 0.5) * 5;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 2;
      positions[i * 3 + 2] =
        Math.sin(angle) * (radius + spiralOffset) + (Math.random() - 0.5) * 5;

      // Galaxy colors - purple/blue/cyan
      const intensity = 1 - (i / 15000) * 0.8;
      colors[i * 3] = 0.2 + Math.random() * 0.3; // Red
      colors[i * 3 + 1] = 0.4 + Math.random() * 0.4; // Green
      colors[i * 3 + 2] = intensity; // Blue

      sizes[i] = Math.random() * 0.3 + 0.05;
    }

    geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    geometry.setAttribute("size", new THREE.BufferAttribute(sizes, 1));

    return geometry;
  }, []);

  // Star material - tiny round dots
  const starMaterial = useMemo(() => {
    const material = new THREE.PointsMaterial({
      size: 0.5,
      sizeAttenuation: true,
      vertexColors: true,
      transparent: true,
      opacity: 0.9,
      blending: THREE.AdditiveBlending,
    });

    // Create a tiny circular texture for stars
    const canvas = document.createElement('canvas');
    canvas.width = 8;
    canvas.height = 8;
    const ctx = canvas.getContext('2d');

    if (ctx) {
      // Create radial gradient for star glow
      const gradient = ctx.createRadialGradient(4, 4, 0, 4, 4, 4);
      gradient.addColorStop(0, 'rgba(255, 255, 255, 1)');
      gradient.addColorStop(0.3, 'rgba(255, 255, 255, 0.8)');
      gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');

      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 8, 8);
    }

    const texture = new THREE.CanvasTexture(canvas);
    material.map = texture;

    return material;
  }, []);

  // Galaxy material - even tinier dots
  const galaxyMaterial = useMemo(() => {
    const material = new THREE.PointsMaterial({
      size: 0.3,
      sizeAttenuation: true,
      vertexColors: true,
      transparent: true,
      opacity: 0.7,
      blending: THREE.AdditiveBlending,
    });

    // Create tiny galaxy particle texture
    const canvas = document.createElement('canvas');
    canvas.width = 4;
    canvas.height = 4;
    const ctx = canvas.getContext('2d');

    if (ctx) {
      const gradient = ctx.createRadialGradient(2, 2, 0, 2, 2, 2);
      gradient.addColorStop(0, 'rgba(100, 150, 255, 1)');
      gradient.addColorStop(1, 'rgba(100, 150, 255, 0)');

      ctx.fillStyle = gradient;
      ctx.fillRect(0, 0, 4, 4);
    }

    const texture = new THREE.CanvasTexture(canvas);
    material.map = texture;

    return material;
  }, []);

  // Animate the galaxy and stars
  useFrame((state) => {
    if (starsRef.current) {
      starsRef.current.rotation.y += 0.0002;
      starsRef.current.rotation.x += 0.0001;
    }
    if (galaxyRef.current) {
      galaxyRef.current.rotation.y += 0.001;
      galaxyRef.current.rotation.z += 0.0005;
    }
  });

  return (
    <group>
      {/* Background stars */}
      <points ref={starsRef} geometry={starGeometry} material={starMaterial} />

      {/* Galaxy spiral */}
      <points
        ref={galaxyRef}
        geometry={galaxyGeometry}
        material={galaxyMaterial}
      />

      {/* Ambient lighting for depth */}
      <ambientLight intensity={0.1} color="#4a00ff" />
    </group>
  );
}
