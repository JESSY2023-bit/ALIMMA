import { useRef } from "react";

/**
 * Saisie de code à usage unique : une case par chiffre, collage et auto-remplissage SMS pris en charge.
 * Props : value, onChange(value), onComplete(value), length=6, invalid, disabled, autoFocus, label
 */
export function OtpInput({ value, onChange, onComplete, length = 6, invalid, disabled, autoFocus, label = "Code reçu par SMS" }) {
  const refs = useRef([]);
  const digits = Array.from({ length }, (_, i) => value[i] ?? "");

  const commit = (next, focusIndex) => {
    const clean = next.replace(/\D/g, "").slice(0, length);
    onChange(clean);
    if (focusIndex !== undefined) refs.current[Math.min(focusIndex, length - 1)]?.focus();
    if (clean.length === length) onComplete?.(clean);
  };

  const onInput = (i, raw) => {
    const d = raw.replace(/\D/g, "");
    if (!d) return;
    if (d.length > 1) return commit(value.slice(0, i) + d, i + d.length); // auto-remplissage SMS
    const arr = digits.slice();
    arr[i] = d;
    return commit(arr.join(""), i + 1);
  };

  const onKeyDown = (i, e) => {
    if (e.key === "Backspace") {
      e.preventDefault();
      if (digits[i]) {
        const arr = digits.slice();
        arr[i] = "";
        commit(arr.join(""));
      } else if (i > 0) {
        const arr = digits.slice();
        arr[i - 1] = "";
        commit(arr.join(""), i - 1);
      }
    } else if (e.key === "ArrowLeft" && i > 0) refs.current[i - 1]?.focus();
    else if (e.key === "ArrowRight" && i < length - 1) refs.current[i + 1]?.focus();
  };

  const onPaste = (e) => {
    e.preventDefault();
    const text = e.clipboardData.getData("text");
    commit(text, text.replace(/\D/g, "").length);
  };

  return (
    <div className="otp" role="group" aria-label={label} data-invalid={invalid || undefined}>
      {digits.map((d, i) => (
        <input
          key={i}
          ref={(el) => { refs.current[i] = el; }}
          className="otp__cell"
          data-filled={d ? true : undefined}
          value={d}
          inputMode="numeric"
          pattern="[0-9]*"
          maxLength={i === 0 ? length : 1}
          autoComplete={i === 0 ? "one-time-code" : "off"}
          autoFocus={autoFocus && i === 0}
          disabled={disabled}
          aria-label={`Chiffre ${i + 1} sur ${length}`}
          aria-invalid={invalid || undefined}
          onChange={(e) => onInput(i, e.target.value)}
          onKeyDown={(e) => onKeyDown(i, e)}
          onPaste={onPaste}
          onFocus={(e) => e.target.select()}
        />
      ))}
    </div>
  );
}
