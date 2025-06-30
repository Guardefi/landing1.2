"use client";

import { forwardRef, ReactNode } from "react";
import { Float } from "@react-three/drei";

import { SecurityCube, SecurityCubeProps } from "@/components/SecurityCube";
import { Group } from "three";

type FloatingSecurityCubeProps = {
  variant?: SecurityCubeProps["variant"];
  floatSpeed?: number;
  rotationIntensity?: number;
  floatIntensity?: number;
  floatingRange?: [number, number];
  children?: ReactNode;
};

const FloatingSecurityCube = forwardRef<Group, FloatingSecurityCubeProps>(
  (
    {
      variant = "hive",
      floatSpeed = 1.5,
      rotationIntensity = 1,
      floatIntensity = 1,
      floatingRange = [-0.1, 0.1],
      children,
      ...props
    },
    ref,
  ) => {
    return (
      <group ref={ref} {...props}>
        <Float
          speed={floatSpeed}
          rotationIntensity={rotationIntensity}
          floatIntensity={floatIntensity}
          floatingRange={floatingRange}
        >
          {children}
          <SecurityCube variant={variant} />
        </Float>
      </group>
    );
  },
);

FloatingSecurityCube.displayName = "FloatingSecurityCube";

export default FloatingSecurityCube;
