"use client";
import { useEffect, useRef } from "react";

export default function LiquidSandBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationId: number;
    let time = 0;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };

    const animate = () => {
      time += 0.01;

      // Clear canvas
      ctx.fillStyle = "#000000";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Create liquid sand effect with multiple layers
      for (let layer = 0; layer < 3; layer++) {
        ctx.fillStyle = `rgba(${20 + layer * 10}, ${20 + layer * 10}, ${20 + layer * 10}, ${0.3 - layer * 0.1})`;

        ctx.beginPath();
        for (let x = 0; x <= canvas.width; x += 2) {
          const y1 =
            canvas.height * 0.5 +
            Math.sin(x * 0.01 + time * 2 + layer * 0.5) * 50 +
            Math.sin(x * 0.005 + time * 1.5 + layer * 0.3) * 30 +
            Math.sin(x * 0.002 + time * 1 + layer * 0.7) * 80;

          if (x === 0) {
            ctx.moveTo(x, y1);
          } else {
            ctx.lineTo(x, y1);
          }
        }

        ctx.lineTo(canvas.width, canvas.height);
        ctx.lineTo(0, canvas.height);
        ctx.closePath();
        ctx.fill();
      }

      // Add subtle particles
      ctx.fillStyle = "rgba(0, 255, 247, 0.1)";
      for (let i = 0; i < 50; i++) {
        const x =
          Math.sin(time + i * 0.1) * canvas.width * 0.5 + canvas.width * 0.5;
        const y =
          Math.cos(time * 0.5 + i * 0.2) * canvas.height * 0.3 +
          canvas.height * 0.5;
        const size = Math.sin(time * 2 + i) * 2 + 2;

        ctx.beginPath();
        ctx.arc(x, y, size, 0, Math.PI * 2);
        ctx.fill();
      }

      animationId = requestAnimationFrame(animate);
    };

    resize();
    animate();

    window.addEventListener("resize", resize);

    return () => {
      window.removeEventListener("resize", resize);
      cancelAnimationFrame(animationId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 z-0"
      style={{ filter: "blur(1px)" }}
    />
  );
}
