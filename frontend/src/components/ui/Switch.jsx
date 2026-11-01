import { forwardRef } from "react";

export const Switch = forwardRef(function Switch({ label, disabled, ...rest }, ref) {
  return (
    <label className="ui-check" data-disabled={disabled || undefined}>
      <input ref={ref} type="checkbox" role="switch" className="ui-check__input" disabled={disabled} {...rest} />
      <span className="ui-switch__track" />
      <span>{label}</span>
    </label>
  );
});
