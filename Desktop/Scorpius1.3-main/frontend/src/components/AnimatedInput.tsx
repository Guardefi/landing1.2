"use client";
import { motion } from "framer-motion";
import { useState } from "react";

interface AnimatedInputProps {
  id: string;
  type: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder: string;
  required?: boolean;
}

export default function AnimatedInput({
  id,
  type,
  value,
  onChange,
  placeholder,
  required = false,
}: AnimatedInputProps) {
  const [isFocused, setIsFocused] = useState(false);

  return (
    <div className="relative">
      <motion.input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        onFocus={() => setIsFocused(true)}
        onBlur={() => setIsFocused(false)}
        required={required}
        className="
          w-full rounded-lg bg-war-room-void/60 px-4 py-3 text-white
          border border-gray-600 focus:border-cyan-400 focus:outline-none
          transition-all duration-300 placeholder-gray-500
        "
        placeholder={placeholder}
        whileFocus={{ scale: 1.02 }}
        transition={{ duration: 0.2 }}
      />

      {/* Animated border glow */}
      <motion.div
        className="absolute inset-0 rounded-lg pointer-events-none"
        initial={{ boxShadow: "0 0 0 rgba(0, 255, 247, 0)" }}
        animate={
          isFocused
            ? {
                boxShadow:
                  "0 0 0 2px rgba(0, 255, 247, 0.3), 0 0 10px rgba(0, 255, 247, 0.2)",
              }
            : {}
        }
        transition={{ duration: 0.3 }}
      />
    </div>
  );
}
