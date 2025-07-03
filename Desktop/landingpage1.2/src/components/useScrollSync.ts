import { useEffect, useState } from 'react';

export function useScrollSync() {
  const [scroll, setScroll] = useState(0);
  useEffect(() => {
    const onScroll = () => {
      const max = document.body.scrollHeight - window.innerHeight;
      setScroll(window.scrollY / max);
    };
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);
  return scroll;
} 