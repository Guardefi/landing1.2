import { useThree } from '@react-three/fiber';
import { useEffect } from 'react';
import gsap from 'gsap';

function useScrollCamera(scroll: number) {
  const { camera } = useThree();

  useEffect(() => {
    // Define camera keyframes for different scroll positions
    const keyframes = [
      { scroll: 0.0, pos: [0, 0, 7], fov: 50 },
      { scroll: 0.25, pos: [1, 0.5, 6], fov: 55 },
      { scroll: 0.5, pos: [0, 1.2, 4.5], fov: 60 },
      { scroll: 0.75, pos: [-1, 0.5, 6], fov: 55 },
      { scroll: 1.0, pos: [0, 0, 7], fov: 50 },
    ];

    // Find which keyframes to interpolate between
    let prev = keyframes[0], next = keyframes[keyframes.length - 1];
    for (let i = 1; i < keyframes.length; i++) {
      if (scroll <= keyframes[i].scroll) {
        prev = keyframes[i - 1];
        next = keyframes[i];
        break;
      }
    }
    const t = (scroll - prev.scroll) / (next.scroll - prev.scroll);
    const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
    const pos = [
      lerp(prev.pos[0], next.pos[0], t),
      lerp(prev.pos[1], next.pos[1], t),
      lerp(prev.pos[2], next.pos[2], t),
    ];
    const fov = lerp(prev.fov, next.fov, t);

    // Animate camera with GSAP
    gsap.to(camera.position, {
      x: pos[0],
      y: pos[1],
      z: pos[2],
      duration: 0.8,
      ease: 'power2.out',
      overwrite: 'auto',
    });
    gsap.to(camera, {
      fov,
      duration: 0.8,
      ease: 'power2.out',
      overwrite: 'auto',
      onUpdate: () => camera.updateProjectionMatrix(),
    });
    camera.lookAt(0, 0, 0);
  }, [scroll, camera]);
}

export { useScrollCamera };