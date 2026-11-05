// // src/components/layout/MainLayout.jsx
// import { Outlet } from "react-router-dom";
// import TopBar from "./TopBar";
// import Navbar from "./Navbar";
// import SearchBar from "./SearchBar";
// import Footer from "./Footer";

// export default function MainLayout() {
//   return (
//     <div className="min-h-screen flex flex-col bg-white">
//       {/* Header complet */}
//       <header className="w-full">
//         <TopBar />
//         <Navbar />
//         <SearchBar />
//       </header>

//       {/* Contenu de la page */}
//       <main className="flex-1 w-full">
//         <Outlet />
//       </main>

//       {/* Footer */}
//       <Footer />
//     </div>
//   );
// }


import { Outlet } from "react-router-dom";
import TopBar from "./TopBar";
import Navbar from "./Navbar";
import CategoryNav from "./CategoryNav";
import Footer from "./Footer";

/** Pages avec en-tête et pied de page : TopBar → Navbar (logo, recherche, compte, panier) → CategoryNav → contenu → Footer. */
export default function MainLayout() {
  return (
    <div className="site">
      <a href="#contenu" className="skip-link">Aller au contenu</a>
      <TopBar />
      <Navbar />
      <CategoryNav />
      <main id="contenu" className="site__main">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}