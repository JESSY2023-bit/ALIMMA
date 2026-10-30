import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react'

export interface RadioProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type' | 'children'> {
  label: ReactNode
  invalid?: boolean
}

/** À regrouper dans un <fieldset><legend> ; le message d'erreur se place sous le groupe. */
export const Radio = forwardRef<HTMLInputElement, RadioProps>(function Radio({ label, invalid, disabled, ...rest }, ref) {
  return (
    <label className="ui-check" data-invalid={invalid || undefined} data-disabled={disabled || undefined}>
      <input ref={ref} type="radio" className="ui-check__input" disabled={disabled} aria-invalid={invalid || undefined} {...rest} />
      <span className="ui-check__box ui-check__box--radio" />
      <span>{label}</span>
    </label>
  )
})
