import { createContext, useCallback, useContext, useMemo, useRef, useState } from "react";
import { Icon } from "./Icon";

const ToastContext = createContext(null);

/**
 * Enveloppe l’application : <ToastProvider><App /></ToastProvider>. Visible 4 s, fermable.
 * toast.success(msg) · toast.error(msg) · toast.show(msg, { variant, duration, action: { label, onClick } })
 */
export function ToastProvider({ children, duration = 4000 }) {
  const [items, setItems] = useState([]);
  const counter = useRef(0);

  const dismiss = useCallback((id) => setItems((t) => t.filter((x) => x.id !== id)), []);

  const show = useCallback(
    (message, options = {}) => {
      const id = ++counter.current;
      setItems((t) => [...t, { id, message, variant: options.variant ?? "success", action: options.action }]);
      window.setTimeout(() => dismiss(id), options.duration ?? duration);
      return id;
    },
    [dismiss, duration],
  );

  const api = useMemo(
    () => ({
      show,
      success: (m) => show(m, { variant: "success" }),
      error: (m) => show(m, { variant: "error" }),
      dismiss,
    }),
    [show, dismiss],
  );

  return (
    <ToastContext.Provider value={api}>
      {children}
      <div className="ui-toast-region">
        {items.map((t) => (
          <div key={t.id} className="ui-toast" data-variant={t.variant} role={t.variant === "error" ? "alert" : "status"}>
            <Icon name={t.variant === "error" ? "error" : "check_circle"} filled />
            <span className="ui-toast__text">{t.message}</span>
            {t.action && (
              <button
                type="button"
                className="ui-toast__action"
                onClick={() => {
                  t.action.onClick();
                  dismiss(t.id);
                }}
              >
                {t.action.label}
              </button>
            )}
            <button type="button" className="ui-toast__close" aria-label="Fermer la notification" onClick={() => dismiss(t.id)}>
              <Icon name="close" size={18} />
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error("useToast doit être utilisé dans <ToastProvider>.");
  return ctx;
}
