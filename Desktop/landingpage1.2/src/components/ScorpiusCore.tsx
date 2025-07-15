"use client";
import { Canvas, useFrame, extend, useThree } from "@react-three/fiber";
import { useRef, useEffect, useState } from "react";
import * as THREE from "three";
import {
  EffectComposer,
  Bloom,
  DepthOfField,
} from "@react-three/postprocessing";
import { shaderMaterial } from "@react-three/drei";
import { useScrollSync } from "./useScrollSync";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

// Camera keyframes for different scroll positions
const cameraKeyframes = [
  { scroll: 0.0, position: [0, 0, 12], fov: 45 },
  { scroll: 0.2, position: [4, 3, 10], fov: 50 },
  { scroll: 0.4, position: [-3, 2, 8], fov: 45 },
  { scroll: 0.6, position: [2, -2, 10], fov: 55 },
  { scroll: 0.8, position: [-4, 1, 7], fov: 60 },
  { scroll: 1.0, position: [0, 0, 12], fov: 40 },
];

// --- GLSL NOISE UTILS (Simplex/FBM) ---
const noiseGLSL = `
vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 mod289(vec4 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
vec4 permute(vec4 x) { return mod289(((x*34.0)+1.0)*x); }
vec4 taylorInvSqrt(vec4 r) { return 1.79284291400159 - 0.85373472095314 * r; }
float snoise(vec3 v) {
  const vec2  C = vec2(1.0/6.0, 1.0/3.0) ;
  const vec4  D = vec4(0.0, 0.5, 1.0, 2.0);
  vec3 i  = floor(v + dot(v, C.yyy) );
  vec3 x0 =   v - i + dot(i, C.xxx) ;
  vec3 g = step(x0.yzx, x0.xyz);
  vec3 l = 1.0 - g;
  vec3 i1 = min( g.xyz, l.zxy );
  vec3 i2 = max( g.xyz, l.zxy );
  vec3 x1 = x0 - i1 + 1.0 * C.xxx;
  vec3 x2 = x0 - i2 + 2.0 * C.xxx;
  vec3 x3 = x0 - 1.0 + 3.0 * C.xxx;
  i = mod289(i);
  vec4 p = permute( permute( permute(
             i.z + vec4(0.0, i1.z, i2.z, 1.0 ))
           + i.y + vec4(0.0, i1.y, i2.y, 1.0 ))
           + i.x + vec4(0.0, i1.x, i2.x, 1.0 ));
  float n_ = 1.0/7.0; 
  vec3  ns = n_ * D.wyz - D.xzx;
  vec4 j = p - 49.0 * floor(p * ns.z * ns.z);  
  vec4 x_ = floor(j * ns.z);
  vec4 y_ = floor(j - 7.0 * x_ );    
  vec4 x = x_ *ns.x + ns.y;
  vec4 y = y_ *ns.x + ns.y;
  vec4 h = 1.0 - abs(x) - abs(y);
  vec4 b0 = vec4( x.xy, y.xy );
  vec4 b1 = vec4( x.zw, y.zw );
  vec4 s0 = floor(b0)*2.0 + 1.0;
  vec4 s1 = floor(b1)*2.0 + 1.0;
  vec4 sh = -step(h, vec4(0.0));
  vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy ;
  vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww ;
  vec3 p0 = vec3(a0.xy,h.x);
  vec3 p1 = vec3(a0.zw,h.y);
  vec3 p2 = vec3(a1.xy,h.z);
  vec3 p3 = vec3(a1.zw,h.w);
  vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2,p2), dot(p3,p3)));
  p0 *= norm.x;
  p1 *= norm.y;
  p2 *= norm.z;
  p3 *= norm.w;
  vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
  m = m * m;
  return 42.0 * dot( m*m, vec4( dot(p0,x0), dot(p1,x1),
                                dot(p2,x2), dot(p3,x3) ) );
}
float fbm(vec3 x) {
  float v = 0.0;
  float a = 0.5;
  vec3 shift = vec3(100);
  for (int i = 0; i < 5; ++i) {
    v += a * snoise(x);
    x = x * 2.0 + shift;
    a *= 0.5;
  }
  return v;
}
`;

// Custom ShaderMaterial for energy layer
const EnergyMaterial = shaderMaterial(
  { uTime: 0, uPulse: 0, uMouse: [0, 0] },
  // vertex
  `
    varying vec3 vNormal;
    varying vec3 vPos;
    uniform float uTime;
    uniform float uPulse;
    uniform vec2 uMouse;
    ${noiseGLSL}
    void main() {
      vNormal = normal;
      vPos = position;
      float n = fbm(normal * 2.0 + uTime * 0.3);
      float mouseDist = length((position.xy/2.0) - uMouse);
      float displacement = n * 0.33 + uPulse * 0.4 * (1.0 - mouseDist);
      vec3 newPos = position + normal * displacement;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(newPos,1.0);
    }
  `,
  // fragment
  `
    varying vec3 vNormal;
    varying vec3 vPos;
    uniform float uTime;
    uniform float uPulse;
    uniform vec2 uMouse;
    ${noiseGLSL}

    // Color morphing function
    vec3 getColorFromTime(float time) {
      float cycle = mod(time * 0.3, 6.0); // 6 color phases

      // Define color palette
      vec3 color1 = vec3(0.0, 0.9, 1.0);    // Cyan
      vec3 color2 = vec3(1.0, 0.0, 0.8);    // Magenta
      vec3 color3 = vec3(0.0, 1.0, 0.3);    // Green
      vec3 color4 = vec3(1.0, 0.5, 0.0);    // Orange
      vec3 color5 = vec3(0.5, 0.0, 1.0);    // Purple
      vec3 color6 = vec3(1.0, 1.0, 0.0);    // Yellow

      // Smooth transitions between colors
      if (cycle < 1.0) {
        return mix(color1, color2, cycle);
      } else if (cycle < 2.0) {
        return mix(color2, color3, cycle - 1.0);
      } else if (cycle < 3.0) {
        return mix(color3, color4, cycle - 2.0);
      } else if (cycle < 4.0) {
        return mix(color4, color5, cycle - 3.0);
      } else if (cycle < 5.0) {
        return mix(color5, color6, cycle - 4.0);
      } else {
        return mix(color6, color1, cycle - 5.0);
      }
    }

    void main() {
      float fresnel = pow(1.0 - dot(normalize(vNormal), vec3(0.,0.,1.)), 2.5);
      float noiseGlow = fbm(vPos * 2.0 + uTime * 0.8) * 0.5 + 0.5;
      float mouseDist = length((vPos.xy/2.0) - uMouse);
      float mouseGlow = smoothstep(0.6, 0.0, mouseDist);
      float energy = fresnel * (0.7 + 0.5 * noiseGlow) + mouseGlow * 0.8;

      // Get morphing colors
      vec3 primaryColor = getColorFromTime(uTime);
      vec3 secondaryColor = getColorFromTime(uTime + 2.0); // Offset for variety

      // Create dynamic color mixing
      float colorMix = sin(uTime * 0.5 + noiseGlow * 3.14159) * 0.5 + 0.5;
      vec3 base = mix(primaryColor, secondaryColor, colorMix * noiseGlow);

      // Add scroll-based color influence
      vec3 scrollColor = getColorFromTime(uTime + uPulse * 5.0);
      vec3 finalColor = mix(base, scrollColor, uPulse * 0.3);

      // Apply fresnel effect with dynamic colors
      vec3 refract = mix(finalColor, finalColor * 1.3, fresnel * 0.5);

      // Add mouse interaction color boost
      if (mouseGlow > 0.1) {
        vec3 interactionColor = getColorFromTime(uTime + mouseDist * 10.0);
        refract = mix(refract, interactionColor, mouseGlow * 0.4);
      }

      gl_FragColor = vec4(refract, energy * 0.85 + 0.15 * uPulse);
    }
  `,
);
extend({ EnergyMaterial });

function EnergyLayer({
  scroll,
  mouse,
}: {
  scroll: number;
  mouse: [number, number];
}) {
  const mesh = useRef<THREE.Mesh>(null!);
  useFrame((state) => {
    const material = mesh.current.material as any;
    material.uTime = state.clock.getElapsedTime();
    material.uPulse = scroll;
    material.uMouse = mouse;
    mesh.current.rotation.y -= 0.002 - scroll * 0.01;
  });
  return (
    <mesh ref={mesh} scale={1.18}>
      <sphereGeometry args={[2.15, 128, 128]} />
      {/* @ts-ignore */}
      <energyMaterial transparent />
    </mesh>
  );
}

function WireframeSphere({ scroll }: { scroll: number }) {
  const mesh = useRef<THREE.Mesh>(null!);

  useFrame((state) => {
    mesh.current.rotation.y += 0.005 + scroll * 0.04;
    mesh.current.position.x = Math.sin(scroll * Math.PI * 2) * 0.3;
    mesh.current.position.y = Math.cos(scroll * Math.PI * 2) * 0.2;

    // Color morphing for wireframe
    const time = state.clock.getElapsedTime();
    const cycle = (time * 0.4) % (Math.PI * 2);

    // Create RGB color cycling
    const r = (Math.sin(cycle) + 1) * 0.5;
    const g = (Math.sin(cycle + (Math.PI * 2) / 3) + 1) * 0.5;
    const b = (Math.sin(cycle + (Math.PI * 4) / 3) + 1) * 0.5;

    // Apply scroll influence
    const scrollInfluence = scroll * 2;
    const finalR = Math.min(1, r + scrollInfluence * 0.3);
    const finalG = Math.min(1, g + scrollInfluence * 0.2);
    const finalB = Math.min(1, b + scrollInfluence * 0.4);

    (mesh.current.material as THREE.MeshBasicMaterial).color.setRGB(
      finalR,
      finalG,
      finalB,
    );
  });

  return (
    <mesh ref={mesh}>
      <sphereGeometry args={[2, 64, 64]} />
      <meshBasicMaterial wireframe transparent opacity={0.8} />
    </mesh>
  );
}

// Camera controller that runs inside Canvas
function CameraController({ scroll }: { scroll: number }) {
  const { camera } = useThree();

  // Multi-angle GSAP camera animation
  useEffect(() => {
    // Keyframes for camera at scroll stops
    const keyframes = [
      { scroll: 0.0, pos: [0, 0, 12], fov: 45 },
      { scroll: 0.25, pos: [2, 1, 10], fov: 50 },
      { scroll: 0.5, pos: [0, 2, 8], fov: 55 },
      { scroll: 0.75, pos: [-2, 1, 10], fov: 50 },
      { scroll: 1.0, pos: [0, 0, 12], fov: 45 },
    ];

    // Interpolate between keyframes
    let prev = keyframes[0],
      next = keyframes[keyframes.length - 1];
    for (let i = 1; i < keyframes.length; i++) {
      if (scroll <= keyframes[i].scroll) {
        prev = keyframes[i - 1];
        next = keyframes[i];
        break;
      }
    }
    const t = (scroll - prev.scroll) / (next.scroll - prev.scroll);
    const lerp = (a: number, b: number) => a + (b - a) * t;
    const pos = [
      lerp(prev.pos[0], next.pos[0]),
      lerp(prev.pos[1], next.pos[1]),
      lerp(prev.pos[2], next.pos[2]),
    ];
    const fov = lerp(prev.fov, next.fov);

    gsap.to(camera.position, {
      x: pos[0],
      y: pos[1],
      z: pos[2],
      duration: 0.8,
      ease: "power2.out",
      overwrite: "auto",
    });
    gsap.to(camera, {
      fov,
      duration: 0.8,
      ease: "power2.out",
      overwrite: "auto",
      onUpdate: () => camera.updateProjectionMatrix(),
    });
    camera.lookAt(0, 0, 0);
  }, [scroll, camera]);

  return null;
}

export default function ScorpiusCore() {
  const scroll = useScrollSync();
  const [mouse, setMouse] = useState<[number, number]>([0, 0]);

  // Mouse interaction for energy shader
  useEffect(() => {
    function onPointerMove(e: MouseEvent) {
      const x = (e.clientX / window.innerWidth) * 2 - 1;
      const y = -(e.clientY / window.innerHeight) * 2 + 1;
      setMouse([x, y]);
    }
    window.addEventListener("pointermove", onPointerMove);
    return () => window.removeEventListener("pointermove", onPointerMove);
  }, []);

  return (
    <>
      <Canvas camera={{ position: [0, 0, 12], fov: 45 }}>
        <CameraController scroll={scroll} />
        <ambientLight intensity={0.25} />
        <pointLight position={[0, 0, 8]} intensity={2} color="#00fff7" />
        <WireframeSphere scroll={scroll} />
        <EnergyLayer scroll={scroll} mouse={mouse} />
        <EffectComposer>
          <Bloom
            luminanceThreshold={0.15}
            luminanceSmoothing={0.8}
            intensity={2.2}
          />
          <DepthOfField
            focusDistance={0.015 + 0.02 * scroll}
            focalLength={0.05}
            bokehScale={3 + 2 * scroll}
            height={700}
          />
        </EffectComposer>
      </Canvas>
    </>
  );
}
