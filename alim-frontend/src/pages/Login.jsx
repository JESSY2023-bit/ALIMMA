import { useState } from "react";

import { Link, useNavigate } from "react-router-dom";

import { FaEye, FaEyeSlash, FaArrowLeft } from "react-icons/fa";

export default function Login() {
  const [showPassword, setShowPassword] = useState(false);
  //  Initialisation de la navigation
  const navigate = useNavigate();

  return (
    // Ajout de "relative" pour positionner le bouton retour en absolu
    <div className="min-h-screen flex items-center justify-center bg-white px-4 py-12 relative">
      
      <button
        onClick={() => navigate(-1)}
        className="absolute top-6 left-6 md:top-8 md:left-8 flex items-center gap-2 text-gray-500 hover:text-primary transition-colors group"
      >
        <FaArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        <span className="font-medium text-sm">Retour</span>
      </button>

      <div className="max-w-5xl w-full grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
        
        
        {/* COLONNE GAUCHE : ILLUSTRATION  */}
        
        <div className="hidden md:flex justify-center">
          <img 
            src="/login.png" 
            alt="Illustration de connexion" 
            className="max-w-md w-full object-contain"
          />
        </div>

        
        {/* COLONNE DROITE : FORMULAIRE    */}
        
        <div className="max-w-md w-full mx-auto">
          {/* Titre et sous-titre */}
          <h1 className="text-3xl md:text-4xl font-bold text-primary mb-3">
            Content de te revoir
          </h1>
          <p className="text-gray-500 uppercase tracking-widest text-xs md:text-sm mb-8">
            Connectez-vous pour continuer
          </p>

          <form className="space-y-6">
            {/* Champ Email */}
            <div>
              <label className="block text-sm font-medium text-gray-800 mb-2">
                Adresse e-mail Continuer
              </label>
              <input
                type="email"
                placeholder="Exemple@gmail.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-gray-700"
              />
            </div>

            {/* Champ Mot de passe */}
            <div>
              <label className="block text-sm font-medium text-gray-800 mb-2">
                Mot de passe
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  placeholder="••••"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-gray-700"
                />
                
                {/* Bouton œil avec les icônes Font Awesome */}
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? (
                    <FaEyeSlash className="w-5 h-5" />
                  ) : (
                    <FaEye className="w-5 h-5" />
                  )}
                </button>
              </div>
              
              {/* Lien Mot de passe oublié */}
              <div className="text-right mt-2">
                <Link to="#" className="text-sm text-gray-500 underline hover:text-primary transition-colors">
                  Mot de passe oublié ?
                </Link>
              </div>
            </div>

            {/* Bouton Se Connecter */}
            <button
              type="submit"
              className="w-full bg-primary text-white font-bold uppercase py-3.5 rounded-lg hover:bg-primary-dark transition-colors duration-200 mt-4"
            >
              Se connecter
            </button>
          </form>

          {/* Lien vers Register */}
          <p className="mt-8 text-center text-xs md:text-sm text-gray-500 uppercase tracking-wide">
            Nouvel utilisateur ?{" "}
            <Link to="/register" className="text-primary font-bold hover:underline ml-1">
              Inscrivez-vous
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}