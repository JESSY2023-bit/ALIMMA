import { useId } from "react";

/** Génère les identifiants d’accessibilité d’un champ (label, message, aria-describedby). */
export function useFieldA11y({ id, hint, error, success }) {
  const auto = useId();
  const base = id ?? auto;
  const msgId = `${base}-msg`;
  return { id: base, msgId, describedBy: error || success || hint ? msgId : undefined };
}

/**
 * Enveloppe commune des champs : libellé, message (erreur > succès > aide).
 * below : contenu sous le champ (ex. jauge) · labelAction : action à droite du libellé.
 */
export function FieldShell({ id, msgId, label, optional, hint, error, success, className, below, labelAction, children }) {
  const msg = error ?? success ?? hint;
  const kind = error ? "error" : success ? "success" : "hint";
  return (
    <div className={className ? `ui-field ${className}` : "ui-field"}>
      {(label || labelAction) && (
        <div className="ui-field__row">
          {label && (
            <label className="ui-label" htmlFor={id}>
              {label} {optional && <span className="ui-label__opt">(facultatif)</span>}
            </label>
          )}
          {labelAction}
        </div>
      )}
      {children}
      {below}
      {msg && (
        <p id={msgId} className={`ui-msg ui-msg--${kind}`}>
          {msg}
        </p>
      )}
    </div>
  );
}
