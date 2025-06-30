"use client";

import { forwardRef, ReactNode } from "react";
import { Float } from "@react-three/drei";

import { Rocket, RocketProps } from "@/components/Rocket";
import { Group } from "three";

type FloatingRocketProps = {
  variant?: RocketProps["variant"];
  floatSpeed?: number;
  rotationIntensity?: number;
  floatIntensity?: number;
  floatingRange?: [number, number];
  children?: ReactNode;
};

const FloatingRocket = forwardRef<Group, FloatingRocketProps>(
  (
    {
      variant = "explorer",
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
          <Rocket variant={variant} />
        </Float>
      </group>
    );
  },
);

FloatingRocket.displayName = "FloatingRocket";

export default FloatingRocket;
