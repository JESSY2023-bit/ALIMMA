import { useState } from "react";
import { Link } from "react-router-dom";
import { FaEye, FaEyeSlash } from "react-icons/fa";

export default function Register() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.value]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Formulaire soumis :", formData);
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-white">
      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        
        {/* Colonne Gauche : Vector Illustration E-commerce */}
        <div className="flex justify-center items-center">
          <img
            src="https://cdni.iconscout.com/illustration/premium/thumb/online-shopping-app-illustration-download-in-svg-png-gif-file-formats--mobile-store-[#f05a22]-buy-e-commerce-pack-illustrations-3798242.png?f=webp&w=600"
            alt="Illustration Alimma"
            className="w-full max-w-md h-auto object-contain"
            onError={(e) => {
              // Image SVG Fallback si le lien réseau bloque
              e.target.src = "https://illustrations.popsy.co/amber/shopping-bags.svg";
            }}
          />
        </div>

        {/* Colonne Droite : Formulaire S'inscrire */}
        <div className="max-w-md w-full mx-auto space-y-6">
          <div>
            <h2 className="text-4xl font-extrabold text-[#f05a22] tracking-tight mb-1">
              S'inscrire
            </h2>
            <p className="text-xs font-bold tracking-widest text-[#9ca3af] uppercase">
              REJOIGNEZ-NOUS
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Nom */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-[#1a1a1a] mb-1.5">
                Votre nom
              </label>
              <input
                id="name"
                type="text"
                name="name"
                placeholder="Votre nom complet"
                value={formData.name}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm placeholder:text-gray-400 text-[#1a1a1a] focus:outline-none focus:ring-2 focus:ring-[#f05a22]/30 focus:border-[#f05a22] transition-all"
              />
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-[#1a1a1a] mb-1.5">
                Adresse email
              </label>
              <input
                id="email"
                type="email"
                name="email"
                placeholder="Entrez votre email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm placeholder:text-gray-400 text-[#1a1a1a] focus:outline-none focus:ring-2 focus:ring-[#f05a22]/30 focus:border-[#f05a22] transition-all"
              />
            </div>

            {/* Mot de passe */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-[#1a1a1a] mb-1.5">
                Mot de passe
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  name="password"
                  placeholder="...."
                  value={formData.password}
                  onChange={handleChange}
                  required
                  className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm placeholder:text-gray-400 text-[#1a1a1a] focus:outline-none focus:ring-2 focus:ring-[#f05a22]/30 focus:border-[#f05a22] transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#f05a22] transition"
                >
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
            </div>

            {/* Confirmer le mot de passe */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-[#1a1a1a] mb-1.5">
                Confirmez le mot de passe
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? "text" : "password"}
                  name="confirmPassword"
                  placeholder="...."
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                  className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm placeholder:text-gray-400 text-[#1a1a1a] focus:outline-none focus:ring-2 focus:ring-[#f05a22]/30 focus:border-[#f05a22] transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-[#f05a22] transition"
                >
                  {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
            </div>

            {/* Bouton S'inscrire (Orange Vif Direct) */}
            <div className="pt-2">
              <button
                type="submit"
                className="bg-[#f05a22] hover:bg-[#d94a15] text-white font-bold text-sm uppercase tracking-wider px-10 py-3.5 rounded-lg shadow-sm transition-colors duration-200 cursor-pointer"
              >
                S'INSCRIRE
              </button>
            </div>
          </form>

          {/* Redirection */}
          <div className="text-xs font-semibold text-[#9ca3af] pt-2 uppercase">
            DÉJÀ UTILISATEUR ?{" "}
            <Link to="/login" className="text-[#f05a22] hover:underline font-bold ml-1">
              CONNECTEZ-VOUS
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
}