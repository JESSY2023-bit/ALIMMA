



import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";
import Home from "./pages/Home";
import Register from "./pages/Register";

import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Toutes les routes avec header + footer */}
        <Route element={<MainLayout />}>
          <Route path="/" element={<Home />} />
          <Route path="/register" element={<Register />} />
         

          {/* 404 — doit rester en dernier */}
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}