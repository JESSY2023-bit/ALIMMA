// src/components/layout/MainLayout.jsx
import { Outlet } from "react-router-dom";
import TopBar from "./TopBar";
import Navbar from "./NavBar";
import SearchBar from "./SearchBar";
import Footer from "./Footer";

export default function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* Header complet */}
      <header className="w-full">
        <TopBar />
        <Navbar />
        <SearchBar />
      </header>

      {/* Contenu de la page */}
      <main className="flex-1 w-full">
        <Outlet />
      </main>

      {/* Footer */}
      <Footer />
    </div>
  );
}