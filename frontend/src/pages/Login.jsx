import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema } from "../schemas/authSchema";
import { useLogin, useVerifyOtp } from "../hooks/useAuth";
import { useAuthContext } from "../hooks/useAuthContext";
import AuthLayout from "../layouts/AuthLayout";
import FlowLayout from "../layouts/FlowLayout";
import OtpStep from "../components/auth/OtpStep";
import { Button, Icon, Input, Notice, PasswordInput, useToast } from "../components/ui";
import { maskPhone, normalizeIdentifier } from "../utils/phone";
import { isNetworkOrServerError } from "../utils/apiErrors";

export default function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const toast = useToast();
  const { login } = useAuthContext();
  const loginMutation = useLogin();
  const verifyOtpMutation = useVerifyOtp();

  const [otp, setOtp] = useState(null); // { sessionToken, creds }
  const [otpError, setOtpError] = useState("");
  const [badCredentials, setBadCredentials] = useState(false);

  const { register, handleSubmit, watch, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
    defaultValues: { identifiant: "", password: "" },
  });

  // Dès que la personne corrige un champ, l’erreur globale disparaît.
  const [identifiant, password] = watch(["identifiant", "password"]);
  useEffect(() => setBadCredentials(false), [identifiant, password]);

  const goNext = () => navigate(location.state?.from?.pathname || "/", { replace: true });

  const onSubmit = (data) => {
    const creds = { identifiant: normalizeIdentifier(data.identifiant), password: data.password };
    setBadCredentials(false);
    loginMutation.mutate(creds, {
      onSuccess: (response) => {
        if (response.otp_requis) {
          setOtp({ sessionToken: response.session_token, creds });
        } else {
          login(response);
          goNext();
        }
      },
      onError: (error) => {
        if (isNetworkOrServerError(error)) {
          toast.show("Réseau trop lent. Votre saisie est conservée.", {
            variant: "error",
            duration: 8000,
            action: { label: "Réessayer", onClick: () => handleSubmit(onSubmit)() },
          });
        } else {
          setBadCredentials(true);
        }
      },
    });
  };

  const verifyOtp = (code) => {
    setOtpError("");
    verifyOtpMutation.mutate(
      { session_token: otp.sessionToken, code },
      {
        onSuccess: (response) => {
          login(response);
          goNext();
        },
        onError: (error) =>
          setOtpError(error.response?.data?.message || "Code incorrect. Vérifiez les 6 chiffres reçus par SMS."),
      },
    );
  };

  const resendOtp = () =>
    loginMutation.mutateAsync(otp.creds).then((response) => {
      if (response?.session_token) setOtp((o) => ({ ...o, sessionToken: response.session_token }));
    });

  /* ---------- Étape 2 : code SMS ---------- */
  if (otp) {
    const masked = maskPhone(otp.creds.identifiant);
    return (
      <FlowLayout
        centered
        icon="sms"
        iconTone={otpError ? "error" : undefined}
        title="Vérifions que c’est bien vous"
        onBack={() => { setOtp(null); setOtpError(""); }}
        headerRight={<span className="flow__secure"><Icon name="lock" filled /> Connexion sécurisée</span>}
        subtitle={
          <>
            Nous avons envoyé un code à 6 chiffres par SMS {masked ? <>au <strong>{masked}</strong></> : "au numéro de votre compte"}.{" "}
            <button type="button" className="ui-link" onClick={() => setOtp(null)}>Modifier</button>
          </>
        }
      >
        <OtpStep
          onVerify={verifyOtp}
          onResend={resendOtp}
          verifying={verifyOtpMutation.isPending}
          resending={loginMutation.isPending}
          error={otpError}
          onClearError={() => setOtpError("")}
        />
      </FlowLayout>
    );
  }

  /* ---------- Étape 1 : identifiants ---------- */
  return (
    <AuthLayout
      variant="login"
      closeIcon="close"
      onClose={() => navigate("/")}
      heroTitle="Bon retour !"
      heroText="Connectez-vous pour acheter, vendre et discuter."
      title="Se connecter"
      subtitle={<>Nouveau sur ALIMMA ? <Link to="/register" className="ui-link">Créer un compte</Link></>}
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="stack stack--lg">
        {badCredentials && (
          <Notice variant="error" title="Identifiant ou mot de passe incorrect.">
            Vérifiez le numéro (sans le +237) ou <Link to="/mot-de-passe-oublie">réinitialisez votre mot de passe</Link>.
          </Notice>
        )}

        <Input
          label="Téléphone ou email" leadingIcon="person" autoComplete="username"
          placeholder="670 12 34 56 ou vous@exemple.cm"
          invalid={badCredentials} error={errors.identifiant?.message}
          {...register("identifiant")}
        />

        <PasswordInput
          leadingIcon="lock" placeholder="Votre mot de passe"
          invalid={badCredentials} error={errors.password?.message}
          labelAction={<Link to="/mot-de-passe-oublie" className="ui-link only-desktop">Mot de passe oublié ?</Link>}
          below={<Link to="/mot-de-passe-oublie" className="ui-link auth__forgot only-mobile">Mot de passe oublié ?</Link>}
          {...register("password")}
        />

        <Button type="submit" size="lg" fullWidth loading={loginMutation.isPending} loadingLabel="Connexion…">
          Se connecter
        </Button>

        <Notice variant="neutral" icon="lock" className="only-mobile">
          Ne communiquez jamais votre mot de passe : ALIMMA ne vous le demandera jamais par téléphone ou WhatsApp.
        </Notice>

        <div className="auth__trust only-desktop">
          <span><Icon name="verified_user" filled /> Paiement protégé</span>
          <span><Icon name="local_shipping" filled /> Livraison suivie</span>
        </div>

        <div className="auth__divider only-mobile">Nouveau sur ALIMMA ?</div>
        <Link to="/register" className="ui-btn ui-btn--secondary ui-btn--lg ui-btn--full only-mobile">
          Créer un compte gratuit
        </Link>
        <p className="auth__center">
          <Link to="/" className="ui-link" style={{ fontWeight: 500, textDecoration: "none", color: "inherit" }}>
            <span className="only-mobile">Continuer sans compte</span>
            <span className="only-desktop">Continuer mes achats sans compte</span>
          </Link>
        </p>
      </form>
    </AuthLayout>
  );
}
