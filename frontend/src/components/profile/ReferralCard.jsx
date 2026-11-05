import { Badge, IconButton, cx, useToast } from "../ui";

/** Carte sombre « Code de parrainage » : copier et partager. */
export default function ReferralCard({ code, points, caption, className }) {
  const toast = useToast();
  if (!code) return null;

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(code);
      toast.success("Code de parrainage copié.");
    } catch {
      toast.error("Impossible de copier le code. Sélectionnez-le et copiez-le à la main.");
    }
  };

  const share = async () => {
    const data = {
      title: "ALIMMA",
      text: `Rejoins-moi sur ALIMMA avec mon code de parrainage ${code}.`,
      url: `${window.location.origin}/register`,
    };
    if (navigator.share) {
      try {
        await navigator.share(data);
      } catch {
        /* partage annulé */
      }
    } else {
      copy();
    }
  };

  return (
    <section className={cx("referral", className)} aria-label="Code de parrainage">
      <div className="referral__top">
        <p className="t-surtitre">Code de parrainage</p>
        {points !== undefined && points !== null && <Badge tone="gold">{new Intl.NumberFormat("fr-FR").format(points)} pts</Badge>}
      </div>
      <div className="referral__row">
        <p className="referral__code">{code}</p>
        <IconButton icon="content_copy" variant="ghost" className="referral__btn referral__btn--dark" aria-label="Copier le code" onClick={copy} />
        <IconButton icon="share" variant="ghost" className="referral__btn referral__btn--gold" aria-label="Partager le code" onClick={share} />
      </div>
      <p className="referral__caption">{caption ?? "Un bonus pour vous deux à chaque premier achat d’un ami parrainé."}</p>
    </section>
  );
}
