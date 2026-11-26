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
      {msg && <p id={msgId} className={`ui-msg ui-msg--${kind}`}>{msg}</p>}
    </div>
  );
}
