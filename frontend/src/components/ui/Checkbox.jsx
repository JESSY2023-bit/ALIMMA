import { forwardRef, useEffect, useImperativeHandle, useRef } from "react";
import { Icon } from "./Icon";
import { useFieldA11y } from "./Field";

/** label peut contenir des liens. error : message sous la case. indeterminate : « Tout sélectionner ». */
export const Checkbox = forwardRef(function Checkbox(
  { label, indeterminate = false, error, id, disabled, ...rest },
  ref,
) {
  const inner = useRef(null);
  useImperativeHandle(ref, () => inner.current);
  useEffect(() => {
    if (inner.current) inner.current.indeterminate = indeterminate;
  }, [indeterminate]);
  const a = useFieldA11y({ id, error });
  return (
    <div>
      <label className="ui-check" data-invalid={error ? true : undefined} data-disabled={disabled || undefined}>
        <input
          ref={inner} id={a.id} type="checkbox" className="ui-check__input" disabled={disabled}
          aria-invalid={error ? true : undefined} aria-describedby={a.describedBy} {...rest}
        />
        <span className="ui-check__box"><Icon name={indeterminate ? "remove" : "check"} /></span>
        <span>{label}</span>
      </label>
      {error && <p id={a.msgId} className="ui-msg ui-msg--error">{error}</p>}
    </div>
  );
});
