import { FaChevronDown } from "react-icons/fa";

export default function TopBar() {
  return (
    <div className="bg-[--color-bg-soft] text-xs text-[--color-secondary-light] border-b border-[--color-border-soft]/50">
      <div className="max-w-7xl mx-auto flex items-center justify-between px-4 sm:px-8 py-2 gap-2">
        {/* Gauche */}
        <span className="bg-white px-3 py-1 rounded-md shadow-2xs font-medium text-[11px]">
          <span className="hidden sm:inline">Ligne d'assistance </span>24 h/24 et 7 j/7
        </span>

        {/* Droite */}
        <div className="flex items-center gap-4 text-[12px]">
          <a href="#" className="hidden md:inline hover:text-[--color-primary] transition">
            Vendez sur <span className="font-bold text-[--color-secondary]">ALIM<span className="text-[--color-primary]">MA</span></span>
          </a>
          <a href="#" className="hidden sm:inline hover:text-[--color-primary] transition whitespace-nowrap">
            Suivre la commande
          </a>

          <div className="hidden sm:flex items-center gap-1 cursor-pointer hover:text-[--color-primary] font-medium">
            FCFA <FaChevronDown className="text-[9px]" />
          </div>

          <div className="h-3 w-[1px] bg-gray-300 hidden sm:block"></div>

          <div className="flex items-center gap-1 cursor-pointer hover:text-[--color-primary] font-medium">
            <span>🇨🇲</span> Fr <FaChevronDown className="text-[9px]" />
          </div>
        </div>
      </div>
    </div>
  );
}