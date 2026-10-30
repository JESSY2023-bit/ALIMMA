import { forwardRef, useEffect, useImperativeHandle, useRef, type InputHTMLAttributes, type ReactNode } from 'react'
import { Icon } from './Icon'
import { useFieldA11y } from './Field'

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'children'> {
  label: ReactNode
  /** État indéterminé (« Tout sélectionner »). */
  indeterminate?: boolean
  /** Message sous la case, ex. « Vous devez accepter les CGU pour créer un compte. » */
  error?: string
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(function Checkbox(
  { label, indeterminate = false, error, id, disabled, ...rest },
  ref,
) {
  const inner = useRef<HTMLInputElement>(null)
  useImperativeHandle(ref, () => inner.current as HTMLInputElement)
  useEffect(() => { if (inner.current) inner.current.indeterminate = indeterminate }, [indeterminate])
  const a = useFieldA11y({ id, error })
  return (
    <div>
      <label className="ui-check" data-invalid={error ? true : undefined} data-disabled={disabled || undefined}>
        <input
          ref={inner} id={a.id} type="checkbox" className="ui-check__input" disabled={disabled}
          aria-invalid={error ? true : undefined} aria-describedby={a.describedBy} {...rest}
        />
        <span className="ui-check__box"><Icon name={indeterminate ? 'remove' : 'check'} /></span>
        <span>{label}</span>
      </label>
      {error && <p id={a.msgId} className="ui-msg ui-msg--error">{error}</p>}
    </div>
  )
})
