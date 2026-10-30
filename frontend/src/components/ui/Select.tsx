import { forwardRef, type SelectHTMLAttributes } from 'react'
import { FieldShell, useFieldA11y, type FieldProps } from './Field'
import { Icon, type IconName } from './Icon'
import { cx } from './utils'

export interface SelectOption { value: string; label: string; disabled?: boolean }

export interface SelectProps extends Omit<SelectHTMLAttributes<HTMLSelectElement>, 'children'>, FieldProps {
  options: SelectOption[]
  placeholder?: string
  leadingIcon?: IconName
  wrapperClassName?: string
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(function Select(
  { label, optional, hint, error, success, options, placeholder, leadingIcon, id, className, wrapperClassName, disabled, ...rest },
  ref,
) {
  const a = useFieldA11y({ id, hint, error, success })
  const state = error ? 'error' : success ? 'success' : 'default'
  return (
    <FieldShell id={a.id} msgId={a.msgId} label={label} optional={optional} hint={hint} error={error} success={success} className={wrapperClassName}>
      <div className="ui-control ui-select" data-state={state} data-disabled={disabled || undefined}>
        {leadingIcon && <Icon name={leadingIcon} className="ui-control__icon" />}
        <select
          ref={ref}
          id={a.id}
          className={cx('ui-control__input', className)}
          disabled={disabled}
          aria-invalid={error ? true : undefined}
          aria-describedby={a.describedBy}
          {...rest}
        >
          {placeholder && <option value="" disabled>{placeholder}</option>}
          {options.map((o) => (
            <option key={o.value} value={o.value} disabled={o.disabled}>{o.label}</option>
          ))}
        </select>
        <Icon name="expand_more" className="ui-select__chevron" />
      </div>
    </FieldShell>
  )
})
