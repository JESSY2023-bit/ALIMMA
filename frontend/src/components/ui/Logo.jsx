import { cx } from "./utils";

/** Logo ALIMMA. Remplacez la marque SVG par votre fichier officiel si besoin. */
export function Logo({ inverse = false, className }) {
  return (
    <span className={cx("logo", inverse && "logo--inverse", className)}>
      <span className="logo__mark" aria-hidden="true">
        <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
          <path d="M10 2 16 15H4L10 2Z" fill="#fff" />
          <circle cx="10" cy="9" r="1.6" fill="#F2A541" />
        </svg>
      </span>
      <span>ALIM<span className="logo__ma">MA</span></span>
    </span>
  );
}
