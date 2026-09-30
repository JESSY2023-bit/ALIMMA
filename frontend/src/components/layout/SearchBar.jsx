import { useState } from "react";
import { FaChevronDown, FaSearch } from "react-icons/fa";

export default function SearchBar() {
  const [category, setCategory] = useState("Toutes les catégories");
  const [searchQuery, setSearchQuery] = useState("");

  const handleSearch = (e) => {
    e.preventDefault();
  };

  return (
    <div className="bg-primary py-3 px-4 sm:px-6 w-full clear-both">
      <div className="max-w-7xl mx-auto flex items-center">
        <form onSubmit={handleSearch} className="w-full max-w-xl">
          <div className="bg-white rounded-full flex items-center w-full overflow-hidden px-4 py-1.5 shadow-sm">
            
            {/* Dropdown Catégories */}
            <div className="relative flex items-center pr-3 border-r border-gray-200 shrink-0">
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="bg-transparent text-gray-800 text-xs font-semibold border-none focus:outline-none pr-4 cursor-pointer appearance-none p-0 focus:ring-0"
              >
                <option value="Toutes les catégories">Toutes les catégories</option>
                <option value="Alimentation">Alimentation</option>
                <option value="Électronique">Électronique</option>
              </select>
              <FaChevronDown className="text-[9px] text-gray-400 pointer-events-none absolute right-0" />
            </div>

            {/* Input Texte */}
            <input
              type="text"
              placeholder="Rechercher quoi que ce soit..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full border-none px-3 py-1 text-xs text-gray-800 placeholder:text-gray-400 focus:outline-none focus:ring-0"
            />

            {/* Bouton Loupe */}
            <button
              type="submit"
              className="pl-2 text-gray-800 text-primary-hover transition cursor-pointer"
              aria-label="Rechercher"
            >
              <FaSearch className="text-xs" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}