
// src/components/layout/TopBar.jsx
import { useState, useRef, useEffect } from "react";
import { FaChevronDown, FaCheck } from "react-icons/fa";

const LANGUAGES = [
  { code: "fr", label: "Fr", fullLabel: "Français", flag: "/drapeau.png" },
  { code: "en", label: "En", fullLabel: "English", flag: "/drapeau.png" },
];

const CURRENCIES = [
  { code: "XAF", label: "FCFA" },
  { code: "EUR", label: "EUR" },
  { code: "USD", label: "USD" },
];

export default function TopBar() {
  const [langOpen, setLangOpen] = useState(false);
  const [currencyOpen, setCurrencyOpen] = useState(false);

  const [currentLang, setCurrentLang] = useState(LANGUAGES[0]);
  const [currentCurrency, setCurrentCurrency] = useState(CURRENCIES[0]);

  const langRef = useRef(null);
  const currencyRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (langRef.current && !langRef.current.contains(e.target)) {
        setLangOpen(false);
      }
      if (currencyRef.current && !currencyRef.current.contains(e.target)) {
        setCurrencyOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleSelectLanguage = (lang) => {
    setCurrentLang(lang);
    setLangOpen(false);
  };

  return (
    <div className="bg-bg-soft text-secondary-light border-b border-border-soft/50">
      <div className="alimma-layout flex items-center justify-between py-2.5 gap-2">
        {/* Gauche */}
        <span className="bg-white px-3 py-1.5 rounded-md shadow-sm font-medium text-sm">
          <span className="hidden sm:inline">Ligne d'assistance </span>
          24 h/24 et 7 j/7
        </span>

        {/* Droite */}
        <div className="flex items-center gap-4 text-sm">
          <a href="#" className="hidden md:inline hover:text-primary transition">
            Vendez sur{" "}
            <span className="font-bold text-secondary">
              ALIM<span className="text-primary">MA</span>
            </span>
          </a>

          <a
            href="#"
            className="hidden sm:inline hover:text-primary transition whitespace-nowrap"
          >
            Suivre la commande
          </a>

          {/* Menu Devise */}
          <div className="relative" ref={currencyRef}>
            <button
              onClick={() => {
                setCurrencyOpen(!currencyOpen);
                setLangOpen(false);
              }}
              className="hidden sm:flex items-center gap-1 cursor-pointer hover:text-primary font-medium"
            >
              {currentCurrency.label}
              <FaChevronDown
                className={`text-[10px] transition-transform ${
                  currencyOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {currencyOpen && (
              <div className="absolute right-0 top-full mt-2 w-24 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50">
                {CURRENCIES.map((c) => (
                  <button
                    key={c.code}
                    onClick={() => {
                      setCurrentCurrency(c);
                      setCurrencyOpen(false);
                    }}
                    className="w-full flex items-center justify-between px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
                  >
                    <span>{c.label}</span>
                    {currentCurrency.code === c.code && (
                      <FaCheck className="text-[9px] text-primary" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>

          <div className="h-3 w-[1px] bg-gray-300 hidden sm:block"></div>

          {/* Menu Langue */}
          <div className="relative" ref={langRef}>
            <button
              onClick={() => {
                setLangOpen(!langOpen);
                setCurrencyOpen(false);
              }}
              className="flex items-center gap-1.5 cursor-pointer hover:text-primary font-medium"
            >
              <img
                src={currentLang.flag}
                alt={currentLang.fullLabel}
                className="w-5 h-3.5 object-cover rounded-sm"
              />
              <span>{currentLang.label}</span>
              <FaChevronDown
                className={`text-[10px] transition-transform ${
                  langOpen ? "rotate-180" : ""
                }`}
              />
            </button>

            {langOpen && (
              <div className="absolute right-0 top-full mt-2 w-32 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50">
                {LANGUAGES.map((l) => (
                  <button
                    key={l.code}
                    onClick={() => handleSelectLanguage(l)}
                    className="w-full flex items-center justify-between px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
                  >
                    <span>{l.fullLabel}</span>
                    {currentLang.code === l.code && (
                      <FaCheck className="text-[9px] text-primary" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// // src/components/layout/TopBar.jsx
// import { useState, useRef, useEffect } from "react";
// import { FaChevronDown, FaCheck } from "react-icons/fa";
// import { useLingui, Trans } from "@lingui/react/macro";
// import { useLingui as useLinguiCore } from "@lingui/react";
// import { dynamicActivate } from "../../i18n";

// const LANGUAGES = [
//   { code: "fr", label: "Fr", fullLabel: "Français", flag: "/drapeau.png" },
//   { code: "en", label: "En", fullLabel: "English", flag: "/drapeau.png" },
// ];

// const CURRENCIES = [
//   { code: "XAF", label: "FCFA" },
//   { code: "EUR", label: "EUR" },
//   { code: "USD", label: "USD" },
// ];

// export default function TopBar() {
//   // ✅ t() via le macro React (comme dans Login.jsx)
//   const { t } = useLingui();

//   // ✅ Accès à l'instance i18n réelle (pour lire .locale)
//   const { i18n } = useLinguiCore();
//   const activeLocale = i18n.locale || "fr";

//   const [langOpen, setLangOpen] = useState(false);
//   const [currencyOpen, setCurrencyOpen] = useState(false);

//   const initialLang = LANGUAGES.find((l) => l.code === activeLocale) || LANGUAGES[0];
//   const [currentLang, setCurrentLang] = useState(initialLang);
//   const [currentCurrency, setCurrentCurrency] = useState(CURRENCIES[0]);

//   const langRef = useRef(null);
//   const currencyRef = useRef(null);

//   useEffect(() => {
//     const matchedLang = LANGUAGES.find((l) => l.code === activeLocale);
//     if (matchedLang) {
//       setCurrentLang(matchedLang);
//     }
//   }, [activeLocale]);

//   useEffect(() => {
//     const handleClickOutside = (e) => {
//       if (langRef.current && !langRef.current.contains(e.target)) {
//         setLangOpen(false);
//       }
//       if (currencyRef.current && !currencyRef.current.contains(e.target)) {
//         setCurrencyOpen(false);
//       }
//     };
//     document.addEventListener("mousedown", handleClickOutside);
//     return () => document.removeEventListener("mousedown", handleClickOutside);
//   }, []);

//   const handleSelectLanguage = (lang) => {
//     setCurrentLang(lang);
//     dynamicActivate(lang.code);
//     setLangOpen(false);
//   };

//   return (
//     <div className="bg-bg-soft text-secondary-light border-b border-border-soft/50">
//       <div className="alimma-layout flex items-center justify-between py-2.5 gap-2">
//         {/* Gauche */}
//         <span className="bg-white px-3 py-1.5 rounded-md shadow-sm font-medium text-sm">
//           <span className="hidden sm:inline">
//             <Trans>Ligne d'assistance </Trans>
//           </span>
//           <Trans>24 h/24 et 7 j/7</Trans>
//         </span>

//         {/* Droite */}
//         <div className="flex items-center gap-4 text-sm">
//           <a href="#" className="hidden md:inline hover:text-primary transition">
//             <Trans>Vendez sur</Trans>{" "}
//             <span className="font-bold text-secondary">
//               ALIM<span className="text-primary">MA</span>
//             </span>
//           </a>

//           <a
//             href="#"
//             className="hidden sm:inline hover:text-primary transition whitespace-nowrap"
//           >
//             <Trans>Suivre la commande</Trans>
//           </a>

//           {/* Menu Devise */}
//           <div className="relative" ref={currencyRef}>
//             <button
//               onClick={() => {
//                 setCurrencyOpen(!currencyOpen);
//                 setLangOpen(false);
//               }}
//               className="hidden sm:flex items-center gap-1 cursor-pointer hover:text-primary font-medium"
//             >
//               {currentCurrency.label}
//               <FaChevronDown
//                 className={`text-[10px] transition-transform ${
//                   currencyOpen ? "rotate-180" : ""
//                 }`}
//               />
//             </button>

//             {currencyOpen && (
//               <div className="absolute right-0 top-full mt-2 w-24 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50">
//                 {CURRENCIES.map((c) => (
//                   <button
//                     key={c.code}
//                     onClick={() => {
//                       setCurrentCurrency(c);
//                       setCurrencyOpen(false);
//                     }}
//                     className="w-full flex items-center justify-between px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <span>{c.label}</span>
//                     {currentCurrency.code === c.code && (
//                       <FaCheck className="text-[9px] text-primary" />
//                     )}
//                   </button>
//                 ))}
//               </div>
//             )}
//           </div>

//           <div className="h-3 w-[1px] bg-gray-300 hidden sm:block"></div>

//           {/* Menu Langue */}
//           <div className="relative" ref={langRef}>
//             <button
//               onClick={() => {
//                 setLangOpen(!langOpen);
//                 setCurrencyOpen(false);
//               }}
//               className="flex items-center gap-1.5 cursor-pointer hover:text-primary font-medium"
//             >
//               <img
//                 src={currentLang.flag}
//                 alt={currentLang.fullLabel}
//                 className="w-5 h-3.5 object-cover rounded-sm"
//               />
//               <span>{currentLang.label}</span>
//               <FaChevronDown
//                 className={`text-[10px] transition-transform ${
//                   langOpen ? "rotate-180" : ""
//                 }`}
//               />
//             </button>

//             {langOpen && (
//               <div className="absolute right-0 top-full mt-2 w-32 bg-white rounded-lg shadow-lg border border-gray-100 py-1 z-50">
//                 {LANGUAGES.map((l) => (
//                   <button
//                     key={l.code}
//                     onClick={() => handleSelectLanguage(l)}
//                     className="w-full flex items-center justify-between px-3 py-1.5 text-sm text-gray-700 hover:bg-gray-50 hover:text-primary transition"
//                   >
//                     <span>{l.fullLabel}</span>
//                     {currentLang.code === l.code && (
//                       <FaCheck className="text-[9px] text-primary" />
//                     )}
//                   </button>
//                 ))}
//               </div>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }