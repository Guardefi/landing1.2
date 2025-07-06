"use client";
import { motion } from "framer-motion";
import { ReactNode } from "react";

interface AnimatedButtonProps {
  children: ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
  className?: string;
}

export default function AnimatedButton({
  children,
  onClick,
  type = "button",
  disabled = false,
  className = "",
}: AnimatedButtonProps) {
  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`
        relative overflow-hidden rounded-lg bg-cyan-400 px-6 py-3 font-bold text-black
        transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed
        ${className}
      `}
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6 }}
    >
      {/* Animated background effect */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-cyan-300 to-cyan-500"
        initial={{ x: "-100%" }}
        whileHover={!disabled ? { x: "0%" } : {}}
        transition={{ duration: 0.3 }}
      />

      {/* Button content */}
      <span className="relative z-10">{children}</span>

      {/* Hover glow effect */}
      <motion.div
        className="absolute inset-0 rounded-lg"
        initial={{ boxShadow: "0 0 0 rgba(0, 255, 247, 0)" }}
        whileHover={
          !disabled
            ? {
                boxShadow:
                  "0 0 20px rgba(0, 255, 247, 0.5), 0 0 40px rgba(0, 255, 247, 0.3)",
              }
            : {}
        }
        transition={{ duration: 0.3 }}
      />
    </motion.button>
  );
}
