// Footer.jsx
import React from 'react';
import NewsletterForm from '../NewsLetter';
import { FaChevronDown } from 'react-icons/fa';



export default function Footer() {
  return (
    <footer className="bg-white text-gray-700 pt-16 pb-8 mt-16 font-sans border-t border-gray-100 w-full">
    
      <div className="max-w-[1600px] w-full mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Grille principale */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-y-10 gap-x-8">
          
          {/*  Marque & Contact (Prend 2 colonnes sur tablette) */}
          <div className="sm:col-span-2 lg:col-span-1">
            <h2 className="text-3xl font-extrabold text-gray-900 tracking-wider mb-2">
              ALIMMA
            </h2>
            <p className="text-xs font-semibold text-gray-600 uppercase mb-6">
              Ligne d'assistance 24 h/24 et 7 j/7
            </p>
            <p className="text-sm text-gray-600 mb-6">
              contact@alimma.com
            </p>
            
            {/* Réseaux sociaux */}
            <div className="flex flex-wrap gap-3 mb-8">
              {[
                { name: 'Twitter', icon: 'M23 3a10.9 10.9 0 01-3.14 1.53 4.48 4.48 0 00-7.86 3v1A10.66 10.66 0 013 4s-4 9 5 13a11.64 11.64 0 01-7 2c9 5 20 0 20-11.5a4.5 4.5 0 00-.08-.83A7.72 7.72 0 0023 3z' },
                { name: 'Facebook', icon: 'M18 2h-3a5 5 0 00-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 011-1h3z' },
                { name: 'Instagram', icon: 'M16 11.37A4 4 0 1112.63 8 4 4 0 0116 11.37zm1.5-4.87h.01M12 2a10 10 0 100 20 10 10 0 000-20z' },
                { name: 'YouTube', icon: 'M22.54 6.42a2.78 2.78 0 00-1.94-2C18.88 4 12 4 12 4s-6.88 0-8.6.42a2.78 2.78 0 00-1.94 2C1 8.25 1 12 1 12s0 3.75.46 5.58a2.78 2.78 0 001.94 2C5.12 20 12 20 12 20s6.88 0 8.6-.42a2.78 2.78 0 001.94-2C23 15.75 23 12 23 12s0-3.75-.46-5.58zM9.75 15.02V8.98L15.5 12l-5.75 3.02z' },
                { name: 'Pinterest', icon: 'M12 2C6.48 2 2 6.48 2 12c0 4.24 2.64 7.86 6.36 9.32-.09-.79-.17-2.01.04-2.87.19-.78 1.2-5.09 1.2-5.09s-.31-.61-.31-1.52c0-1.42.82-2.48 1.85-2.48.87 0 1.29.65 1.29 1.44 0 .87-.56 2.18-.85 3.39-.24.99.5 1.79 1.48 1.79 1.77 0 3.13-1.87 3.13-4.57 0-2.39-1.72-4.06-4.17-4.06-2.84 0-4.51 2.13-4.51 4.33 0 .86.33 1.78.74 2.28.08.1.09.19.06.29-.08.34-.27 1.09-.31 1.24-.05.2-.18.24-.4.15-1.49-.69-2.42-2.87-2.42-4.62 0-3.77 2.74-7.24 7.9-7.24 4.14 0 7.36 2.95 7.36 6.9 0 4.12-2.6 7.44-6.2 7.44-1.21 0-2.35-.63-2.74-1.38l-.74 2.83c-.27 1.03-1 2.32-1.49 3.11C9.87 21.77 10.91 22 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2z' }
              ].map((social) => (
                <a key={social.name} href="#" className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center text-gray-600 hover:bg-gray-300 transition-colors">
                  <svg viewBox="0 0 24 24" fill="currentColor" className="w-4 h-4">
                    <path d={social.icon} />
                  </svg>
                </a>
              ))}
            </div>

            {/* Sélecteurs Devise / Langue */}
            <div className="flex flex-wrap gap-3">
              <div className="relative">
                <select className="appearance-none bg-white border border-gray-300 rounded px-3 py-1.5 text-sm text-gray-700 outline-none cursor-pointer pr-8">
                  <option>FCFA</option>
                  <option>EUR</option>
                  <option>USD</option>
                </select>
                <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700">
                  <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z"/></svg>
                </div>
              </div>
              {/* Sélecteur de Langue avec Drapeau */}
             <div className="relative flex items-center bg-white border border-gray-300 rounded overflow-hidden">
  {/* L'image du drapeau (depuis le dossier public) */}
  <div className="absolute left-2.5 flex items-center pointer-events-none z-10">
    <img 
      src="/drapeau.png" 
      alt="Drapeau" 
      className="w-5 h-4 object-cover rounded-sm" 
    />
  </div>
  
  {/* Le menu déroulant */}
  <select className="appearance-none bg-transparent pl-9 pr-8 py-1.5 text-sm text-gray-700 outline-none cursor-pointer w-full z-0">
    <option>FR</option>
    <option>EN</option>
  </select>
  
  {/* La flèche vers le bas (avec react-icons) */}
  <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 z-10">
    <FaChevronDown className="h-4 w-4" />
  </div>
</div>
            </div>
          </div>

          {/* Colonne 2 : Top Categories */}
          <div>
            <h3 className="font-bold text-gray-900 uppercase text-sm mb-4">Top Categories</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              {['Laptops', 'PC & Computers', 'Cell Phones', 'Tablets', 'Gaming & VR', 'Networks', 'Cameras', 'Sounds', 'Office'].map((item) => (
                <li key={item}><a href="#" className="hover:text-gray-900 transition-colors">{item}</a></li>
              ))}
            </ul>
          </div>

          {/* Colonne 3 : Company */}
          <div>
            <h3 className="font-bold text-gray-900 uppercase text-sm mb-4">Company</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              {['About ALIMMA', 'Contact', 'Career', 'Blog', 'Sitemap', 'Store Locations'].map((item) => (
                <li key={item}><a href="#" className="hover:text-gray-900 transition-colors">{item}</a></li>
              ))}
            </ul>
          </div>

          {/* Colonne 4 : Help Center */}
          <div>
            <h3 className="font-bold text-gray-900 uppercase text-sm mb-4">Help Center</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              {['Customer Service', 'Policy', 'Terms & Conditions', 'Track Order', 'FAQs', 'My Account', 'Product Support'].map((item) => (
                <li key={item}><a href="#" className="hover:text-gray-900 transition-colors">{item}</a></li>
              ))}
            </ul>
          </div>

          {/* Colonne 5 : Partner */}
          <div>
            <h3 className="font-bold text-gray-900 uppercase text-sm mb-4">Partner</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              {['Become Seller', 'Affiliate', 'Advertise', 'Partnership'].map((item) => (
                <li key={item}><a href="#" className="hover:text-gray-900 transition-colors">{item}</a></li>
              ))}
            </ul>
          </div>
        </div>

        {/* Section Newsletter - Maintenant Centrée */}
        <div className="flex justify-center mt-16 mb-8">
          <NewsletterForm />
        </div>

        {/* Barre inférieure */}
        <div className="border-t border-gray-200 pt-8 flex flex-col md:flex-row justify-between items-center gap-6">
          <p className="text-sm text-gray-500 text-center md:text-left">
            © {new Date().getFullYear()} <span className="font-bold text-gray-900">ALIMMA</span>. Tous droits réservés
          </p>
          
          {/* Moyens de paiement */}
          <div className="flex flex-wrap justify-center items-center gap-3">
            <span className="text-[#003087] font-bold italic text-lg tracking-tighter">PayPal</span>
            <div className="flex items-center">
              <div className="w-6 h-6 bg-red-500 rounded-full opacity-80 -mr-2"></div>
              <div className="w-6 h-6 bg-yellow-500 rounded-full opacity-80"></div>
            </div>
            <span className="text-[#1A1F71] font-extrabold italic text-lg tracking-tighter">VISA</span>
            <span className="text-[#635BFF] font-bold text-lg tracking-tight">stripe</span>
            <span className="font-bold text-black text-lg tracking-tight">Klarna.</span>
            
            {/* Orange Money */}
            <div className="flex items-center bg-orange-500 text-white text-xs font-bold px-2 py-1 rounded">
              Orange Money
            </div>
            
            {/* MTN Mobile Money */}
            <div className="flex items-center bg-yellow-400 text-black text-xs font-bold px-2 py-1 rounded">
              MTN MoMo
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}