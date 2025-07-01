import { useEffect, useRef } from "react";
import { motion } from "framer-motion";

interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  life: number;
  maxLife: number;
  color: string;
  size: number;
}

export const ParticleField = ({
  particleCount = 50,
  colors = ["#00ff88", "#00ffff", "#ff4444", "#ffaa00"],
  className = "",
}: {
  particleCount?: number;
  colors?: string[];
  className?: string;
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number>();
  const particlesRef = useRef<Particle[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const resizeCanvas = () => {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    };

    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Initialize particles
    particlesRef.current = Array.from({ length: particleCount }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 2,
      vy: (Math.random() - 0.5) * 2,
      life: Math.random() * 100,
      maxLife: 100,
      color: colors[Math.floor(Math.random() * colors.length)],
      size: Math.random() * 3 + 1,
    }));

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      particlesRef.current.forEach((particle, index) => {
        // Update particle
        particle.x += particle.vx;
        particle.y += particle.vy;
        particle.life -= 1;

        // Wrap around edges
        if (particle.x < 0) particle.x = canvas.width;
        if (particle.x > canvas.width) particle.x = 0;
        if (particle.y < 0) particle.y = canvas.height;
        if (particle.y > canvas.height) particle.y = 0;

        // Reset particle when life is over
        if (particle.life <= 0) {
          particle.x = Math.random() * canvas.width;
          particle.y = Math.random() * canvas.height;
          particle.life = particle.maxLife;
          particle.color = colors[Math.floor(Math.random() * colors.length)];
        }

        // Draw particle
        const alpha = particle.life / particle.maxLife;
        ctx.globalAlpha = alpha * 0.6;
        ctx.fillStyle = particle.color;
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fill();

        // Draw connections
        particlesRef.current.forEach((otherParticle, otherIndex) => {
          if (index !== otherIndex) {
            const dx = particle.x - otherParticle.x;
            const dy = particle.y - otherParticle.y;
            const distance = Math.sqrt(dx * dx + dy * dy);

            if (distance < 100) {
              ctx.globalAlpha = (1 - distance / 100) * 0.2;
              ctx.strokeStyle = particle.color;
              ctx.lineWidth = 1;
              ctx.beginPath();
              ctx.moveTo(particle.x, particle.y);
              ctx.lineTo(otherParticle.x, otherParticle.y);
              ctx.stroke();
            }
          }
        });
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [particleCount, colors]);

  return (
    <canvas
      ref={canvasRef}
      className={`absolute inset-0 pointer-events-none ${className}`}
      style={{ zIndex: -1 }}
    />
  );
};

export const FloatingOrbs = ({
  orbCount = 5,
  className = "",
}: {
  orbCount?: number;
  className?: string;
}) => {
  return (
    <div
      className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}
    >
      {Array.from({ length: orbCount }).map((_, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full blur-xl opacity-30"
          style={{
            width: Math.random() * 200 + 100,
            height: Math.random() * 200 + 100,
            background: `radial-gradient(circle, ${
              ["#00ff88", "#00ffff", "#ff4444", "#ffaa00", "#ff88ff"][i % 5]
            } 0%, transparent 70%)`,
          }}
          initial={{
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
          }}
          animate={{
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
          }}
          transition={{
            duration: Math.random() * 20 + 10,
            repeat: Infinity,
            repeatType: "reverse",
            ease: "linear",
          }}
        />
      ))}
    </div>
  );
};

export const NetworkLines = ({
  nodes,
  className = "",
}: {
  nodes: { x: number; y: number; active?: boolean }[];
  className?: string;
}) => {
  return (
    <svg className={`absolute inset-0 pointer-events-none ${className}`}>
      <defs>
        <filter id="glow-line">
          <feGaussianBlur stdDeviation="3" result="coloredBlur" />
          <feMerge>
            <feMergeNode in="coloredBlur" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
      </defs>
      {nodes.map((node, i) =>
        nodes.slice(i + 1).map((otherNode, j) => {
          const distance = Math.sqrt(
            Math.pow(node.x - otherNode.x, 2) +
              Math.pow(node.y - otherNode.y, 2),
          );

          if (distance < 200) {
            return (
              <motion.line
                key={`${i}-${j}`}
                x1={`${node.x}%`}
                y1={`${node.y}%`}
                x2={`${otherNode.x}%`}
                y2={`${otherNode.y}%`}
                stroke={node.active || otherNode.active ? "#00ff88" : "#00ffff"}
                strokeWidth="1"
                strokeOpacity={0.4}
                filter="url(#glow-line)"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{
                  duration: 2,
                  delay: Math.random() * 2,
                  repeat: Infinity,
                  repeatType: "reverse",
                }}
              />
            );
          }
          return null;
        }),
      )}
    </svg>
  );
};

export const DataFlow = ({
  fromNode,
  toNode,
  color = "#00ff88",
  className = "",
}: {
  fromNode: { x: number; y: number };
  toNode: { x: number; y: number };
  color?: string;
  className?: string;
}) => {
  return (
    <motion.div
      className={`absolute w-2 h-2 rounded-full ${className}`}
      style={{ backgroundColor: color, boxShadow: `0 0 10px ${color}` }}
      initial={{
        left: `${fromNode.x}%`,
        top: `${fromNode.y}%`,
        scale: 0,
      }}
      animate={{
        left: `${toNode.x}%`,
        top: `${toNode.y}%`,
        scale: [0, 1, 0],
      }}
      transition={{
        duration: 2,
        ease: "easeInOut",
      }}
    />
  );
};
