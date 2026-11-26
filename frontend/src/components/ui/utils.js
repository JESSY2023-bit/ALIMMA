import { useEffect, useState } from "react";

export const cx = (...classes) => classes.filter(Boolean).join(" ");

/** Devient true seulement après `delay` ms d’attente (indicateur affiché dès 300 ms). */
export function useDelayedFlag(active, delay = 300) {
  const [elapsed, setElapsed] = useState(false);
  useEffect(() => {
    if (!active) return undefined;
    const t = window.setTimeout(() => setElapsed(true), delay);
    return () => window.clearTimeout(t);
  }, [active, delay]);
  return active && elapsed;
}
