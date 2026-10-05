// src/components/PublicOnlyRoute.jsx
import { Navigate, Outlet } from "react-router-dom";
import { useAuthContext } from "../hooks/useAuthContext";

export default function PublicOnlyRoute() {
  const { isAuthenticated, isLoading } = useAuthContext();

  if (isLoading) return null; // ou un loader

  // Si déjà connecté, on redirige vers l'accueil
  if (isAuthenticated) return <Navigate to="/" replace />;

  return <Outlet />;
}