import { useRef, useState, useMemo } from "react";
import { motion } from "framer-motion";

// Fallback 2D visualizations when 3D dependencies are not available
const use3D = false; // Set to true when 3D dependencies are resolved

// Enhanced Server Rack Visualization - 2D Fallback
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
  if (!use3D) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
        className={`w-full h-96 bg-gray-900 rounded-lg p-4 ${className}`}
    >
        <div className="text-white text-center mb-4">
          <h3 className="text-lg font-bold">Server Rack Visualization</h3>
          <p className="text-sm text-gray-400">2D Fallback View</p>
        </div>
        <div className="grid grid-cols-2 gap-4 h-full">
        {[1, 2].map((rackNumber) => (
            <div key={rackNumber} className="bg-gray-800 rounded p-2">
              <div className="text-white text-sm mb-2">Rack {rackNumber}</div>
              <div className="space-y-2">
            {nodes
              .filter((node) => node.rack === rackNumber)
                  .map((node) => (
                    <div
                  key={node.id}
                      className={`p-2 rounded text-xs ${
                        node.status === "active"
                          ? "bg-green-600"
                          : node.status === "maintenance"
                          ? "bg-yellow-600"
                          : node.status === "error"
                          ? "bg-red-600"
                          : "bg-blue-600"
                      }`}
                    >
                      <div className="text-white font-semibold">{node.id}</div>
                      <div className="text-gray-200">
                        CPU: {node.cpu}% | Memory: {node.memory}% | Jobs: {node.jobs}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </motion.div>
  );
  }

  // 3D version would go here when enabled
  return <div>3D visualization not available</div>;
};

// Network Topology Visualization - 2D Fallback
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
  if (!use3D) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
        className={`w-full h-96 bg-gray-900 rounded-lg p-4 ${className}`}
    >
        <div className="text-white text-center mb-4">
          <h3 className="text-lg font-bold">Network Topology</h3>
          <p className="text-sm text-gray-400">2D Fallback View</p>
        </div>
        <div className="grid grid-cols-3 gap-4 h-full">
        {nodes.map((node) => (
            <div
              key={node.id}
              className={`p-3 rounded-lg border-2 ${
                node.status === "active"
                  ? "border-green-500 bg-green-900/20"
                  : node.status === "maintenance"
                  ? "border-yellow-500 bg-yellow-900/20"
                  : node.status === "error"
                  ? "border-red-500 bg-red-900/20"
                  : "border-gray-500 bg-gray-900/20"
              }`}
            >
              <div className="text-white font-semibold">{node.name}</div>
              <div className="text-gray-300 text-sm">{node.id}</div>
              <div className={`text-xs mt-1 ${
                node.status === "active"
                  ? "text-green-400"
                  : node.status === "maintenance"
                  ? "text-yellow-400"
                  : node.status === "error"
                  ? "text-red-400"
                  : "text-gray-400"
              }`}>
                {node.status.toUpperCase()}
              </div>
            </div>
          ))}
        </div>
        <div className="mt-4 text-white text-sm">
          <div>Active Connections: {connections.filter(c => c.active).length}</div>
          <div>Total Connections: {connections.length}</div>
        </div>
    </motion.div>
  );
  }

  // 3D version would go here when enabled
  return <div>3D visualization not available</div>;
};

// Export placeholder for other components that might use 3D
export const DataFlowParticles = ({ nodes }: { nodes: any[] }) => {
  return (
    <div className="text-gray-400 text-sm">
      Data flow visualization (2D fallback)
    </div>
  );
};

export const NetworkNode3D = ({ node }: { node: any }) => {
  return (
    <div className="p-2 bg-gray-800 rounded text-white text-sm">
      {node.name}
            </div>
  );
};

export const NetworkConnection3D = ({ from, to, active }: { from: any; to: any; active: boolean }) => {
  return (
    <div className={`h-1 ${active ? "bg-green-500" : "bg-gray-500"} rounded`}>
      {/* Connection line placeholder */}
    </div>
  );
};

// When 3D is enabled, you can uncomment and modify this:
/*
if (use3D) {
  // Import 3D dependencies here
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
  
  // Implement full 3D versions here
}
*/
