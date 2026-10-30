import { forwardRef, useState } from 'react'
import { Icon } from './Icon'
import { Input, type InputProps } from './Input'

export const PasswordInput = forwardRef<HTMLInputElement, Omit<InputProps, 'type' | 'trailing'>>(
  function PasswordInput({ label = 'Mot de passe', autoComplete = 'current-password', ...rest }, ref) {
    const [visible, setVisible] = useState(false)
    return (
      <Input
        ref={ref}
        type={visible ? 'text' : 'password'}
        label={label}
        autoComplete={autoComplete}
        trailing={
          <button
            type="button"
            className="ui-control__btn"
            onClick={() => setVisible((v) => !v)}
            aria-label={visible ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
            aria-pressed={visible}
            disabled={rest.disabled}
          >
            <Icon name={visible ? 'visibility_off' : 'visibility'} size={20} />
          </button>
        }
        {...rest}
      />
    )
  },
)
