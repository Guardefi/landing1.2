import { useThree } from '@react-three/fiber';
import { useLayoutEffect, useRef } from 'react';
import { gsap } from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';

gsap.registerPlugin(ScrollTrigger);

export function CameraRig() {
  const { camera } = useThree();
  const timeline = useRef<gsap.core.Timeline>();

  useLayoutEffect(() => {
    // Create the master timeline for camera movements
    timeline.current = gsap.timeline({});

    // SCENE 1: Initial view - Wide perspective of the Dark Forest
    timeline.current.set(camera.position, { x: 0, y: 0, z: 10 });
    timeline.current.set(camera.rotation, { x: 0, y: 0, z: 0 });

    // SCENE 2: Zoom into the Scorpius Core (Hero section)
    timeline.current.to(camera.position, { 
      x: 0, 
      y: 0, 
      z: 5, 
      duration: 2,
      ease: "power2.inOut"
    }, 1);

    // SCENE 3: Move closer to inspect the core (Features introduction)
    timeline.current.to(camera.position, { 
      x: 2, 
      y: 1, 
      z: 3, 
      duration: 1.5,
      ease: "power2.inOut"
    }, 3);
    timeline.current.to(camera.rotation, { 
      y: Math.PI * 0.15, 
      x: -0.1,
      duration: 1.5,
      ease: "power2.inOut"
    }, 3);

    // SCENE 4: Circle around to the "Hive Alert" module position
    timeline.current.to(camera.position, { 
      x: 1, 
      y: -1, 
      z: 4, 
      duration: 2,
      ease: "power2.inOut"
    }, 5);
    timeline.current.to(camera.rotation, { 
      y: Math.PI * 0.25, 
      x: 0.05,
      duration: 2,
      ease: "power2.inOut"
    }, 5);

    // SCENE 5: Move to "Bytecode Engine" position
    timeline.current.to(camera.position, { 
      x: -1.5, 
      y: 0.5, 
      z: 3.5, 
      duration: 2,
      ease: "power2.inOut"
    }, 7);
    timeline.current.to(camera.rotation, { 
      y: -Math.PI * 0.2, 
      x: -0.05,
      duration: 2,
      ease: "power2.inOut"
    }, 7);

    // SCENE 6: Final wide shot for conclusion/CTA
    timeline.current.to(camera.position, { 
      x: 0, 
      y: 2, 
      z: 8, 
      duration: 2.5,
      ease: "power2.inOut"
    }, 9);
    timeline.current.to(camera.rotation, { 
      y: 0, 
      x: -0.2,
      duration: 2.5,
      ease: "power2.inOut"
    }, 9);

    // Link the timeline to scroll progress
    ScrollTrigger.create({
      trigger: '#scroll-container',
      start: 'top top',
      end: 'bottom bottom',
      scrub: 1, // Smooth scrubbing effect
      animation: timeline.current,
      invalidateOnRefresh: true,
    });

    return () => {
      ScrollTrigger.getAll().forEach(trigger => trigger.kill());
    };
  }, [camera]);

  return null; // This component doesn't render anything visual
} 