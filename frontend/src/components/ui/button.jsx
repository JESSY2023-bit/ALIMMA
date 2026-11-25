import { forwardRef } from "react";
import { Icon } from "./Icon";
import { Spinner } from "./Spinner";
import { cx, useDelayedFlag } from "./utils";

/**
 * Props :
 *  variant : "primary" | "purchase" | "secondary" | "tertiary" | "danger"
 *  size : "lg" (52 px, action principale mobile) | "md" (44 px) | "sm" (36 px, tableaux desktop)
 *  loading : envoi en cours → aria-busy, double envoi impossible, spinner dès 300 ms
 *  loadingLabel : libellé pendant l’envoi (ex. « Création du compte… »)
 *  leadingIcon : nom d’icône · fullWidth : pleine largeur
 * Pour un bouton de formulaire, passez type="submit" (le type par défaut est "button").
 */
export const Button = forwardRef(function Button(
  {
    variant = "primary", size = "md", loading = false, loadingLabel, leadingIcon,
    fullWidth, className, children, onClick, type = "button", ...rest
  },
  ref,
) {
  const showSpinner = useDelayedFlag(loading, 300);
  return (
    <button
      ref={ref}
      type={type}
      className={cx("ui-btn", `ui-btn--${variant}`, `ui-btn--${size}`, fullWidth && "ui-btn--full", className)}
      aria-busy={loading || undefined}
      aria-disabled={loading || undefined}
      onClick={(e) => {
        if (loading) {
          e.preventDefault();
          return;
        }
        onClick?.(e);
      }}
      {...rest}
    >
      {showSpinner ? <Spinner /> : leadingIcon ? <Icon name={leadingIcon} size={20} /> : null}
      {loading && loadingLabel ? loadingLabel : children}
    </button>
  );
});
