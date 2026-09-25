import { Outlet } from "react-router-dom";
import TopBar from "./TopBar";
import Navbar from "./Navbar";
import SearchBar from "./SearchBar";
import Footer from "./Footer";

export default function MainLayout() {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Partie haute fixe sur toutes les pages */}
      <header>
        <TopBar />
        <Navbar />
        <SearchBar />
      </header>

      {/* Contenu de la page courante */}
      <main className="flex-1">
        <Outlet />
      </main>

      <Footer />
    </div>
  );
}