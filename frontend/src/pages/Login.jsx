


import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { FaEye, FaEyeSlash, FaArrowLeft } from "react-icons/fa";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { loginSchema, otpSchema } from "../schemas/authSchema";
import { useLogin, useVerifyOtp } from "../hooks/useAuth";

export default function Login() {
  const [showPassword, setShowPassword] = useState(false);
  const [otpStep, setOtpStep] = useState(false); // Étape 2 : OTP
  const [sessionToken, setSessionToken] = useState("");
  const [apiError, setApiError] = useState("");
  
  const navigate = useNavigate();
  const loginMutation = useLogin();
  const verifyOtpMutation = useVerifyOtp();

  // Formulaire de connexion
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(loginSchema),
  });

  // Formulaire OTP
  const { register: registerOtp, handleSubmit: handleOtpSubmit, formState: { errors: otpErrors } } = useForm({
    resolver: zodResolver(otpSchema),
  });

  // Soumission du login
  const onSubmitLogin = (data) => {
    setApiError("");
    loginMutation.mutate(data, {
      onSuccess: (response) => {
        if (response.otp_requis) {
          setSessionToken(response.session_token);
          setOtpStep(true); // Passer à l'étape OTP
        } else {
          // Connexion directe réussie
          localStorage.setItem("access_token", response.access_token);
          navigate("/"); 
        }
      },
      onError: (error) => {
        setApiError(error.response?.data?.message || "Identifiants incorrects.");
      },
    });
  };

  // Soumission de l'OTP
  const onSubmitOtp = (data) => {
    setApiError("");
    verifyOtpMutation.mutate(
      { session_token: sessionToken, code: data.code },
      {
        onSuccess: (response) => {
          localStorage.setItem("access_token", response.access_token);
          localStorage.setItem("refresh_token", response.refresh_token);
          navigate("/");
        },
        onError: (error) => {
          setApiError(error.response?.data?.message || "Code OTP invalide.");
        },
      }
    );
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-white px-4 py-12 relative">
      <button
        onClick={() => otpStep ? setOtpStep(false) : navigate(-1)}
        className="absolute top-6 left-6 md:top-8 md:left-8 flex items-center gap-2 text-gray-500 hover:text-primary transition-colors group"
      >
        <FaArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
        <span className="font-medium text-sm">Retour</span>
      </button>

      <div className="max-w-5xl w-full grid grid-cols-1 md:grid-cols-2 gap-16 items-center">
        <div className="hidden md:flex justify-center">
          <img src="/login.png" alt="Illustration" className="max-w-md w-full object-contain" />
        </div>

        <div className="max-w-md w-full mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold text-primary mb-3">
            {otpStep ? "Vérification" : "Content de te revoir"}
          </h1>
          <p className="text-gray-500 uppercase tracking-widest text-xs md:text-sm mb-8">
            {otpStep ? "Entrez le code reçu par SMS" : "Connectez-vous pour continuer"}
          </p>

          {apiError && (
            <div className="bg-red-50 text-red-500 text-sm p-3 rounded-lg mb-4">
              {apiError}
            </div>
          )}

          {/* ÉTAPE 1 : Connexion */}
          {!otpStep ? (
            <form onSubmit={handleSubmit(onSubmitLogin)} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-800 mb-2">
                  Adresse e-mail ou Téléphone
                </label>
                <input
                  {...register("identifiant")}
                  type="text"
                  placeholder="Exemple@gmail.com ou +237..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-gray-700"
                />
                {errors.identifiant && <p className="text-red-500 text-xs mt-1">{errors.identifiant.message}</p>}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-800 mb-2">Mot de passe</label>
                <div className="relative">
                  <input
                    {...register("password")}
                    type={showPassword ? "text" : "password"}
                    placeholder="••••"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent text-gray-700"
                  />
                  <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600">
                    {showPassword ? <FaEyeSlash className="w-5 h-5" /> : <FaEye className="w-5 h-5" />}
                  </button>
                </div>
                {errors.password && <p className="text-red-500 text-xs mt-1">{errors.password.message}</p>}
                <div className="text-right mt-2">
                  <Link to="#" className="text-sm text-gray-500 underline hover:text-primary">Mot de passe oublié ?</Link>
                </div>
              </div>

              <button
                type="submit"
                disabled={loginMutation.isPending}
                className="w-full bg-primary text-white font-bold uppercase py-3.5 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-70"
              >
                {loginMutation.isPending ? "Connexion..." : "Se connecter"}
              </button>
            </form>
          ) : (
            /* ÉTAPE 2 : OTP */
            <form onSubmit={handleOtpSubmit(onSubmitOtp)} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-800 mb-2">Code OTP</label>
                <input
                  {...registerOtp("code")}
                  type="text"
                  maxLength={6}
                  placeholder="Ex: 482913"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-center text-2xl tracking-widest"
                />
                {otpErrors.code && <p className="text-red-500 text-xs mt-1 text-center">{otpErrors.code.message}</p>}
              </div>
              <button
                type="submit"
                disabled={verifyOtpMutation.isPending}
                className="w-full bg-primary text-white font-bold uppercase py-3.5 rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-70"
              >
                {verifyOtpMutation.isPending ? "Vérification..." : "Valider le code"}
              </button>
            </form>
          )}

          {!otpStep && (
            <p className="mt-8 text-center text-xs md:text-sm text-gray-500 uppercase tracking-wide">
              Nouvel utilisateur ?{" "}
              <Link to="/register" className="text-primary font-bold hover:underline ml-1">Inscrivez-vous</Link>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}