"use client";

import { forwardRef, ReactNode } from "react";
import { Float } from "@react-three/drei";

import {
  SecurityAsteroid,
  SecurityAsteroidProps,
} from "@/components/SecurityAsteroid";
import { Group } from "three";

type FloatingSecurityAsteroidProps = {
  variant?: SecurityAsteroidProps["variant"];
  floatSpeed?: number;
  rotationIntensity?: number;
  floatIntensity?: number;
  floatingRange?: [number, number];
  children?: ReactNode;
};

const FloatingSecurityAsteroid = forwardRef<
  Group,
  FloatingSecurityAsteroidProps
>(
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
          <SecurityAsteroid variant={variant} />
        </Float>
      </group>
    );
  },
);

FloatingSecurityAsteroid.displayName = "FloatingSecurityAsteroid";

export default FloatingSecurityAsteroid;
