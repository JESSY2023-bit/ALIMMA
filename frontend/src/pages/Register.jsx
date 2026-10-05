

import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash, FaArrowLeft } from "react-icons/fa";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { registerSchema } from "../schemas/authSchema";
import { useRegister } from "../hooks/useAuth";

export default function Register() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [apiError, setApiError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  
  const navigate = useNavigate();
  const registerMutation = useRegister();

  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = (data) => {
    setApiError("");
    setSuccessMsg("");
    
    registerMutation.mutate(data, {
      onSuccess: () => {
        setSuccessMsg("Compte créé avec succès ! Redirection...");
        setTimeout(() => navigate("/login"), 2000);
      },
      onError: (error) => {
        setApiError(error.response?.data?.message || "Erreur lors de l'inscription.");
      },
    });
  };

  return (
    <div className="min-h-[75vh] flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 bg-white relative">
      <button
        onClick={() => navigate(-1)}
        className="absolute top-6 left-6 md:top-8 md:left-8 flex items-center gap-2 text-gray-500 hover:text-primary transition-colors group"
      >
        <FaArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        <span className="font-medium text-sm">Retour</span>
      </button>

      <div className="max-w-6xl w-full grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
        <div className="flex justify-center items-center">
          <img src="/login.png" alt="Illustration" className="w-full max-w-md h-auto object-contain" />
        </div>

        <div className="max-w-md w-full mx-auto space-y-6">
          <div>
            <h2 className="text-4xl font-extrabold text-primary tracking-tight mb-1">S'inscrire</h2>
            <p className="text-xs font-bold tracking-widest text-gray-400 uppercase">REJOIGNEZ-NOUS</p>
          </div>

          {apiError && <div className="bg-red-50 text-red-500 text-sm p-3 rounded-lg">{apiError}</div>}
          {successMsg && <div className="bg-green-50 text-green-600 text-sm p-3 rounded-lg">{successMsg}</div>}

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Nom */}
            <div>
              <label className="block text-sm font-medium text-gray-800 mb-1.5">Votre nom complet</label>
              <input
                {...register("nom")}
                type="text"
                placeholder="Ex: John Doe"
                className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
              {errors.nom && <p className="text-red-500 text-xs mt-1">{errors.nom.message}</p>}
            </div>

            {/* Téléphone (Nouveau champ requis par l'API) */}
            <div>
              <label className="block text-sm font-medium text-gray-800 mb-1.5">Téléphone</label>
              <input
                {...register("telephone")}
                type="tel"
                placeholder="+237670000000"
                className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
              {errors.telephone && <p className="text-red-500 text-xs mt-1">{errors.telephone.message}</p>}
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-800 mb-1.5">Adresse email (Optionnel)</label>
              <input
                {...register("email")}
                type="email"
                placeholder="Entrez votre email"
                className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary"
              />
              {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email.message}</p>}
            </div>

            {/* Mot de passe */}
            <div>
              <label className="block text-sm font-medium text-gray-800 mb-1.5">Mot de passe</label>
              <div className="relative">
                <input
                  {...register("password")}
                  type={showPassword ? "text" : "password"}
                  placeholder="...."
                  className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary">
                  {showPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
              {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
            </div>

            {/* Confirmer le mot de passe */}
            <div>
              <label className="block text-sm font-medium text-gray-800 mb-1.5">Confirmez le mot de passe</label>
              <div className="relative">
                <input
                  {...register("confirmPassword")}
                  type={showConfirmPassword ? "text" : "password"}
                  placeholder="...."
                  className="w-full rounded-lg border border-gray-200 px-4 py-3 text-sm focus:ring-2 focus:ring-primary/30 focus:border-primary"
                />
                <button type="button" onClick={() => setShowConfirmPassword(!showConfirmPassword)} className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-primary">
                  {showConfirmPassword ? <FaEyeSlash /> : <FaEye />}
                </button>
              </div>
              {errors.confirmPassword && <p className="text-red-500 text-xs mt-1">{errors.confirmPassword.message}</p>}
            </div>

            {/* Bouton S'inscrire */}
            <div className="pt-2">
              <button
                type="submit"
                disabled={registerMutation.isPending}
                className="w-full bg-primary hover:bg-primary-dark text-white font-bold text-sm uppercase tracking-wider py-3.5 rounded-lg shadow-sm transition-colors disabled:opacity-70"
              >
                {registerMutation.isPending ? "Inscription en cours..." : "S'INSCRIRE"}
              </button>
            </div>
          </form>

          <div className="text-xs font-semibold text-gray-400 pt-2 uppercase">
            DÉJÀ UTILISATEUR ?{" "}
            <Link to="/login" className="text-primary hover:underline font-bold ml-1">CONNECTEZ-VOUS</Link>
          </div>
        </div>
      </div>
    </div>
  );
}