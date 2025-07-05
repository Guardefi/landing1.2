import { useRef, useState, useMemo } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import {
  OrbitControls,
  Text,
  Sphere,
  Box,
  Cylinder,
  Environment,
  ContactShadows,
  Float,
  useGLTF,
  PerspectiveCamera,
  Html,
} from "@react-three/drei";
import * as THREE from "three";
import { motion } from "framer-motion";

// Enhanced Server Rack Visualization
export const ServerRack3D = ({
  nodes,
  className = "",
}: {
  nodes: Array<{
    id: string;
    rack: number;
    slot: number;
    status: string;
    cpu: number;
    memory: number;
    jobs: number;
  }>;
  className?: string;
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      className={`w-full h-96 ${className}`}
    >
      <Canvas camera={{ position: [8, 6, 8], fov: 60 }}>
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1} />
        <spotLight
          position={[0, 15, 0]}
          angle={0.3}
          penumbra={1}
          intensity={2}
          castShadow
        />

        <Environment preset="night" />
        <ContactShadows
          rotation-x={Math.PI / 2}
          position={[0, -2, 0]}
          opacity={0.4}
          width={20}
          height={20}
          blur={1}
          far={10}
        />

        {/* Rack Structure */}
        {[1, 2].map((rackNumber) => (
          <group key={rackNumber} position={[(rackNumber - 1.5) * 3, 0, 0]}>
            {/* Rack Frame */}
            <Box
              args={[2.5, 6, 1]}
              position={[0, 0, 0]}
              material={
                new THREE.MeshStandardMaterial({
                  color: "#2a2a2a",
                  metalness: 0.8,
                  roughness: 0.2,
                })
              }
            />

            {/* Server Nodes */}
            {nodes
              .filter((node) => node.rack === rackNumber)
              .map((node, index) => (
                <ServerNode3D
                  key={node.id}
                  node={node}
                  position={[0, 2 - index * 1.2, 0.6]}
                />
              ))}
          </group>
        ))}

        {/* Data Flow Visualization */}
        <DataFlowParticles nodes={nodes} />

        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          autoRotate={true}
          autoRotateSpeed={1}
        />
      </Canvas>
    </motion.div>
  );
};

// Individual Server Node
const ServerNode3D = ({
  node,
  position,
}: {
  node: {
    id: string;
    status: string;
    cpu: number;
    memory: number;
    jobs: number;
  };
  position: [number, number, number];
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y = Math.sin(Date.now() * 0.001) * 0.1;
    }
  });

  const statusColor =
    {
      active: "#00ff88",
      maintenance: "#ffaa00",
      error: "#ff4444",
      idle: "#00ffff",
    }[node.status] || "#888888";

  return (
    <Float speed={2} rotationIntensity={0.2} floatIntensity={0.5}>
      <group position={position}>
        <Box
          ref={meshRef}
          args={[2, 0.8, 0.8]}
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
          material={
            new THREE.MeshStandardMaterial({
              color: hovered ? statusColor : "#1a1a1a",
              metalness: 0.6,
              roughness: 0.4,
              emissive: statusColor,
              emissiveIntensity: node.status === "active" ? 0.1 : 0.05,
            })
          }
        />

        {/* Status LED */}
        <Sphere
          args={[0.05]}
          position={[0.8, 0.2, 0.41]}
          material={
            new THREE.MeshStandardMaterial({
              color: statusColor,
              emissive: statusColor,
              emissiveIntensity: 0.5,
            })
          }
        />

        {/* CPU Usage Indicator */}
        <Box
          args={[0.3, 0.1, 0.02]}
          position={[-0.5, 0.1, 0.41]}
          material={
            new THREE.MeshStandardMaterial({
              color: node.cpu > 80 ? "#ff4444" : "#00ff88",
              emissive: node.cpu > 80 ? "#ff4444" : "#00ff88",
              emissiveIntensity: 0.2,
            })
          }
        />

        {hovered && (
          <Html position={[0, 1, 0]} center>
            <div className="bg-black/90 text-white p-2 rounded text-xs whitespace-nowrap">
              <div>{node.id}</div>
              <div>CPU: {node.cpu}%</div>
              <div>Memory: {node.memory}%</div>
              <div>Jobs: {node.jobs}</div>
            </div>
          </Html>
        )}
      </group>
    </Float>
  );
};

// Data Flow Particles
const DataFlowParticles = ({
  nodes,
}: {
  nodes: Array<{ rack: number; slot: number; status: string }>;
}) => {
  const particlesRef = useRef<THREE.Points>(null);
  const particleCount = 200;

  const particles = useMemo(() => {
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);

    for (let i = 0; i < particleCount; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 8;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10;

      const color = new THREE.Color("#00ff88");
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    }

    return { positions, colors };
  }, []);

  useFrame((state) => {
    if (particlesRef.current) {
      const positions = particlesRef.current.geometry.attributes.position
        .array as Float32Array;

      for (let i = 0; i < particleCount; i++) {
        positions[i * 3 + 1] +=
          Math.sin(state.clock.elapsedTime + i * 0.1) * 0.01;
      }

      particlesRef.current.geometry.attributes.position.needsUpdate = true;
      particlesRef.current.rotation.y = state.clock.elapsedTime * 0.1;
    }
  });

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particleCount}
          array={particles.positions}
          itemSize={3}
        />
        <bufferAttribute
          attach="attributes-color"
          count={particleCount}
          array={particles.colors}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.05}
        vertexColors
        transparent
        opacity={0.6}
        sizeAttenuation={true}
      />
    </points>
  );
};

// Network Topology 3D
export const NetworkTopology3D = ({
  nodes,
  connections,
  className = "",
}: {
  nodes: Array<{
    id: string;
    name: string;
    status: string;
    position: [number, number, number];
  }>;
  connections: Array<{ from: string; to: string; active: boolean }>;
  className?: string;
}) => {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
      className={`w-full h-96 ${className}`}
    >
      <Canvas camera={{ position: [0, 0, 10], fov: 60 }}>
        <ambientLight intensity={0.4} />
        <pointLight position={[10, 10, 10]} intensity={1} />

        <Environment preset="night" />

        {/* Network Nodes */}
        {nodes.map((node) => (
          <NetworkNode3D key={node.id} node={node} />
        ))}

        {/* Network Connections */}
        {connections.map((connection, index) => {
          const fromNode = nodes.find((n) => n.id === connection.from);
          const toNode = nodes.find((n) => n.id === connection.to);

          if (fromNode && toNode) {
            return (
              <NetworkConnection3D
                key={index}
                from={fromNode.position}
                to={toNode.position}
                active={connection.active}
              />
            );
          }
          return null;
        })}

        <OrbitControls
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          autoRotate={true}
          autoRotateSpeed={0.5}
        />
      </Canvas>
    </motion.div>
  );
};

// Individual Network Node
const NetworkNode3D = ({
  node,
}: {
  node: {
    id: string;
    name: string;
    status: string;
    position: [number, number, number];
  };
}) => {
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  useFrame(() => {
    if (meshRef.current) {
      meshRef.current.rotation.y += 0.01;
    }
  });

  const statusColor =
    {
      healthy: "#00ff88",
      warning: "#ffaa00",
      error: "#ff4444",
    }[node.status] || "#888888";

  return (
    <Float speed={1} rotationIntensity={0.1} floatIntensity={0.3}>
      <group position={node.position}>
        <Sphere
          ref={meshRef}
          args={[0.5]}
          onPointerOver={() => setHovered(true)}
          onPointerOut={() => setHovered(false)}
          material={
            new THREE.MeshStandardMaterial({
              color: hovered ? statusColor : "#1a1a1a",
              metalness: 0.8,
              roughness: 0.2,
              emissive: statusColor,
              emissiveIntensity: 0.2,
            })
          }
        />

        {hovered && (
          <Html position={[0, 1, 0]} center>
            <div className="bg-black/90 text-white p-2 rounded text-xs whitespace-nowrap">
              <div className="font-bold">{node.name}</div>
              <div>Status: {node.status}</div>
            </div>
          </Html>
        )}

        <Text
          position={[0, -0.8, 0]}
          fontSize={0.2}
          color="white"
          anchorX="center"
          anchorY="middle"
        >
          {node.name}
        </Text>
      </group>
    </Float>
  );
};

// Network Connection Line
const NetworkConnection3D = ({
  from,
  to,
  active,
}: {
  from: [number, number, number];
  to: [number, number, number];
  active: boolean;
}) => {
  const lineRef = useRef<THREE.BufferGeometry>(null);

  const points = [new THREE.Vector3(...from), new THREE.Vector3(...to)];

  return (
    <line>
      <bufferGeometry ref={lineRef} setFromPoints={points} />
      <lineBasicMaterial
        color={active ? "#00ff88" : "#333333"}
        linewidth={active ? 3 : 1}
        transparent
        opacity={active ? 0.8 : 0.3}
      />
    </line>
  );
};
