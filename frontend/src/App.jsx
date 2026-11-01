


// // src/App.jsx
// import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
// import MainLayout from "./components/layout/MainLayout";
// import ProtectedRoute from "./components/ProtectedRoute";
// import PublicOnlyRoute from "./components/PublicOnlyRoute";
// import Home from "./pages/Home";
// import Register from "./pages/Register";
// import Login from "./pages/Login";
// import NotFound from "./pages/NotFound";

// export default function App() {
//   return (
//     <BrowserRouter>
//       <Routes>
        
//         <Route element={<PublicOnlyRoute />}>
//           <Route path="/login" element={<Login />} />
//           <Route path="/register" element={<Register />} />
//         </Route>

//         {/* ROUTES AVEC NAVBAR + FOOTER   */}
        
//         <Route element={<MainLayout />}>
//           {/* --- Routes publiques (accessibles sans connexion) --- */}
//           <Route path="/" element={<Home />} />

//           {/* Routes protégées (nécessitent d'être connecté) --- */}
//           <Route element={<ProtectedRoute />}>
//             {/* Exemple : décommentez au fur et à mesure */}
//             {/* <Route path="/profile" element={<Profile />} /> */}
//             {/* <Route path="/mes-annonces" element={<MesAnnonces />} /> */}
//             {/* <Route path="/favoris" element={<Favoris />} /> */}
//             {/* <Route path="/commandes" element={<Commandes />} /> */}
//           </Route>

//           {/* 404  */}
//           <Route path="*" element={<NotFound />} />
//         </Route>
//       </Routes>
//     </BrowserRouter>
//   );
// }



// src/App.jsx
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import PublicOnlyRoute from "./components/PublicOnlyRoute";
import { ToastProvider } from "./components/ui";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Profile from './pages/Profile';
//import ForgotPassword from "./pages/ForgotPassword";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <BrowserRouter>
      <ToastProvider>
        <Routes>
          {/* PAGES D'AUTHENTIFICATION (sans navbar ni footer, réservées aux non-connectés) */}
          <Route element={<PublicOnlyRoute />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            {/* <Route path="/mot-de-passe-oublie" element={<ForgotPassword />} /> */}
          </Route>

          {/* ROUTES AVEC NAVBAR + FOOTER */}
          <Route element={<MainLayout />}>
            {/* --- Routes publiques --- */}
            <Route path="/" element={<Home />} />
            {/* <Route path="/cgu" element={<Cgu />} /> */}
            {/* <Route path="/confidentialite" element={<Confidentialite />} /> */}

            {/* --- Routes protégées (connexion requise) --- */}
            <Route element={<ProtectedRoute />}>
              <Route path="/profile" element={<Profile />} />
              {/* <Route path="/mes-annonces" element={<MesAnnonces />} /> */}
              {/* <Route path="/favoris" element={<Favoris />} /> */}
              {/* <Route path="/commandes" element={<Commandes />} /> */}
            </Route>

            {/* 404 */}
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </ToastProvider>
    </BrowserRouter>
  );
}