'use client';
import { motion, AnimatePresence } from 'framer-motion';

interface AnimatedSectionProps {
  children: React.ReactNode;
  active: boolean;
  align?: 'left' | 'center' | 'right';
}

export default function AnimatedSection({ 
  children, 
  active, 
  align = 'center' 
}: AnimatedSectionProps) {
  // Calculate entrance direction based on alignment
  const getInitialPosition = () => {
    switch (align) {
      case 'left':
        return { opacity: 0, x: -120, y: 60 };
      case 'right':
        return { opacity: 0, x: 120, y: 60 };
      default:
        return { opacity: 0, x: 0, y: 80 };
    }
  };

  const getExitPosition = () => {
    switch (align) {
      case 'left':
        return { opacity: 0, x: -80, y: -60 };
      case 'right':
        return { opacity: 0, x: 80, y: -60 };
      default:
        return { opacity: 0, x: 0, y: -80 };
    }
  };

  // Advanced easing curve for smooth, cinematic motion
  const transition = {
    duration: 1.2,
    ease: [0.23, 1, 0.32, 1], // Custom cubic-bezier for smooth motion
    type: "tween"
  };

  return (
    <AnimatePresence mode="wait">
      {active && (
        <motion.div
          key={`section-${align}`}
          initial={getInitialPosition()}
          animate={{ 
            opacity: 1, 
            x: 0, 
            y: 0,
            scale: 1,
            rotateX: 0,
            rotateY: 0
          }}
          exit={getExitPosition()}
          transition={transition}
          className="absolute inset-0 flex items-center justify-center p-4"
          style={{
            perspective: '1000px',
          }}
        >
          <motion.div
            initial={{ rotateX: 10, scale: 0.95 }}
            animate={{ rotateX: 0, scale: 1 }}
            exit={{ rotateX: -10, scale: 0.95 }}
            transition={{ ...transition, delay: 0.1 }}
            className="w-full"
          >
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
} 