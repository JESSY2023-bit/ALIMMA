import { useState } from "react";
import { Button, Icon, Notice, OtpInput } from "../ui";
import { formatMMSS, formatMSS, useCountdown } from "../../hooks/useCountdown";

/**
 * Saisie du code SMS : 6 cases, validation automatique au 6e chiffre, expiration (5 min),
 * renvoi après 45 s. À placer dans <FlowLayout>.
 *  onVerify(code) · onResend() → Promise · verifying · resending
 *  error : message d’erreur renvoyé par l’API (code incorrect) · onClearError()
 */
export default function OtpStep({
  onVerify, onResend, verifying, resending, error, onClearError,
  submitLabel = "Valider", verifyingLabel = "Vérification en cours…", expireSeconds = 300, resendSeconds = 45,
}) {
  const [code, setCode] = useState("");
  const [resendError, setResendError] = useState("");
  const [expiresIn, resetExpire] = useCountdown(expireSeconds);
  const [cooldown, resetCooldown] = useCountdown(resendSeconds);
  const expired = expiresIn <= 0;

  const message = expired
    ? "Ce code a expiré. Les codes sont valables 5 minutes. Demandez-en un nouveau : il arrivera en quelques secondes."
    : error || resendError;

  const submit = (value) => {
    if (value.length === 6 && !expired && !verifying) onVerify(value);
  };

  const resend = async () => {
    setResendError("");
    try {
      await onResend();
      setCode("");
      onClearError?.();
      resetExpire(expireSeconds);
      resetCooldown(resendSeconds);
    } catch {
      setResendError("Impossible d’envoyer le code pour le moment. Réessayez dans quelques instants.");
    }
  };

  return (
    <>
      <div className="flow__content">
        <OtpInput
          value={code}
          onChange={(v) => {
            setCode(v);
            setResendError("");
            onClearError?.();
          }}
          onComplete={submit}
          invalid={Boolean(message)}
          disabled={verifying || expired}
          autoFocus
        />
        {message && <Notice variant="error" className="mt-4">{message}</Notice>}
        {!expired && (
          <p className="otp-meta">
            <span>
              <Icon name="timer" /> Le code expire dans <strong>{formatMMSS(expiresIn)}</strong>
            </span>
            <button type="button" className="ui-link" disabled={cooldown > 0 || resending} onClick={resend}>
              Renvoyer le code{cooldown > 0 ? ` (${formatMSS(cooldown)})` : ""}
            </button>
          </p>
        )}
        {!expired && <p className="auth__note" style={{ marginTop: 16 }}>Vous pouvez coller le code reçu : il se répartit tout seul dans les 6 cases.</p>}
        {message && (
          <Notice variant="info" icon="help" className="mt-4">
            Pas de SMS ? Vérifiez que votre téléphone a du réseau et que le numéro est le bon. Le SMS peut prendre jusqu’à 1 minute.
          </Notice>
        )}
      </div>
      <div className="flow__actions">
        {expired ? (
          <Button size="lg" fullWidth leadingIcon="refresh" loading={resending} onClick={resend}>
            Renvoyer un code
          </Button>
        ) : (
          <Button
            size="lg" fullWidth disabled={code.length < 6} loading={verifying}
            loadingLabel={verifyingLabel} onClick={() => submit(code)}
          >
            {submitLabel}
          </Button>
        )}
      </div>
    </>
  );
}
