export function Spinner({ className }: { className?: string }) {
  return <span className={className ? `ui-spinner ${className}` : 'ui-spinner'} aria-hidden="true" />
}
