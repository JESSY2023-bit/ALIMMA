


import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Icon, cx } from "../ui";
import { CATEGORIES } from "../../config/navigation";

/**
 * Barre de recherche : catégorie + mot-clé + bouton « Rechercher ».
 * Mobile : le sélecteur de catégorie est masqué et le bouton n’affiche que la loupe.
 * Redirige vers /recherche?q=…&categorie=… (route à créer).
 */
export default function SearchBar({ className }) {
  const navigate = useNavigate();
  const [category, setCategory] = useState("");
  const [query, setQuery] = useState("");

  const onSubmit = (e) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (query.trim()) params.set("q", query.trim());
    if (category) params.set("categorie", category);
    navigate(`/recherche?${params.toString()}`);
  };

  return (
    <form role="search" className={cx("search", className)} onSubmit={onSubmit}>
      <div className="search__cat only-desktop">
        <label className="sr-only" htmlFor="search-category">Catégorie</label>
        <select id="search-category" value={category} onChange={(e) => setCategory(e.target.value)}>
          <option value="">Toutes catégories</option>
          {CATEGORIES.map((c) => (
            <option key={c.slug} value={c.slug}>{c.label}</option>
          ))}
        </select>
        <Icon name="expand_more" className="search__chevron" />
      </div>

      <input
        type="search"
        className="search__input"
        aria-label="Rechercher une annonce"
        placeholder="iPhone, frigo, pagne wax, moto…"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        enterKeyHint="search"
      />

      <button type="submit" className="search__btn">
        <Icon name="search" size={22} />
        <span className="only-desktop">Rechercher</span>
        <span className="sr-only only-mobile">Rechercher</span>
      </button>
    </form>
  );
}