import { useState } from "react";
import { Link } from "react-router-dom";
import { Icon } from "./Icon";
import { cx } from "./utils";
import { formatNumber, timeAgo } from "../../utils/format";

/**
 * Carte annonce (coin « ancre »). Le titre est un vrai lien étiré sur toute la carte ;
 * le cœur reste un bouton indépendant (pas d’interactif imbriqué).
 * listing : { id, title, price, image, createdAt, sold }
 */
export function ListingCard({ listing, onToggleFavorite }) {
  const [fav, setFav] = useState(false);
  const { id, title, price, image, createdAt, sold } = listing;
  return (
    <article className={cx("listing", sold && "is-sold")}>
      <div className="listing__media">
        {image ? <img src={image} alt="" loading="lazy" /> : <Icon name="image" size={40} />}
        <button
          type="button" className={cx("listing__fav", fav && "is-on")} aria-pressed={fav}
          aria-label={fav ? "Retirer des favoris" : "Ajouter aux favoris"}
          onClick={() => { setFav((f) => !f); onToggleFavorite?.(id, !fav); }}
        >
          <Icon name="favorite" size={20} filled={fav} />
        </button>
        {sold && <span className="listing__sold">Vendue</span>}
      </div>
      <div className="listing__body">
        <h3 className="listing__title"><Link to={`/annonce/${id}`}>{title}</Link></h3>
        <p className="listing__price">{formatNumber(price)}<small>FCFA</small></p>
        {createdAt && (
          <p className="listing__meta"><Icon name="schedule" size={14} /><span>{timeAgo(createdAt)}</span></p>
        )}
      </div>
    </article>
  );
}
