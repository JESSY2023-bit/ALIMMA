import { forwardRef, type ButtonHTMLAttributes, type ReactNode } from 'react'
import { Icon, type IconName } from './Icon'
import { Spinner } from './Spinner'
import { cx, useDelayedFlag } from './utils'

export type ButtonVariant = 'primary' | 'purchase' | 'secondary' | 'tertiary' | 'danger'
export type ButtonSize = 'lg' | 'md' | 'sm'

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  /** lg = 52 px (action principale mobile) · md = 44 px · sm = 36 px (tableaux desktop). */
  size?: ButtonSize
  /** Envoi en cours : bouton verrouillé (aria-busy), indicateur affiché dès 300 ms. */
  loading?: boolean
  /** Libellé affiché pendant l'envoi (ex. « Création du compte… »). */
  loadingLabel?: ReactNode
  leadingIcon?: IconName
  fullWidth?: boolean
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  {
    variant = 'primary', size = 'md', loading = false, loadingLabel, leadingIcon,
    fullWidth, className, children, onClick, type = 'button', ...rest
  },
  ref,
) {
  const showSpinner = useDelayedFlag(loading, 300)
  return (
    <button
      ref={ref}
      type={type}
      className={cx('ui-btn', `ui-btn--${variant}`, `ui-btn--${size}`, fullWidth && 'ui-btn--full', className)}
      aria-busy={loading || undefined}
      aria-disabled={loading || undefined}
      onClick={(e) => {
        if (loading) { e.preventDefault(); return } // double envoi impossible
        onClick?.(e)
      }}
      {...rest}
    >
      {showSpinner ? <Spinner /> : leadingIcon ? <Icon name={leadingIcon} size={20} /> : null}
      {loading && loadingLabel ? loadingLabel : children}
    </button>
  )
})
