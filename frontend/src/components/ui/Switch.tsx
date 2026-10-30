import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react'

export interface SwitchProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'role' | 'children'> {
  label: ReactNode
}

export const Switch = forwardRef<HTMLInputElement, SwitchProps>(function Switch({ label, disabled, ...rest }, ref) {
  return (
    <label className="ui-check" data-disabled={disabled || undefined}>
      <input ref={ref} type="checkbox" role="switch" className="ui-check__input" disabled={disabled} {...rest} />
      <span className="ui-switch__track" />
      <span>{label}</span>
    </label>
  )
})
