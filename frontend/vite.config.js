// // import react from '@vitejs/plugin-react'

// // import { defineConfig } from 'vite'
// // import tailwindcss from '@tailwindcss/vite'

// // // https://vite.dev/config/
// // export default defineConfig({
// //   plugins: [react() , tailwindcss()],

// import { defineConfig, loadEnv } from 'vite'
// import tailwindcss from '@tailwindcss/vite'

// // Le proxy évite au navigateur local d'appeler directement localhost:8000.
// // Dans Docker, la cible est le nom de service Compose « backend ».
// export default defineConfig(({ mode }) => {
//   const env = loadEnv(mode, process.cwd(), '')

//   return {
//     plugins: [react(), tailwindcss()],
//     server: {
//       proxy: {
//         '/v1': {
//           target: env.VITE_API_PROXY_TARGET || 'http://localhost:8000',
//           changeOrigin: true,
//         },
//       },
//     },
//   }

// })



import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { lingui } from "@lingui/vite-plugin";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [
      lingui({ macroTransform: true }),
      react(),
      tailwindcss(),
    ],

    server: {
      proxy: {
        "/v1": {
          target:
            env.VITE_API_PROXY_TARGET || "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
  };
});
