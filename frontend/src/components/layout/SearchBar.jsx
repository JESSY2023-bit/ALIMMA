// import { useState } from "react";
// import { FaChevronDown, FaSearch } from "react-icons/fa";

// export default function SearchBar() {
//   const [category, setCategory] = useState("Toutes les catégories");
//   const [searchQuery, setSearchQuery] = useState("");

//   const handleSearch = (e) => {
//     e.preventDefault();
//   };

//   return (
//     <div className="bg-primary py-3 px-4 sm:px-6 w-full clear-both">
//       <div className="max-w-7xl mx-auto flex items-center">
//         <form onSubmit={handleSearch} className="w-full max-w-xl">
//           <div className="bg-white rounded-full flex items-center w-full overflow-hidden px-4 py-1.5 shadow-sm">
            
//             {/* Dropdown Catégories */}
//             <div className="relative flex items-center pr-3 border-r border-gray-200 shrink-0">
//               <select
//                 value={category}
//                 onChange={(e) => setCategory(e.target.value)}
//                 className="bg-transparent text-gray-800 text-xs font-semibold border-none focus:outline-none pr-4 cursor-pointer appearance-none p-0 focus:ring-0"
//               >
//                 <option value="Toutes les catégories">Toutes les catégories</option>
//                 <option value="Alimentation">Alimentation</option>
//                 <option value="Électronique">Électronique</option>
//               </select>
//               <FaChevronDown className="text-[9px] text-gray-400 pointer-events-none absolute right-0" />
//             </div>

//             {/* Input Texte */}
//             <input
//               type="text"
//               placeholder="Rechercher quoi que ce soit..."
//               value={searchQuery}
//               onChange={(e) => setSearchQuery(e.target.value)}
//               className="w-full border-none px-3 py-1 text-xs text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-0"
//             />

//             {/* Bouton Loupe */}
//             <button
//               type="submit"
//               className="pl-2 text-gray-800 text-primary-hover transition cursor-pointer"
//               aria-label="Rechercher"
//             >
//               <FaSearch className="text-xs" />
//             </button>
//           </div>
//         </form>
//       </div>
//     </div>
//   );
// }


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