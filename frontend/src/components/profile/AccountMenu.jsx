import { Link } from "react-router-dom";
import { Badge, Icon, Panel } from "../ui";

// Pages à créer au fur et à mesure (elles afficheront la 404 en attendant).
const SIDE_ITEMS = [
  { key: "infos", label: "Mes informations", icon: "person", to: "/profile?vue=infos" },
  { key: "annonces", label: "Mes annonces", icon: "inventory_2", to: "/mes-annonces", count: "annonces" },
  { key: "commandes", label: "Mes commandes", icon: "receipt_long", to: "/mes-commandes" },
  { key: "favoris", label: "Favoris", icon: "favorite", to: "/favoris" },
  { key: "alertes", label: "Mes alertes", icon: "notifications_active", to: "/alertes" },
  { key: "parrainage", label: "Parrainage", icon: "group_add", to: "/parrainage" },
  { key: "securite", label: "Sécurité", icon: "lock", to: "/profile?vue=securite" },
];

const HUB_GROUPS = [
  [
    { key: "annonces", label: "Mes annonces", icon: "inventory_2", to: "/mes-annonces", count: "annonces" },
    { key: "commandes", label: "Mes commandes", icon: "receipt_long", to: "/mes-commandes", transit: true },
    { key: "favoris", label: "Favoris", icon: "favorite", to: "/favoris" },
    { key: "alertes", label: "Mes alertes", icon: "notifications_active", to: "/alertes" },
    { key: "avis", label: "Avis reçus", icon: "star", to: "/avis" },
  ],
  [
    { key: "securite", label: "Mot de passe et sécurité", icon: "lock", to: "/profile?vue=securite" },
    { key: "aide", label: "Aide et CGU", icon: "help", to: "/aide" },
  ],
];

function Item({ item, active, variant, counts }) {
  const count = item.count ? counts[item.count] : null;
  return (
    <Link to={item.to} className="acct__item" aria-current={active ? "page" : undefined}>
      <Icon name={item.icon} size={20} filled={active} />
      <span className="acct__label">{item.label}</span>
      {count ? <Badge tone="neutral">{count}</Badge> : null}
      {item.transit && counts.enTransit ? <Badge tone="info" icon="local_shipping">{counts.enTransit} en transit</Badge> : null}
      {active && variant === "side" ? <span className="acct__dot" aria-hidden="true" /> : null}
      {variant === "hub" ? <Icon name="chevron_right" className="acct__chev" size={20} /> : null}
    </Link>
  );
}

function Logout({ onLogout }) {
  return (
    <button type="button" className="acct__item acct__item--danger" onClick={onLogout}>
      <Icon name="logout" size={20} />
      <span className="acct__label">Se déconnecter</span>
    </button>
  );
}

/**
 * Menu du compte.
 *  variant "side" : barre latérale desktop (élément actif surligné)
 *  variant "hub" : liste mobile en deux groupes
 *  counts : { annonces, enTransit } (affichés seulement s’ils existent)
 */
export default function AccountMenu({ variant = "side", activeKey, counts = {}, onLogout }) {
  if (variant === "hub") {
    return (
      <nav aria-label="Mon compte" className="acct acct--hub">
        {HUB_GROUPS.map((group, i) => (
          <Panel key={i} className="acct__group">
            {group.map((item) => (
              <Item key={item.key} item={item} variant="hub" counts={counts} />
            ))}
            {i === HUB_GROUPS.length - 1 && <Logout onLogout={onLogout} />}
          </Panel>
        ))}
      </nav>
    );
  }
  return (
    <nav aria-label="Mon compte" className="acct acct--side">
      {SIDE_ITEMS.map((item) => (
        <Item key={item.key} item={item} active={item.key === activeKey} variant="side" counts={counts} />
      ))}
      <hr className="sep acct__sep" />
      <Logout onLogout={onLogout} />
    </nav>
  );
}
