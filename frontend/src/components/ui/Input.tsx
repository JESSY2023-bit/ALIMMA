import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react'
import { FieldShell, useFieldA11y, type FieldProps } from './Field'
import { Icon, type IconName } from './Icon'
import { Spinner } from './Spinner'
import { cx } from './utils'

export interface InputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'prefix'>, FieldProps {
  /** Vérification asynchrone en cours (ex. « Vérification de l'opérateur… »). */
  loading?: boolean
  leadingIcon?: IconName
  prefixText?: string
  /** Élément final (ex. bouton œil). Remplace l'icône d'état. */
  trailing?: ReactNode
  wrapperClassName?: string
}

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  {
    label, optional, hint, error, success, loading, leadingIcon, prefixText, trailing,
    id, className, wrapperClassName, disabled, ...rest
  },
  ref,
) {
  const a = useFieldA11y({ id, hint, error, success })
  const state = error ? 'error' : loading ? 'loading' : success ? 'success' : 'default'
  return (
    <FieldShell id={a.id} msgId={a.msgId} label={label} optional={optional} hint={hint} error={error} success={success} className={wrapperClassName}>
      <div className="ui-control" data-state={state} data-disabled={disabled || undefined}>
        {leadingIcon && <Icon name={leadingIcon} className="ui-control__icon" />}
        {prefixText && <span className="ui-control__prefix">{prefixText}</span>}
        <input
          ref={ref}
          id={a.id}
          className={cx('ui-control__input', className)}
          disabled={disabled}
          aria-invalid={error ? true : undefined}
          aria-describedby={a.describedBy}
          aria-busy={loading || undefined}
          {...rest}
        />
        {loading && <Spinner />}
        {!trailing && !loading && error && <Icon name="error" className="ui-control__status--error" />}
        {!trailing && !loading && !error && success && <Icon name="check_circle" className="ui-control__status--success" />}
        {trailing}
      </div>
    </FieldShell>
  )
})
