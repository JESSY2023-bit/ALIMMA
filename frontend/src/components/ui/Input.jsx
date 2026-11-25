import { forwardRef } from "react";
import { FieldShell, useFieldA11y } from "./Field";
import { Icon } from "./Icon";
import { Spinner } from "./Spinner";
import { cx } from "./utils";

/**
 * Champ texte. Props : label, optional, hint, error, success, loading, invalid,
 * leadingIcon, prefixText, trailing, below, labelAction, wrapperClassName + props <input>.
 * invalid : état erreur sans message propre (le message est ailleurs, ex. alerte).
 * valid : état succès (bordure verte + coche) sans message.
 */
export const Input = forwardRef(function Input(
  {
    label, optional, hint, error, success, loading, valid, leadingIcon, prefixText, trailing,
    id, className, wrapperClassName, disabled, invalid, below, labelAction, ...rest
  },
  ref,
) {
  const a = useFieldA11y({ id, hint, error, success });
  const hasError = !!error || !!invalid;
  const state = hasError ? "error" : loading ? "loading" : success || valid ? "success" : "default";
  return (
    <FieldShell
      id={a.id} msgId={a.msgId} label={label} optional={optional} hint={hint} error={error}
      success={success} className={wrapperClassName} below={below} labelAction={labelAction}
    >
      <div className="ui-control" data-state={state} data-disabled={disabled || undefined}>
        {leadingIcon && <Icon name={leadingIcon} className="ui-control__icon" />}
        {prefixText && <span className="ui-control__prefix">{prefixText}</span>}
        <input
          ref={ref}
          id={a.id}
          className={cx("ui-control__input", className)}
          disabled={disabled}
          aria-invalid={hasError ? true : undefined}
          aria-describedby={a.describedBy}
          aria-busy={loading || undefined}
          {...rest}
        />
        {loading && <Spinner />}
        {!trailing && !loading && hasError && <Icon name="error" className="ui-control__status--error" />}
        {!trailing && !loading && !hasError && (success || valid) && <Icon name="check_circle" className="ui-control__status--success" />}
        {trailing}
      </div>
    </FieldShell>
  );
});
