import { useEffect, useRef, useState, useCallback } from "react";

interface InteractiveGridProps {
  className?: string;
  cellSize?: number;
  glowColor?: string;
  opacity?: number;
}

export const InteractiveGrid = ({
  className = "",
  cellSize = 20,
  glowColor = "rgba(0, 255, 255, 0.4)",
  opacity = 0.2,
}: InteractiveGridProps) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredCell, setHoveredCell] = useState<{
    x: number;
    y: number;
  } | null>(null);

  const handleMouseMove = useCallback(
    (e: MouseEvent) => {
      if (!containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      const x = Math.floor((e.clientX - rect.left) / cellSize);
      const y = Math.floor((e.clientY - rect.top) / cellSize);

      setHoveredCell({ x, y });
    },
    [cellSize],
  );

  const handleMouseLeave = useCallback(() => {
    setHoveredCell(null);
  }, []);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener("mousemove", handleMouseMove);
    container.addEventListener("mouseleave", handleMouseLeave);

    return () => {
      container.removeEventListener("mousemove", handleMouseMove);
      container.removeEventListener("mouseleave", handleMouseLeave);
    };
  }, [handleMouseMove, handleMouseLeave]);

  return (
    <div
      ref={containerRef}
      className={`absolute inset-0 ${className}`}
      style={{ opacity }}
    >
      {/* Base grid pattern */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `
            linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px)
          `,
          backgroundSize: `${cellSize}px ${cellSize}px`,
        }}
      />

      {/* Interactive highlight */}
      {hoveredCell && (
        <div
          className="absolute pointer-events-none transition-all duration-150 ease-out"
          style={{
            left: hoveredCell.x * cellSize,
            top: hoveredCell.y * cellSize,
            width: cellSize,
            height: cellSize,
            background: `radial-gradient(circle, ${glowColor} 0%, rgba(0, 255, 255, 0.15) 70%, transparent 100%)`,
            boxShadow: `0 0 15px ${glowColor}, 0 0 30px rgba(0, 255, 255, 0.3)`,
            transform: "translateZ(8px) scale(1.1)",
            transformStyle: "preserve-3d",
            borderRadius: "2px",
          }}
        />
      )}
    </div>
  );
};
