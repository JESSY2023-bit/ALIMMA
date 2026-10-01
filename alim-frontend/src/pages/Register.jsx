import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash, FaArrowLeft } from "react-icons/fa";

export default function Register() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
  });

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  
  //  Hook pour la navigation retour
  const navigate = useNavigate();

  const handleChange = (e) => {
    //  Correction du bug : e.target.name au lieu de e.target.value
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log("Formulaire soumis :", formData);
    // Ajoutez ici votre logique d'inscription (ex: appel API Supabase)
  };

  return (
    // Ajout de "relative" pour positionner le bouton retour
    <div className="min-h-[75vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-white relative">
      
      
      {/* BOUTON RETOUR                  */}
      
      <button
        onClick={() => navigate(-1)}
        className="absolute top-6 left-6 md:top-8 md:left-8 flex items-center gap-2 text-gray-500 hover:text-primary transition-colors group"
      >
        <FaArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        <span className="font-medium text-sm">Retour</span>
      </button>

      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        
        {/* Colonne Gauche : Vector Illustration E-commerce */}
        <div className="flex justify-center items-center">
          <img
            src="/login.png"
            alt="Illustration Alimma"
            className="w-full max-w-md h-auto object-contain"
            onError={(e) => {
              e.target.src = "https://illustrations.popsy.co/amber/shopping-bags.svg";
            }}
          />
        </div>

        {/* Colonne Droite : Formulaire S'inscrire */}
        <div className="max-w-md w-full mx-auto space-y-6">
          <div>
            {/*  Utilisation de text-primary (violet) au lieu de l'orange */}
            <h2 className="text-4xl font-extrabold text-primary tracking-tight mb-1">
              S'inscrire
            </h2>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">
              REJOIGNEZ-NOUS
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Nom */}
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-800 mb-1.5">
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
                className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm placeholder:text-gray-400 text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-800 mb-1.5">
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
                className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm placeholder:text-gray-400 text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
              />
            </div>

            {/* Mot de passe */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-800 mb-1.5">
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
                  className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm placeholder:text-gray-400 text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary transition"
                >
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
            </div>

            {/* Confirmer le mot de passe */}
            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-800 mb-1.5">
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
                  className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm placeholder:text-gray-400 text-gray-800 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:border-primary transition-all"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary transition"
                >
                  {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
            </div>

            {/* Bouton S'inscrire (Violet de l'application) */}
            <div className="pt-2">
              <button
                type="submit"
                className="w-full bg-primary hover:bg-primary-dark text-white font-bold text-sm uppercase tracking-wider py-3.5 rounded-lg shadow-sm transition-colors duration-200 cursor-pointer"
              >
                S'INSCRIRE
              </button>
            </div>
          </form>

          {/* Redirection */}
          <div className="text-xs font-semibold text-gray-400 pt-2 uppercase">
            DÉJÀ UTILISATEUR ?{" "}
            <Link to="/login" className="text-primary hover:underline font-bold ml-1">
              CONNECTEZ-VOUS
            </Link>
          </div>
        </div>

      </div>
    </div>
  );
}