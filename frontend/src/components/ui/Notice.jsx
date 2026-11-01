import { Icon } from "./Icon";
import { cx } from "./utils";

const DEFAULT_ICON = { error: "error", info: "help", warning: "shield", neutral: "lock" };

/**
 * Bandeau d’information : erreur de formulaire, conseil de sécurité, aide.
 * variant : "error" | "info" | "warning" | "neutral" · icon · title
 */
export function Notice({ variant = "neutral", icon, title, children, className }) {
  return (
    <div className={cx("ui-notice", className)} data-variant={variant} role={variant === "error" ? "alert" : undefined}>
      <Icon name={icon ?? DEFAULT_ICON[variant]} filled size={20} />
      <div className="ui-notice__body">
        {title && <p className="ui-notice__title">{title}</p>}
        {children && <div>{children}</div>}
      </div>
    </div>
  );
}
