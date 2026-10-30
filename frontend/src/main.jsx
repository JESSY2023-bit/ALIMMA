


// // src/main.jsx
// import { StrictMode } from "react";
// import { createRoot } from "react-dom/client";
// import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
// import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
// import { AuthProvider } from "./contexts/AuthContext"; //  AJOUTER CET IMPORT
// import App from "./App.jsx";
// import "./index.css";

// const queryClient = new QueryClient({
//   defaultOptions: {
//     queries: {
//       staleTime: 1000 * 60,
//       refetchOnWindowFocus: false,
//     },
//     mutations: {
//       retry: 0, // ⚠️ Recommandé : ne jamais retenter une mutation automatiquement
//     },
//   },
// });

// createRoot(document.getElementById("root")).render(
//   <StrictMode>
//     <QueryClientProvider client={queryClient}>
//       {/* AJOUTER AuthProvider AUTOUR de App */}
//       <AuthProvider>
//         <App />
//       </AuthProvider>
//       <ReactQueryDevtools initialIsOpen={false} />
//     </QueryClientProvider>
//   </StrictMode>
// );



// src/main.jsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";

// 🌍 Imports Lingui
import { I18nProvider } from "@lingui/react";
import { i18n } from "./i18n";

import { AuthProvider } from "./contexts/AuthContext";
import App from "./App.jsx";
import "./index.css";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
});

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        {/* 🌍 Intégration du I18nProvider ici */}
        <I18nProvider i18n={i18n}>
          <App />
        </I18nProvider>
      </AuthProvider>
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  </StrictMode>
);