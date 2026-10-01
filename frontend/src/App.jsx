import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login"; // Assurez-vous d'avoir ce fichier
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* ========================================== */}
        {/* ROUTES SANS NAVBAR / FOOTER (Authentification) */}
        {/* ========================================== */}
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />

        {/* ========================================== */}
        {/* ROUTES AVEC NAVBAR / FOOTER (MainLayout)   */}
        {/* ========================================== */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          
          {/* Ajoutez toutes vos autres pages ici (Profile, Products, etc.) */}
          
          {/* 404 — doit rester en dernier */}
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}