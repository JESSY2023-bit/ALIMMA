// src/pages/Profile.jsx — Mon compte (D-014). Desktop : barre latérale + sections. Mobile : accueil du compte puis écrans.
import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { profileSchema, passwordSchema } from "../schemas/profileSchema";
import { useProfile, useUpdateProfile, useChangePassword } from "../hooks/useProfile";
import { useAuthContext } from "../hooks/useAuthContext";
import { useLogout } from "../hooks/useAuth";
import ConfirmModal from "../components/ui/confirmModal";
import AccountMenu from "../components/profile/AccountMenu";
import ReferralCard from "../components/profile/ReferralCard";
import {
  Avatar, Button, EmptyState, FormAlert, Icon, IconButton, Input, Notice, Panel, PasswordInput,
  PasswordStrength, Rating, Switch, useToast,
} from "../components/ui";
import { compressImage } from "../utils/image";
import { applyApiFieldErrors, isNetworkOrServerError } from "../utils/apiErrors";
import { digitsOf } from "../utils/phone";
import { formatDateLong, formatPhoneLocal, memberSince } from "../utils/format";

const TITLES = { infos: "Mes informations", securite: "Mot de passe et sécurité" };

export default function Profile() {
  const navigate = useNavigate();
  const toast = useToast();
  const [params, setParams] = useSearchParams();
  const rawVue = params.get("vue");
  const vue = rawVue === "infos" || rawVue === "securite" ? rawVue : "hub";

  const { user: authUser, setUser, logout } = useAuthContext();
  const { data: profile, isLoading, isError } = useProfile();
  const updateProfile = useUpdateProfile();
  const changePassword = useChangePassword();
  const logoutMutation = useLogout();

  const [logoutOpen, setLogoutOpen] = useState(false);
  const [infoAlert, setInfoAlert] = useState(false);
  const [pwdAlert, setPwdAlert] = useState(false);
  const [photoPreview, setPhotoPreview] = useState(null);
  const [photoData, setPhotoData] = useState(null);
  const [photoError, setPhotoError] = useState("");
  const fileRef = useRef(null);

  const infoForm = useForm({
    resolver: zodResolver(profileSchema),
    mode: "onTouched",
    defaultValues: { nom: "", email: "" },
  });
  const pwdForm = useForm({
    resolver: zodResolver(passwordSchema),
    mode: "onTouched",
    defaultValues: { ancien_mot_de_passe: "", nouveau_mot_de_passe: "", confirm_password: "" },
  });
  const newPassword = pwdForm.watch("nouveau_mot_de_passe");
  const infoDirty = infoForm.formState.isDirty || Boolean(photoData);

  // Hydrate le formulaire quand le profil arrive.
  const { reset: resetInfo } = infoForm;
  useEffect(() => {
    if (profile) {
      resetInfo({ nom: profile.nom || "", email: profile.email || "" });
      setPhotoPreview(profile.photo_url || null);
    }
  }, [profile, resetInfo]);

  // Desktop : « Sécurité » fait défiler jusqu’à la section.
  useEffect(() => {
    if (vue === "securite") document.getElementById("securite")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [vue]);

  const me = profile || authUser;

  /* ---------- Photo ---------- */
  const onPickPhoto = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file) return;
    setPhotoError("");
    if (!["image/jpeg", "image/png"].includes(file.type)) {
      setPhotoError("Format non pris en charge : choisissez une photo JPG ou PNG.");
      return;
    }
    if (file.size > 2 * 1024 * 1024) {
      setPhotoError("Photo trop lourde : 2 Mo maximum. Choisissez une image plus légère.");
      return;
    }
    try {
      const data = await compressImage(file);
      setPhotoData(data);
      setPhotoPreview(data);
    } catch {
      setPhotoError("Impossible de lire cette image. Essayez-en une autre.");
    }
  };

  /* ---------- Informations ---------- */
  const submitInfos = (data) => {
    setInfoAlert(false);
    const payload = { nom: data.nom.trim() };
    if (data.email?.trim()) payload.email = data.email.trim();
    if (photoData) payload.photo_url = photoData;

    updateProfile.mutate(payload, {
      onSuccess: (updated) => {
        if (updated && setUser) setUser(updated);
        setPhotoData(null);
        resetInfo({ nom: updated?.nom ?? payload.nom, email: updated?.email ?? payload.email ?? "" });
        toast.success("Profil mis à jour.");
      },
      onError: (error) => {
        if (applyApiFieldErrors(error, infoForm.setError, infoForm.setFocus)) return;
        if (isNetworkOrServerError(error)) setInfoAlert(true);
        else toast.error(error.response?.data?.message || "Mise à jour impossible. Vérifiez vos informations.");
      },
    });
  };

  const cancelInfos = () => {
    resetInfo({ nom: profile?.nom || "", email: profile?.email || "" });
    setPhotoData(null);
    setPhotoPreview(profile?.photo_url || null);
    setPhotoError("");
  };

  /* ---------- Mot de passe ---------- */
  const submitPassword = (data) => {
    setPwdAlert(false);
    changePassword.mutate(
      { ancien_mot_de_passe: data.ancien_mot_de_passe, nouveau_mot_de_passe: data.nouveau_mot_de_passe },
      {
        onSuccess: () => {
          pwdForm.reset();
          toast.success("Mot de passe modifié.");
        },
        onError: (error) => {
          if (applyApiFieldErrors(error, pwdForm.setError, pwdForm.setFocus, { ancien_mot_de_passe: "ancien_mot_de_passe", nouveau_mot_de_passe: "nouveau_mot_de_passe" })) return;
          if (isNetworkOrServerError(error)) {
            setPwdAlert(true);
          } else {
            pwdForm.setError("ancien_mot_de_passe", { message: error.response?.data?.message || "Mot de passe actuel incorrect." });
            pwdForm.setFocus("ancien_mot_de_passe");
          }
        },
      },
    );
  };

  /* ---------- Déconnexion ---------- */
  const confirmLogout = () => {
    logoutMutation.mutate(undefined, {
      onSettled: () => {
        logout();
        setLogoutOpen(false);
        navigate("/login", { replace: true });
      },
    });
  };

  if (isLoading) return <ProfileSkeleton />;
  if (isError && !me) {
    return (
      <div className="site-wrap page">
        <Panel anchor><EmptyState icon="error" title="Profil indisponible">Impossible de charger votre profil pour le moment. Réessayez dans quelques instants.</EmptyState></Panel>
      </div>
    );
  }

  const counts = { annonces: me?.nb_annonces, enTransit: me?.commandes_en_transit };
  const phoneLocal = formatPhoneLocal(digitsOf(me?.telephone));
  const since = me?.date_inscription;

  return (
    <div className="site-wrap page">
      <div className="profile" data-vue={vue}>
        {/* ===== Desktop : barre latérale ===== */}
        <aside className="profile__side only-desktop">
          <Panel className="profile__sidecard">
            <div className="profile__mini">
              <Avatar size="m" name={me?.nom} src={photoPreview} verified />
              <div>
                <p className="t-label">{me?.nom || "Utilisateur"}</p>
                <Rating value={me?.note_moyenne} count={me?.nb_avis} suffix="" />
              </div>
            </div>
            <AccountMenu variant="side" activeKey={vue === "securite" ? "securite" : "infos"} counts={counts} onLogout={() => setLogoutOpen(true)} />
          </Panel>
        </aside>

        {/* ===== Mobile : accueil du compte ===== */}
        <section className="hub only-mobile" aria-label="Mon compte">
          <header className="hub__head">
            <div className="hub__title">
              <h1>Mon compte</h1>
              <IconButton icon="settings" variant="ghost" className="hub__settings" aria-label="Modifier mes informations" onClick={() => setParams({ vue: "infos" })} />
            </div>
            <div className="hub__id">
              <Avatar size="l" name={me?.nom} src={photoPreview} verified />
              <div>
                <p className="hub__name">{me?.nom}</p>
                <p className="hub__sub">
                  {phoneLocal && `+237 ${phoneLocal}`}{since && ` · membre depuis ${memberSince(since)}`}
                </p>
                <Rating value={me?.note_moyenne} count={me?.nb_avis} suffix="avis reçus" />
              </div>
            </div>
            <Button variant="secondary" fullWidth leadingIcon="edit" className="hub__edit" onClick={() => setParams({ vue: "infos" })}>
              Modifier mes informations
            </Button>
          </header>
          <div className="hub__body">
            <ReferralCard code={me?.code_parrainage} points={me?.points_parrainage} />
            <AccountMenu variant="hub" counts={counts} onLogout={() => setLogoutOpen(true)} />
          </div>
        </section>

        {/* ===== Contenu ===== */}
        <div className="profile__main">
          <div className="profile__bar only-mobile">
            <IconButton icon="arrow_back" variant="ghost" aria-label="Retour au compte" onClick={() => setParams({})} />
            <p>{TITLES[vue]}</p>
          </div>
          <h1 className="t-h1 only-desktop">Mes informations</h1>

          {/* Identité + parrainage */}
          <div className="profile__top" data-section="infos">
            <Panel anchor className="profile-id">
              <Avatar size="xl" name={me?.nom} src={photoPreview} verified />
              <div className="profile-id__info">
                <p className="t-h3 only-desktop">{me?.nom}</p>
                <span className="only-desktop"><Rating value={me?.note_moyenne} count={me?.nb_avis} suffix="avis reçus" /></span>
                {since && <p className="t-petit muted only-desktop">Membre depuis le {formatDateLong(since)}</p>}
                <input ref={fileRef} type="file" accept="image/jpeg,image/png" hidden onChange={onPickPhoto} />
                <Button variant="secondary" leadingIcon="add_a_photo" onClick={() => fileRef.current?.click()}>
                  Changer la photo
                </Button>
                <p className="ui-msg only-mobile">JPG ou PNG, compressée automatiquement.</p>
                {photoError && <p className="ui-msg ui-msg--error" role="alert">{photoError}</p>}
              </div>
            </Panel>
            <ReferralCard className="profile__ref only-desktop" code={me?.code_parrainage} points={me?.points_parrainage} />
          </div>

          {/* Informations personnelles */}
          <Panel className="profile-card" data-section="infos">
            <form noValidate onSubmit={infoForm.handleSubmit(submitInfos)} className="stack stack--lg">
              <div className="profile-card__head">
                <h2 className="t-h3 only-desktop">Informations personnelles</h2>
                {infoDirty && <span className="t-legende muted">Modifications non enregistrées</span>}
              </div>
              {infoAlert && <FormAlert onRetry={infoForm.handleSubmit(submitInfos)} retrying={updateProfile.isPending} />}
              <div className="profile-grid">
                <Input
                  label="Nom complet" autoComplete="name" hint="Affiché sur vos annonces et vos avis."
                  error={infoForm.formState.errors.nom?.message} {...infoForm.register("nom")}
                />
                <Input
                  label="Email" optional type="email" inputMode="email" autoComplete="email"
                  error={infoForm.formState.errors.email?.message} {...infoForm.register("email")}
                />
                <Input
                  label="Téléphone" prefixText="+237" value={phoneLocal} readOnly disabled
                  trailing={<Icon name="lock" className="ui-control__icon" />}
                  hint="Votre identifiant de connexion. Pour le changer, contactez le support."
                />
              </div>
              {since && (
                <p className="profile-since only-mobile"><Icon name="calendar_month" size={20} /> Membre depuis le {formatDateLong(since)}</p>
              )}
              <div className="profile-card__actions">
                <Button variant="tertiary" className="only-desktop" onClick={cancelInfos} disabled={!infoDirty || updateProfile.isPending}>Annuler</Button>
                <Button type="submit" size="lg" className="profile-submit" disabled={!infoDirty} loading={updateProfile.isPending} loadingLabel="Enregistrement…">
                  <span className="only-desktop">Enregistrer les modifications</span>
                  <span className="only-mobile">Enregistrer</span>
                </Button>
              </div>
            </form>
          </Panel>

          {/* Mot de passe et sécurité */}
          <Panel id="securite" className="profile-card" data-section="securite">
            <form noValidate onSubmit={pwdForm.handleSubmit(submitPassword)} className="stack stack--lg">
              <h2 className="t-h3">
                <span className="only-desktop">Mot de passe et sécurité</span>
                <span className="only-mobile">Changer le mot de passe</span>
              </h2>
              {pwdAlert && <FormAlert onRetry={pwdForm.handleSubmit(submitPassword)} retrying={changePassword.isPending} />}
              <div className="profile-grid profile-grid--pwd">
                <PasswordInput
                  label="Mot de passe actuel" autoComplete="current-password" placeholder="••••••••"
                  error={pwdForm.formState.errors.ancien_mot_de_passe?.message} {...pwdForm.register("ancien_mot_de_passe")}
                />
                <PasswordInput
                  label="Nouveau mot de passe" autoComplete="new-password" placeholder="8 caractères, dont 1 chiffre"
                  error={pwdForm.formState.errors.nouveau_mot_de_passe?.message}
                  below={newPassword ? <PasswordStrength value={newPassword} /> : null}
                  {...pwdForm.register("nouveau_mot_de_passe")}
                />
                <PasswordInput
                  label="Confirmation" autoComplete="new-password" placeholder="Saisissez-le à nouveau"
                  error={pwdForm.formState.errors.confirm_password?.message} {...pwdForm.register("confirm_password")}
                />
              </div>
              <div className="profile-card__actions">
                <Button type="submit" variant="secondary" size="lg" className="profile-submit" loading={changePassword.isPending} loadingLabel="Mise à jour…">
                  Mettre à jour le mot de passe
                </Button>
              </div>
            </form>

            <hr className="sep" />
            <div className="stack">
              <h3 className="t-h3 only-mobile">Double vérification</h3>
              <Switch
                disabled className="ui-check--between"
                label={<span className="switch-label"><strong>Code SMS à chaque connexion</strong><small>Bientôt disponible</small></span>}
              />
            </div>
            <Notice variant="warning" icon="shield" className="only-mobile">
              ALIMMA ne vous demandera jamais votre mot de passe ou un code SMS par téléphone ou par WhatsApp.
            </Notice>
          </Panel>
        </div>
      </div>

      <ConfirmModal
        isOpen={logoutOpen}
        title="Se déconnecter ?"
        message="Voulez-vous vraiment vous déconnecter de votre compte ALIMMA ?"
        confirmLabel="Oui, me déconnecter"
        cancelLabel="Annuler"
        onConfirm={confirmLogout}
        onCancel={() => setLogoutOpen(false)}
        isPending={logoutMutation.isPending}
        variant="danger"
      />
    </div>
  );
}

function ProfileSkeleton() {
  return (
    <div className="site-wrap page" aria-busy="true" aria-label="Chargement du profil">
      <div className="profile">
        <div className="profile__side only-desktop"><div className="skeleton" style={{ height: 420, borderRadius: 24 }} /></div>
        <div className="profile__main" style={{ display: "flex" }}>
          <div className="skeleton" style={{ height: 40, width: 260 }} />
          <div className="skeleton" style={{ height: 160, borderRadius: 20 }} />
          <div className="skeleton" style={{ height: 280, borderRadius: 24 }} />
        </div>
      </div>
    </div>
  );
}
