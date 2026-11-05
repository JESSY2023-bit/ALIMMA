export function Spinner({ className }) {
  return <span className={className ? `ui-spinner ${className}` : "ui-spinner"} aria-hidden="true" />;
}
