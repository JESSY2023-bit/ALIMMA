import { useCallback, useEffect, useState } from "react";

/** Compte à rebours en secondes. Retourne [secondesRestantes, relancer(secondes)]. */
export function useCountdown(initial = 0) {
  const [left, setLeft] = useState(initial);
  useEffect(() => {
    if (left <= 0) return undefined;
    const t = setTimeout(() => setLeft((l) => l - 1), 1000);
    return () => clearTimeout(t);
  }, [left]);
  const reset = useCallback((seconds) => setLeft(seconds), []);
  return [left, reset];
}

export const formatMMSS = (s) => `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
export const formatMSS = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
