import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from 'react'
import { Icon } from './Icon'

type Variant = 'success' | 'error' | 'info'
interface ToastItem { id: number; message: ReactNode; variant: Variant }
interface ShowOptions { variant?: Variant; duration?: number }

interface ToastApi {
  show: (message: ReactNode, options?: ShowOptions) => number
  success: (message: ReactNode) => number
  error: (message: ReactNode) => number
  dismiss: (id: number) => void
}

const ToastContext = createContext<ToastApi | null>(null)

/** Enveloppe l'application : <ToastProvider><App /></ToastProvider>. Visible 4 s, fermable. */
export function ToastProvider({ children, duration = 4000 }: { children: ReactNode; duration?: number }) {
  const [items, setItems] = useState<ToastItem[]>([])
  const counter = useRef(0)

  const dismiss = useCallback((id: number) => setItems((t) => t.filter((x) => x.id !== id)), [])

  const show = useCallback<ToastApi['show']>((message, options = {}) => {
    const id = ++counter.current
    setItems((t) => [...t, { id, message, variant: options.variant ?? 'success' }])
    window.setTimeout(() => dismiss(id), options.duration ?? duration)
    return id
  }, [dismiss, duration])

  const api = useMemo<ToastApi>(() => ({
    show,
    success: (m) => show(m, { variant: 'success' }),
    error: (m) => show(m, { variant: 'error' }),
    dismiss,
  }), [show, dismiss])

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="ui-toast-region">
        {items.map((t) => (
          <div key={t.id} className="ui-toast" data-variant={t.variant} role={t.variant === 'error' ? 'alert' : 'status'}>
            <Icon name={t.variant === 'error' ? 'error' : 'check_circle'} filled />
            <span className="ui-toast__text">{t.message}</span>
            <button type="button" className="ui-toast__close" aria-label="Fermer la notification" onClick={() => dismiss(t.id)}>
              <Icon name="close" size={18} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast(): ToastApi {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast doit être utilisé dans <ToastProvider>.')
  return ctx
}
