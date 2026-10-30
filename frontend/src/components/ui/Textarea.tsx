import { forwardRef, type TextareaHTMLAttributes } from 'react'
import { FieldShell, useFieldA11y, type FieldProps } from './Field'
import { cx } from './utils'

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement>, FieldProps {
  wrapperClassName?: string
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(function Textarea(
  { label, optional, hint, error, success, id, className, wrapperClassName, disabled, rows = 3, ...rest },
  ref,
) {
  const a = useFieldA11y({ id, hint, error, success })
  const state = error ? 'error' : success ? 'success' : 'default'
  return (
    <FieldShell id={a.id} msgId={a.msgId} label={label} optional={optional} hint={hint} error={error} success={success} className={wrapperClassName}>
      <div className="ui-control ui-control--area" data-state={state} data-disabled={disabled || undefined}>
        <textarea
          ref={ref}
          id={a.id}
          rows={rows}
          className={cx('ui-control__input', className)}
          disabled={disabled}
          aria-invalid={error ? true : undefined}
          aria-describedby={a.describedBy}
          {...rest}
        />
      </div>
    </FieldShell>
  )
})
