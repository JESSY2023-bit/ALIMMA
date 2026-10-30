import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { Icon, type IconName } from './Icon'
import { cx } from './utils'

export interface IconButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'aria-label' | 'children'> {
  icon: IconName
  /** Obligatoire : un bouton icône seule n'a pas de texte visible. */
  'aria-label': string
  variant?: 'outline' | 'ghost'
  filled?: boolean
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(function IconButton(
  { icon, variant = 'outline', filled, className, type = 'button', ...rest },
  ref,
) {
  return (
    <button ref={ref} type={type} className={cx('ui-iconbtn', variant === 'ghost' && 'ui-iconbtn--ghost', className)} {...rest}>
      <Icon name={icon} filled={filled} size={20} />
    </button>
  )
})
