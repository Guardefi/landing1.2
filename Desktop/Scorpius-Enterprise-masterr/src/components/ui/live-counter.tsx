import { useState, useEffect } from "react";
import { motion } from "framer-motion";

interface LiveCounterProps {
  value: number;
  suffix?: string;
  decimals?: number;
  duration?: number;
  className?: string;
}

export const LiveCounter = ({
  value,
  suffix = "",
  decimals = 0,
  duration = 1000,
  className = "",
}: LiveCounterProps) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const startValue = displayValue;
    const endValue = value;
    const difference = endValue - startValue;

    if (difference === 0) return;

    const startTime = Date.now();

    const updateValue = () => {
      const currentTime = Date.now();
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function for smooth animation
      const easeOutCubic = 1 - Math.pow(1 - progress, 3);
      const currentValue = startValue + difference * easeOutCubic;

      setDisplayValue(currentValue);

      if (progress < 1) {
        requestAnimationFrame(updateValue);
      } else {
        setDisplayValue(endValue);
      }
    };

    requestAnimationFrame(updateValue);
  }, [value, duration, displayValue]);

  const formatValue = (val: number) => {
    if (decimals > 0) {
      return val.toFixed(decimals);
    }
    return Math.floor(val).toLocaleString();
  };

  return (
    <motion.span
      className={className}
      initial={{ scale: 0.8 }}
      animate={{ scale: 1 }}
      transition={{ duration: 0.3 }}
    >
      {formatValue(displayValue)}
      {suffix}
    </motion.span>
  );
};
