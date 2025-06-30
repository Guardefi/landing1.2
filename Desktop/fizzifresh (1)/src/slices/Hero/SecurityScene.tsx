"use client";

import { useRef } from "react";
import { Environment, OrbitControls } from "@react-three/drei";
import { Group } from "three";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import FloatingSecurityAsteroid from "@/components/FloatingSecurityAsteroid";
import { GalaxyBackground } from "@/components/GalaxyBackground";
import { useStore } from "@/hooks/useStore";

gsap.registerPlugin(useGSAP, ScrollTrigger);

type Props = {};

export default function SecurityScene({}: Props) {
  const isReady = useStore((state) => state.isReady);

  const cube1Ref = useRef<Group>(null);
  const cube2Ref = useRef<Group>(null);
  const cube3Ref = useRef<Group>(null);
  const cube4Ref = useRef<Group>(null);
  const cube5Ref = useRef<Group>(null);

  const cube1GroupRef = useRef<Group>(null);
  const cube2GroupRef = useRef<Group>(null);

  const groupRef = useRef<Group>(null);

  const FLOAT_SPEED = 1.5;

  useGSAP(() => {
    if (
      !cube1Ref.current ||
      !cube2Ref.current ||
      !cube3Ref.current ||
      !cube4Ref.current ||
      !cube5Ref.current ||
      !cube1GroupRef.current ||
      !cube2GroupRef.current ||
      !groupRef.current
    )
      return;

    isReady();

    // Set cube starting locations
    gsap.set(cube1Ref.current.position, { x: -1.5 });
    gsap.set(cube1Ref.current.rotation, { z: -0.5 });

    gsap.set(cube2Ref.current.position, { x: 1.5 });
    gsap.set(cube2Ref.current.rotation, { z: 0.5 });

    gsap.set(cube3Ref.current.position, { y: 5, z: 2 });
    gsap.set(cube4Ref.current.position, { x: 2, y: 4, z: 2 });
    gsap.set(cube5Ref.current.position, { y: -5 });

    const introTl = gsap.timeline({
      defaults: {
        duration: 3,
        ease: "back.out(1.4)",
      },
    });

    if (window.scrollY < 20) {
      introTl
        .from(cube1GroupRef.current.position, { y: -5, x: 1 }, 0)
        .from(cube1GroupRef.current.rotation, { z: 3 }, 0)
        .from(cube2GroupRef.current.position, { y: 5, x: 1 }, 0)
        .from(cube2GroupRef.current.rotation, { z: 3 }, 0);
    }

    const scrollTl = gsap.timeline({
      defaults: {
        duration: 2,
      },
      scrollTrigger: {
        trigger: ".hero",
        start: "top top",
        end: "bottom bottom",
        scrub: 1.5,
      },
    });

    scrollTl
      // Rotate cube group
      .to(groupRef.current.rotation, { y: Math.PI * 2 })

      // Cube 1 - Hive Alert
      .to(cube1Ref.current.position, { x: -0.2, y: -0.7, z: -2 }, 0)
      .to(cube1Ref.current.rotation, { z: 0.3 }, 0)

      // Cube 2 - Bytecode Engine
      .to(cube2Ref.current.position, { x: 1, y: -0.2, z: -1 }, 0)
      .to(cube2Ref.current.rotation, { z: 0 }, 0)

      // Cube 3 - AI Trading Bot
      .to(cube3Ref.current.position, { x: -0.3, y: 0.5, z: -1 }, 0)
      .to(cube3Ref.current.rotation, { z: -0.1 }, 0)

      // Cube 4 - Bridge Network
      .to(cube4Ref.current.position, { x: 0, y: -0.3, z: 0.5 }, 0)
      .to(cube4Ref.current.rotation, { z: 0.3 }, 0)

      // Cube 5 - Wallet Guard
      .to(cube5Ref.current.position, { x: 0.3, y: 0.5, z: -0.5 }, 0)
      .to(cube5Ref.current.rotation, { z: -0.25 }, 0)
      .to(
        groupRef.current.position,
        { x: 1, duration: 3, ease: "sine.inOut" },
        1.3,
      );
  });

  return (
    <group ref={groupRef}>
      {/* Galaxy background */}
      <GalaxyBackground count={12000} />

      <group ref={cube1GroupRef}>
        <FloatingSecurityAsteroid
          ref={cube1Ref}
          variant="hive"
          floatSpeed={FLOAT_SPEED}
        />
      </group>
      <group ref={cube2GroupRef}>
        <FloatingSecurityAsteroid
          ref={cube2Ref}
          variant="bytecode"
          floatSpeed={FLOAT_SPEED}
        />
      </group>

      <FloatingSecurityAsteroid
        ref={cube3Ref}
        variant="ai"
        floatSpeed={FLOAT_SPEED}
      />

      <FloatingSecurityAsteroid
        ref={cube4Ref}
        variant="bridge"
        floatSpeed={FLOAT_SPEED}
      />

      <FloatingSecurityAsteroid
        ref={cube5Ref}
        variant="wallet"
        floatSpeed={FLOAT_SPEED}
      />

      {/* <OrbitControls /> */}
      <Environment preset="night" environmentIntensity={0.1} />
    </group>
  );
}
