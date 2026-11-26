import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { registerSchema } from "../schemas/authSchema";
import { useRegister } from "../hooks/useAuth";
import AuthLayout from "../layouts/AuthLayout";
import {
  Button, Checkbox, FormAlert, Icon, Input, Notice, PasswordInput, PasswordStrength, PhoneInput, useToast,
} from "../components/ui";
import { toE164 } from "../utils/phone";
import { applyApiFieldErrors, isNetworkOrServerError } from "../utils/apiErrors";

export default function Register() {
  const navigate = useNavigate();
  const toast = useToast();
  const registerMutation = useRegister();
  const [banner, setBanner] = useState(null); // { type: "conflict" | "server" | "message", message? }
  const [showReferral, setShowReferral] = useState(false);

  const {
    register, handleSubmit, setError, setFocus, watch,
    formState: { errors, touchedFields },
  } = useForm({
    resolver: zodResolver(registerSchema),
    mode: "onTouched",
    defaultValues: { nom: "", telephone: "", email: "", password: "", codeParrainage: "", cgu: false },
  });

  const password = watch("password");
  const isOk = (name) => Boolean(touchedFields[name] && !errors[name] && watch(name));

  const onSubmit = (data) => {
    setBanner(null);
    const payload = { nom: data.nom.trim(), telephone: toE164(data.telephone), password: data.password };
    if (data.email) payload.email = data.email.trim();
    if (data.codeParrainage) payload.code_parrainage = data.codeParrainage.trim();

    registerMutation.mutate(payload, {
      onSuccess: () => {
        toast.success(`Compte créé. Bienvenue sur ALIMMA, ${payload.nom.split(" ")[0]} !`);
        navigate("/login");
      },
      onError: (error) => {
        if (applyApiFieldErrors(error, setError, setFocus, { code_parrainage: "codeParrainage" })) {
          if (error.response?.data?.errors?.code_parrainage) setShowReferral(true);
          return;
        }
        if (error.response?.status === 409) setBanner({ type: "conflict" });
        else if (isNetworkOrServerError(error)) setBanner({ type: "server" });
        else setBanner({ type: "message", message: error.response?.data?.message || "Inscription impossible. Vérifiez vos informations." });
      },
    });
  };

  return (
    <AuthLayout
      variant="register"
      heroTitle="Créez votre compte"
      heroText="Gratuit. Achetez, vendez et suivez vos commandes."
      title="Créer un compte"
      subtitle={<>Déjà inscrit ? <Link to="/login" className="ui-link">Se connecter</Link></>}
    >
      <form onSubmit={handleSubmit(onSubmit)} noValidate className="stack stack--lg">
        {banner?.type === "server" && <FormAlert onRetry={handleSubmit(onSubmit)} retrying={registerMutation.isPending} />}
        {banner?.type === "conflict" && (
          <Notice variant="error">
            Ce numéro a déjà un compte ALIMMA. <Link to="/login">Se connecter</Link> ou{" "}
            <Link to="/mot-de-passe-oublie">réinitialiser le mot de passe</Link>.
          </Notice>
        )}
        {banner?.type === "message" && <Notice variant="error">{banner.message}</Notice>}

        <Input
          label="Nom complet" placeholder="Ex. : Aïcha Ngono" autoComplete="name"
          error={errors.nom?.message} valid={isOk("nom")}
          {...register("nom")}
        />

        <PhoneInput
          hint="Obligatoire : il sert d’identifiant de connexion et pour vos livraisons."
          error={errors.telephone?.message} valid={isOk("telephone")}
          {...register("telephone")}
        />

        <Input
          label="Email" optional type="email" inputMode="email" autoComplete="email" placeholder="vous@exemple.cm"
          error={errors.email?.message} valid={isOk("email")}
          {...register("email")}
        />

        <PasswordInput
          label="Mot de passe" autoComplete="new-password" placeholder="8 caractères minimum, dont 1 chiffre"
          error={errors.password?.message}
          below={password ? <PasswordStrength value={password} /> : null}
          {...register("password")}
        />

        {showReferral || watch("codeParrainage") ? (
          <Input
            label="Code de parrainage" optional leadingIcon="redeem" placeholder="EX. : PAUL-E7K2" autoCapitalize="characters"
            hint="Un bonus pour vous et votre parrain à votre premier achat."
            error={errors.codeParrainage?.message}
            {...register("codeParrainage")}
          />
        ) : (
          <Button
            variant="tertiary" size="sm" className="auth__disclosure" leadingIcon="redeem"
            aria-expanded="false" onClick={() => setShowReferral(true)}
          >
            J’ai un code de parrainage <Icon name="expand_more" size={20} />
          </Button>
        )}

        <Checkbox
          error={errors.cgu?.message}
          label={
            <>
              J’accepte les <Link to="/cgu" target="_blank" className="ui-link">CGU</Link> et la{" "}
              <Link to="/confidentialite" target="_blank" className="ui-link">politique de confidentialité</Link>
            </>
          }
          {...register("cgu")}
        />

        <Button type="submit" size="lg" fullWidth loading={registerMutation.isPending} loadingLabel="Création du compte…">
          Créer mon compte
        </Button>

        <p className="auth__center only-mobile">
          Déjà inscrit ? <Link to="/login" className="ui-link">Se connecter</Link>
        </p>
        <p className="auth__note only-desktop">Votre compte est actif immédiatement : aucun code à saisir.</p>
      </form>
    </AuthLayout>
  );
}
