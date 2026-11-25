import { Icon } from "./Icon";

const fr = (n) => String(n).replace(".", ",");

/** Étoiles (demi-étoiles prises en charge). value : 0 à 5. */
export function Stars({ value = 0, size = 16 }) {
  return (
    <span className="ui-stars" role="img" aria-label={`${fr(value)} sur 5`}>
      {[1, 2, 3, 4, 5].map((i) => {
        const full = value >= i;
        const half = !full && value >= i - 0.5;
        return <Icon key={i} name={half ? "star_half" : "star"} filled size={size} className={full || half ? undefined : "is-empty"} />;
      })}
    </span>
  );
}

/** « ★ 4,8 · 126 avis » */
export function Rating({ value, count, suffix = "avis" }) {
  if (value === undefined || value === null || value === "") return null;
  return (
    <span className="ui-rating">
      <Icon name="star" filled size={16} />
      {fr(value)}
      {count !== undefined && count !== null && (
        <span className="ui-rating__count">{suffix ? `· ${count} ${suffix}` : `(${count})`}</span>
      )}
    </span>
  );
}
