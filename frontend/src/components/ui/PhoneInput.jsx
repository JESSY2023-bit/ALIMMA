import { forwardRef } from "react";
import { Input } from "./Input";

/** Téléphone Cameroun : préfixe +237 fixe, 9 chiffres (le numéro commence par 6). */
export const PhoneInput = forwardRef(function PhoneInput(
  { label = "Téléphone", placeholder = "6XX XX XX XX", ...rest },
  ref,
) {
  return (
    <Input
      ref={ref}
      type="tel"
      inputMode="numeric"
      autoComplete="tel-national"
      prefixText="+237"
      label={label}
      placeholder={placeholder}
      {...rest}
    />
  );
});
