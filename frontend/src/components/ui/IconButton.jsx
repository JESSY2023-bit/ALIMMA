import { forwardRef } from "react";
import { Icon } from "./Icon";
import { cx } from "./utils";

/** Bouton icône seule : `aria-label` est OBLIGATOIRE (aucun texte visible). variant : "outline" | "ghost" */
export const IconButton = forwardRef(function IconButton(
  { icon, variant = "outline", filled, className, type = "button", ...rest },
  ref,
) {
  return (
    <button ref={ref} type={type} className={cx("ui-iconbtn", variant === "ghost" && "ui-iconbtn--ghost", className)} {...rest}>
      <Icon name={icon} filled={filled} size={20} />
    </button>
  );
});
