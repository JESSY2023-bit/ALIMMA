import { Icon } from "./Icon";

export function EmptyState({ icon = "inventory_2", title, children, action }) {
  return (
    <div className="empty">
      <Icon name={icon} />
      <h3 className="t-h3">{title}</h3>
      {children && <p>{children}</p>}
      {action}
    </div>
  );
}
