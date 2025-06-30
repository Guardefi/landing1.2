"use client";

import { useRef } from "react";
import { Environment, OrbitControls } from "@react-three/drei";
import { Group } from "three";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ScrollTrigger } from "gsap/ScrollTrigger";

import FloatingRocket from "@/components/FloatingRocket";
import { useStore } from "@/hooks/useStore";

gsap.registerPlugin(useGSAP, ScrollTrigger);

type Props = {};

export default function SpaceScene({}: Props) {
  const isReady = useStore((state) => state.isReady);

  const rocket1Ref = useRef<Group>(null);
  const rocket2Ref = useRef<Group>(null);
  const rocket3Ref = useRef<Group>(null);
  const rocket4Ref = useRef<Group>(null);
  const rocket5Ref = useRef<Group>(null);

  const rocket1GroupRef = useRef<Group>(null);
  const rocket2GroupRef = useRef<Group>(null);

  const groupRef = useRef<Group>(null);

  const FLOAT_SPEED = 1.5;

  useGSAP(() => {
    if (
      !rocket1Ref.current ||
      !rocket2Ref.current ||
      !rocket3Ref.current ||
      !rocket4Ref.current ||
      !rocket5Ref.current ||
      !rocket1GroupRef.current ||
      !rocket2GroupRef.current ||
      !groupRef.current
    )
      return;

    isReady();

    // Set rocket starting locations
    gsap.set(rocket1Ref.current.position, { x: -1.5 });
    gsap.set(rocket1Ref.current.rotation, { z: -0.5 });

    gsap.set(rocket2Ref.current.position, { x: 1.5 });
    gsap.set(rocket2Ref.current.rotation, { z: 0.5 });

    gsap.set(rocket3Ref.current.position, { y: 5, z: 2 });
    gsap.set(rocket4Ref.current.position, { x: 2, y: 4, z: 2 });
    gsap.set(rocket5Ref.current.position, { y: -5 });

    const introTl = gsap.timeline({
      defaults: {
        duration: 3,
        ease: "back.out(1.4)",
      },
    });

    if (window.scrollY < 20) {
      introTl
        .from(rocket1GroupRef.current.position, { y: -5, x: 1 }, 0)
        .from(rocket1GroupRef.current.rotation, { z: 3 }, 0)
        .from(rocket2GroupRef.current.position, { y: 5, x: 1 }, 0)
        .from(rocket2GroupRef.current.rotation, { z: 3 }, 0);
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
      // Rotate rocket group
      .to(groupRef.current.rotation, { y: Math.PI * 2 })

      // Rocket 1 - Explorer
      .to(rocket1Ref.current.position, { x: -0.2, y: -0.7, z: -2 }, 0)
      .to(rocket1Ref.current.rotation, { z: 0.3 }, 0)

      // Rocket 2 - Fighter
      .to(rocket2Ref.current.position, { x: 1, y: -0.2, z: -1 }, 0)
      .to(rocket2Ref.current.rotation, { z: 0 }, 0)

      // Rocket 3 - Cargo
      .to(rocket3Ref.current.position, { x: -0.3, y: 0.5, z: -1 }, 0)
      .to(rocket3Ref.current.rotation, { z: -0.1 }, 0)

      // Rocket 4 - Scout
      .to(rocket4Ref.current.position, { x: 0, y: -0.3, z: 0.5 }, 0)
      .to(rocket4Ref.current.rotation, { z: 0.3 }, 0)

      // Rocket 5 - Interceptor
      .to(rocket5Ref.current.position, { x: 0.3, y: 0.5, z: -0.5 }, 0)
      .to(rocket5Ref.current.rotation, { z: -0.25 }, 0)
      .to(
        groupRef.current.position,
        { x: 1, duration: 3, ease: "sine.inOut" },
        1.3,
      );
  });

  return (
    <group ref={groupRef}>
      <group ref={rocket1GroupRef}>
        <FloatingRocket
          ref={rocket1Ref}
          variant="explorer"
          floatSpeed={FLOAT_SPEED}
        />
      </group>
      <group ref={rocket2GroupRef}>
        <FloatingRocket
          ref={rocket2Ref}
          variant="fighter"
          floatSpeed={FLOAT_SPEED}
        />
      </group>

      <FloatingRocket
        ref={rocket3Ref}
        variant="cargo"
        floatSpeed={FLOAT_SPEED}
      />

      <FloatingRocket
        ref={rocket4Ref}
        variant="scout"
        floatSpeed={FLOAT_SPEED}
      />

      <FloatingRocket
        ref={rocket5Ref}
        variant="interceptor"
        floatSpeed={FLOAT_SPEED}
      />

      {/* <OrbitControls /> */}
      <Environment preset="night" environmentIntensity={0.8} />
    </group>
  );
}
