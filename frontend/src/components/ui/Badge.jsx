import { Icon } from "./Icon";

/** Pastille d’état. tone : "neutral" | "primary" | "gold" | "success" | "info" | "warning" | "error" | "solid" */
export function Badge({ tone = "neutral", icon, children }) {
  return (
    <span className="ui-badge" data-tone={tone}>
      {icon && <Icon name={icon} filled size={16} />}
      {children}
    </span>
  );
}
