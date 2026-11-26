import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { forgotPhoneSchema, newPasswordSchema } from "../schemas/authSchema";
import { useForgotPassword, useResetPassword, useVerifyResetCode } from "../hooks/usePasswordReset";
import FlowLayout from "../layouts/FlowLayout";
import OtpStep from "../components/auth/OtpStep";
import { Button, FormAlert, Icon, PasswordInput, PasswordStrength, PhoneInput } from "../components/ui";
import { maskPhone, toE164 } from "../utils/phone";
import { applyApiFieldErrors, isNetworkOrServerError } from "../utils/apiErrors";

const STEPS = ["Numéro", "Code", "Nouveau mot de passe", "Terminé"];

export default function ForgotPassword() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [telephone, setTelephone] = useState("");
  const [resetToken, setResetToken] = useState("");
  const [codeError, setCodeError] = useState("");
  const [serverError, setServerError] = useState(false);
  const [sameAsOld, setSameAsOld] = useState(false);

  const forgot = useForgotPassword();
  const verify = useVerifyResetCode();
  const reset = useResetPassword();

  const phoneForm = useForm({ resolver: zodResolver(forgotPhoneSchema), defaultValues: { telephone: "" } });
  const pwdForm = useForm({
    resolver: zodResolver(newPasswordSchema),
    mode: "onTouched",
    defaultValues: { password: "", confirmPassword: "" },
  });
  const password = pwdForm.watch("password");
  const confirm = pwdForm.watch("confirmPassword");

  const goTo = (n) => { setServerError(false); setStep(n); };
  const back = () => (step === 1 ? navigate("/login") : goTo(step - 1));

  /* 1 · Numéro */
  const submitPhone = (data) => {
    setServerError(false);
    const e164 = toE164(data.telephone);
    forgot.mutate(e164, {
      onSuccess: () => { setTelephone(e164); goTo(2); },
      onError: (error) => {
        if (applyApiFieldErrors(error, phoneForm.setError, phoneForm.setFocus)) return;
        if (error.response?.status === 404) {
          phoneForm.setError("telephone", { message: "Aucun compte ALIMMA avec ce numéro. Vérifiez-le ou créez un compte." });
        } else if (isNetworkOrServerError(error)) setServerError(true);
      },
    });
  };

  /* 2 · Code */
  const submitCode = (code) => {
    setCodeError("");
    verify.mutate({ telephone, code }, {
      onSuccess: (res) => { setResetToken(res.reset_token); goTo(3); },
      onError: (error) =>
        setCodeError(error.response?.data?.message || "Code incorrect. Vérifiez les 6 chiffres reçus par SMS."),
    });
  };

  /* 3 · Nouveau mot de passe */
  const submitPassword = (data) => {
    setServerError(false);
    setSameAsOld(false);
    reset.mutate({ reset_token: resetToken, password: data.password }, {
      onSuccess: () => goTo(4),
      onError: (error) => {
        if (applyApiFieldErrors(error, pwdForm.setError, pwdForm.setFocus)) {
          if (error.response?.data?.errors?.password) setSameAsOld(true);
          return;
        }
        if (isNetworkOrServerError(error)) setServerError(true);
      },
    });
  };

  const common = { steps: STEPS, step, onBack: step < 4 ? back : undefined };

  if (step === 1) {
    return (
      <FlowLayout {...common} icon="lock_reset" title="Mot de passe oublié ?"
        subtitle="Pas de souci. Saisissez le numéro de votre compte : nous vous envoyons un code par SMS.">
        <form className="flow__form" noValidate onSubmit={phoneForm.handleSubmit(submitPhone)}>
          <div className="flow__content stack">
            {serverError && <FormAlert onRetry={phoneForm.handleSubmit(submitPhone)} retrying={forgot.isPending} />}
            <PhoneInput autoFocus error={phoneForm.formState.errors.telephone?.message} {...phoneForm.register("telephone")} />
          </div>
          <div className="flow__actions">
            <Button type="submit" size="lg" fullWidth loading={forgot.isPending} loadingLabel="Envoi du code…">
              Recevoir le code
            </Button>
            <p className="auth__center">
              Vous vous en souvenez ? <Link to="/login" className="ui-link">Se connecter</Link>
            </p>
          </div>
        </form>
      </FlowLayout>
    );
  }

  if (step === 2) {
    const masked = maskPhone(telephone);
    return (
      <FlowLayout {...common} centered icon="sms" iconTone={codeError ? "error" : undefined} title="Entrez le code à 6 chiffres"
        subtitle={<>Envoyé au <strong>{masked ?? telephone}</strong>.</>}>
        <OtpStep
          submitLabel="Vérifier"
          onVerify={submitCode}
          onResend={() => forgot.mutateAsync(telephone)}
          verifying={verify.isPending}
          resending={forgot.isPending}
          error={codeError}
          onClearError={() => setCodeError("")}
        />
      </FlowLayout>
    );
  }

  if (step === 3) {
    const { errors, touchedFields } = pwdForm.formState;
    const rules = [
      { label: "8 caractères minimum", ok: password.length >= 8 },
      { label: "Au moins 1 chiffre", ok: /\d/.test(password) },
      { label: "Différent de l’ancien mot de passe", ok: password.length > 0 && !sameAsOld },
    ];
    const matches = touchedFields.confirmPassword && confirm && confirm === password;
    return (
      <FlowLayout {...common} title="Choisissez un nouveau mot de passe"
        subtitle={<>Pour le compte {maskPhone(telephone) ?? telephone}. Il remplacera l’ancien sur tous vos appareils.</>}>
        <form className="flow__form" noValidate onSubmit={pwdForm.handleSubmit(submitPassword)}>
          <div className="flow__content stack stack--lg">
            {serverError && <FormAlert onRetry={pwdForm.handleSubmit(submitPassword)} retrying={reset.isPending} />}
            <PasswordInput
              label="Nouveau mot de passe" autoComplete="new-password" autoFocus
              error={errors.password?.message}
              below={password ? <PasswordStrength value={password} rules={rules} /> : null}
              {...pwdForm.register("password")}
            />
            <PasswordInput
              label="Confirmez le mot de passe" autoComplete="new-password"
              error={errors.confirmPassword?.message}
              success={matches ? "Les deux mots de passe correspondent." : undefined}
              {...pwdForm.register("confirmPassword")}
            />
          </div>
          <div className="flow__actions">
            <Button type="submit" size="lg" fullWidth loading={reset.isPending} loadingLabel="Enregistrement…">
              Enregistrer le mot de passe
            </Button>
          </div>
        </form>
      </FlowLayout>
    );
  }

  return (
    <FlowLayout {...common}>
      <div className="flow__done">
        <span className="flow__done-badge"><Icon name="check_circle" filled /></span>
        <h1 className="flow__title">Mot de passe modifié</h1>
        <p className="flow__sub">
          Vous pouvez maintenant vous connecter avec votre nouveau mot de passe. Par sécurité, vos autres appareils ont été déconnectés.
        </p>
      </div>
      <div className="flow__actions">
        <Button size="lg" fullWidth onClick={() => navigate("/login")}>Se connecter</Button>
      </div>
    </FlowLayout>
  );
}
