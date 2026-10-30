import { useId, type ReactNode } from 'react'

export interface FieldProps {
  label?: string
  /** Affiche « (facultatif) » après le libellé. */
  optional?: boolean
  hint?: string
  /** Message d'erreur : dit quoi faire. Passe le champ à l'état erreur. */
  error?: string
  success?: string
}

export function useFieldA11y({ id, hint, error, success }: { id?: string } & Pick<FieldProps, 'hint' | 'error' | 'success'>) {
  const auto = useId()
  const base = id ?? auto
  const msgId = `${base}-msg`
  return { id: base, msgId, describedBy: error || success || hint ? msgId : undefined }
}

interface ShellProps extends FieldProps {
  id: string
  msgId: string
  className?: string
  children: ReactNode
}

export function FieldShell({ id, msgId, label, optional, hint, error, success, className, children }: ShellProps) {
  const msg = error ?? success ?? hint
  const kind = error ? 'error' : success ? 'success' : 'hint'
  return (
    <div className={className ? `ui-field ${className}` : 'ui-field'}>
      {label && (
        <label className="ui-label" htmlFor={id}>
          {label} {optional && <span className="ui-label__opt">(facultatif)</span>}
        </label>
      )}
      {children}
      {msg && (
        <p id={msgId} className={`ui-msg ui-msg--${kind}`}>
          {msg}
        </p>
      )}
    </div>
  )
}
