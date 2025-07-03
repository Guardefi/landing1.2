'use client';
import { Canvas, useFrame, extend, useThree } from '@react-three/fiber';
import { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { EffectComposer, Bloom, DepthOfField } from '@react-three/postprocessing';
import { shaderMaterial } from '@react-three/drei';
import { useScrollSync } from './useScrollSync';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { motion } from 'framer-motion';

// Register ScrollTrigger plugin
gsap.registerPlugin(ScrollTrigger);

// Camera keyframes for different scroll positions
const cameraKeyframes = [
  { scroll: 0.0, position: [0, 0, 7], fov: 50 },
  { scroll: 0.2, position: [3, 2, 5], fov: 60 },
  { scroll: 0.4, position: [-2, 1, 4], fov: 55 },
  { scroll: 0.6, position: [1, -1, 6], fov: 65 },
  { scroll: 0.8, position: [-3, 0, 3], fov: 70 },
  { scroll: 1.0, position: [0, 0, 8], fov: 45 },
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
  { uTime: 0, uPulse: 0, uMouse: [0,0] },
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
    void main() {
      float fresnel = pow(1.0 - dot(normalize(vNormal), vec3(0.,0.,1.)), 2.5);
      float noiseGlow = fbm(vPos * 2.0 + uTime * 0.8) * 0.5 + 0.5;
      float mouseDist = length((vPos.xy/2.0) - uMouse);
      float mouseGlow = smoothstep(0.6, 0.0, mouseDist);
      float energy = fresnel * (0.7 + 0.5 * noiseGlow) + mouseGlow * 0.8;
      // Simulate refractive color shift
      vec3 base = mix(vec3(0.0, 0.9, 1.0), vec3(0.1, 1.0, 1.0), noiseGlow);
      vec3 refract = mix(base, vec3(0.0, 1.0, 0.7), fresnel * 0.5);
      gl_FragColor = vec4(refract, energy * 0.85 + 0.15 * uPulse);
    }
  `
);
extend({ EnergyMaterial });

function EnergyLayer({ scroll, mouse }: { scroll: number; mouse: [number, number] }) {
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
  });
  return (
    <mesh ref={mesh}>
      <sphereGeometry args={[2, 64, 64]} />
      <meshBasicMaterial wireframe color="#00fff7" transparent opacity={0.8} />
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
      { scroll: 0.0, pos: [0, 0, 7], fov: 50 },
      { scroll: 0.25, pos: [1, 0.5, 6], fov: 55 },
      { scroll: 0.5, pos: [0, 1.2, 4.5], fov: 60 },
      { scroll: 0.75, pos: [-1, 0.5, 6], fov: 55 },
      { scroll: 1.0, pos: [0, 0, 7], fov: 50 },
    ];
    
    // Interpolate between keyframes
    let prev = keyframes[0], next = keyframes[keyframes.length - 1];
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
      x: pos[0], y: pos[1], z: pos[2], duration: 0.8, ease: 'power2.out', overwrite: 'auto'
    });
    gsap.to(camera, { 
      fov, 
      duration: 0.8, 
      ease: 'power2.out', 
      overwrite: 'auto', 
      onUpdate: () => camera.updateProjectionMatrix() 
    });
    camera.lookAt(0, 0, 0);
  }, [scroll, camera]);

  return null;
}

// Dynamic overlay sections that move with camera
function DynamicOverlays({ scroll }: { scroll: number }) {
  const [cameraAngle, setCameraAngle] = useState(0);
  
  useEffect(() => {
    setCameraAngle(Math.atan2(scroll * 2 - 1, 1) * 180 / Math.PI);
  }, [scroll]);

  const overlays = [
    {
      id: 'greeting',
      active: scroll < 0.2,
      content: 'Hello, Dark Forest',
      position: { top: '20%', left: '10%' },
      parallax: { x: scroll * 50, y: -scroll * 30 }
    },
    {
      id: 'defense',
      active: scroll >= 0.2 && scroll < 0.4,
      content: 'Defense Protocol Activated',
      position: { top: '60%', right: '15%' },
      parallax: { x: -scroll * 40, y: scroll * 25 }
    },
    {
      id: 'modules',
      active: scroll >= 0.4 && scroll < 0.6,
      content: 'Security Modules Online',
      position: { top: '40%', left: '60%' },
      parallax: { x: scroll * 30, y: -scroll * 40 }
    },
    {
      id: 'enterprise',
      active: scroll >= 0.6 && scroll < 0.8,
      content: 'Enterprise Command Center',
      position: { bottom: '30%', left: '20%' },
      parallax: { x: -scroll * 35, y: scroll * 20 }
    },
    {
      id: 'final',
      active: scroll >= 0.8,
      content: 'War Room Initialized',
      position: { top: '50%', right: '25%' },
      parallax: { x: scroll * 45, y: -scroll * 35 }
    }
  ];

  return (
    <div className="fixed inset-0 z-20 pointer-events-none">
      {overlays.map((overlay) => (
        <motion.div
          key={overlay.id}
          style={{
            position: 'absolute',
            ...overlay.position,
            filter: "blur(8px)",
            background: "rgba(0,0,0,0.4)",
            textShadow: "0 0 16px #00fff7",
            transform: `rotate(${cameraAngle * 0.1}deg)`
          }}
          animate={{ 
            opacity: overlay.active ? 1 : 0,
            y: overlay.parallax.y,
            x: overlay.parallax.x,
            scale: overlay.active ? 1 : 0.8
          }}
          transition={{ 
            duration: 0.8, 
            ease: [0.23, 1, 0.32, 1] 
          }}
          className="p-8 rounded-xl max-w-2xl backdrop-blur-sm"
        >
          <div className="text-cyan-400 font-terminal text-2xl font-bold">
            {overlay.content}
          </div>
        </motion.div>
      ))}
    </div>
  );
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
    window.addEventListener('pointermove', onPointerMove);
    return () => window.removeEventListener('pointermove', onPointerMove);
  }, []);

  return (
    <>
      <Canvas camera={{ position: [0, 0, 7], fov: 50 }}>
        <CameraController scroll={scroll} />
        <ambientLight intensity={0.25} />
        <pointLight position={[0, 0, 8]} intensity={2} color="#00fff7" />
        <WireframeSphere scroll={scroll} />
        <EnergyLayer scroll={scroll} mouse={mouse} />
        <EffectComposer>
          <Bloom luminanceThreshold={0.15} luminanceSmoothing={0.8} intensity={2.2} />
          <DepthOfField focusDistance={0.015 + 0.02 * scroll} focalLength={0.05} bokehScale={3 + 2 * scroll} height={700} />
        </EffectComposer>
      </Canvas>
      <DynamicOverlays scroll={scroll} />
    </>
  );
} 