import type { CSSProperties } from 'react'
import { cx } from './utils'

/** Jeu d'icônes D-008 (Material Symbols Rounded). */
export type IconName =
  | 'search' | 'tune' | 'favorite' | 'shopping_bag' | 'person' | 'home' | 'add' | 'chat_bubble'
  | 'notifications' | 'menu' | 'close' | 'arrow_back' | 'chevron_right' | 'expand_more'
  | 'location_on' | 'map' | 'grid_view' | 'view_list' | 'sort' | 'add_a_photo' | 'upload'
  | 'download' | 'edit' | 'delete' | 'pause_circle' | 'visibility' | 'visibility_off' | 'flag'
  | 'share' | 'verified' | 'verified_user' | 'star' | 'workspace_premium' | 'timer' | 'gavel'
  | 'payments' | 'smartphone' | 'local_shipping' | 'inventory_2' | 'qr_code_scanner'
  | 'storefront' | 'bar_chart' | 'sell' | 'group_add' | 'shield' | 'admin_panel_settings'
  | 'wifi_off' | 'error' | 'check_circle' | 'check' | 'remove' | 'lock'
  | (string & {})

export interface IconProps {
  name: IconName
  /** Pleine = état actif ; contour par défaut. */
  filled?: boolean
  size?: number
  className?: string
  /** Si fourni, l'icône est exposée aux lecteurs d'écran. Sinon elle est décorative. */
  label?: string
}

export function Icon({ name, filled = false, size, className, label }: IconProps) {
  const style: CSSProperties = {
    fontVariationSettings: `'FILL' ${filled ? 1 : 0}, 'wght' 400, 'GRAD' 0, 'opsz' 24`,
    ...(size ? { fontSize: size } : null),
  }
  return (
    <span
      className={cx('ui-icon', className)}
      style={style}
      aria-hidden={label ? undefined : true}
      role={label ? 'img' : undefined}
      aria-label={label}
    >
      {name}
    </span>
  )
}
