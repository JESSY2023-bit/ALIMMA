import { useState } from "react";
import { Link, NavLink } from "react-router-dom";
import {
  FaChevronDown,
  FaHeart,
  FaShoppingCart,
  FaBars,
  FaTimes,
  FaExchangeAlt,
  FaEye,
} from "react-icons/fa";

const navItems = [
  { label: "HOMES", to: "/" },
  { label: "PAGES", to: "/pages" },
  { label: "PRODUCTS", to: "/products" },
  { label: "CONTACT", to: "/contact" },
];

export default function Navbar() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="w-full bg-white border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3.5 flex items-center justify-between gap-2 xl:gap-4">
        
        {/* Logo + Liens de Navigation */}
        <div className="flex items-center gap-4 xl:gap-8 shrink-0">
          <Link to="/" className="font-display text-2xl font-black tracking-tight shrink-0 text-gray-900">
            ALIM<span className="text-primary">MA</span>
          </Link>

          <nav className="hidden lg:flex items-center gap-4 xl:gap-6">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex items-center gap-1 text-[11px] xl:text-xs font-bold uppercase tracking-wider transition ${
                    isActive ? "text-primary" : "text-gray-800 text-primary-hover"
                  }`
                }
              >
                {item.label}
                <FaChevronDown className="text-[8px] text-gray-500" />
              </NavLink>
            ))}
          </nav>
        </div>

        {/* Bloc d'actions à droite */}
        <div className="hidden lg:flex items-center gap-2 xl:gap-3 shrink-0">
          
          {/* Boutons d'icônes circulaires */}
          <button className="w-8 h-8 xl:w-9 xl:h-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
            <FaExchangeAlt className="text-xs" />
          </button>

          <button className="w-8 h-8 xl:w-9 xl:h-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
            <FaHeart className="text-xs" />
          </button>

          <button className="w-8 h-8 xl:w-9 xl:h-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-600 text-primary-hover transition cursor-pointer shrink-0">
            <FaEye className="text-xs" />
          </button>

          {/* Connexion / Inscription */}
          <div className="text-left leading-tight ml-1 shrink-0">
            <p className="text-[8px] xl:text-[9px] uppercase font-bold text-gray-400 tracking-wider">BIENVENU</p>
            <Link to="/register" className="font-extrabold uppercase text-gray-800 text-primary-hover transition whitespace-nowrap text-[10px] xl:text-[11px]">
              CONNEXION / INSCRIPTION
            </Link>
          </div>

          {/* PANIER CORRIGÉ : flex-row strict pour forcer l'alignement horizontal */}
          <div className="flex items-center gap-2 ml-1 xl:ml-2 shrink-0">
            {/* Icône Panier + Badge */}
            <div className="relative shrink-0">
              <div className="w-8 h-8 xl:w-9 xl:h-9 rounded-full bg-gray-100 flex items-center justify-center text-gray-600">
                <FaShoppingCart className="text-xs" />
              </div>
              <span className="badge-primary absolute -top-1 -right-1 text-[8px] xl:text-[9px] w-4 h-4 border-2 border-white">
                5
              </span>
            </div>

            {/* Libellé et Montant à droite de l'icône */}
            <div className="flex flex-col justify-center text-left leading-none shrink-0">
              <span className="text-[8px] xl:text-[9px] uppercase font-bold text-gray-400 tracking-wider mb-0.5">
                PANIER
              </span>
              <span className="font-extrabold text-gray-900 whitespace-nowrap text-[10px] xl:text-[11px]">
                FCFA 1,689.00
              </span>
            </div>
          </div>

        </div>

        {/* Bouton pour menu mobile */}
        <button onClick={() => setMobileOpen(!mobileOpen)} className="lg:hidden p-2 text-xl text-gray-800">
          {mobileOpen ? <FaTimes /> : <FaBars />}
        </button>
      </div>

      {/* Menu Mobile */}
      {mobileOpen && (
        <div className="lg:hidden bg-white border-t border-gray-200 px-4 py-3">
          <nav className="flex flex-col gap-2">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setMobileOpen(false)}
                className="py-2 text-xs font-bold uppercase text-gray-800"
              >
                {item.label}
              </NavLink>
            ))}
          </nav>
        </div>
      )}
    </div>
  );
}