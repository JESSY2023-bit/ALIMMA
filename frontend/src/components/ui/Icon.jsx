import { cx } from "./utils";

/**
 * Icône Material Symbols Rounded (jeu D-008).
 * name : nom de l’icône (ex. "search", "check_circle") · filled : état actif (pleine)
 * size : taille en px · label : si fourni, l’icône est annoncée aux lecteurs d’écran.
 */
export function Icon({ name, filled = false, size, className, label }) {
  const style = {
    fontVariationSettings: `'FILL' ${filled ? 1 : 0}, 'wght' 400, 'GRAD' 0, 'opsz' 24`,
    ...(size ? { fontSize: size } : null),
  };
  return (
    <span
      className={cx("ui-icon", className)}
      style={style}
      aria-hidden={label ? undefined : true}
      role={label ? "img" : undefined}
      aria-label={label}
    >
      {name}
    </span>
  );
}
