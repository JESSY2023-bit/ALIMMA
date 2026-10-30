


import { formatter } from "@lingui/format-po";

export default {
  locales: ["fr", "en"],
  sourceLocale: "fr",
  catalogs: [
    {
      path: "src/locales/{locale}/messages",
      include: ["src/**/*.{js,jsx}"], //  Cible explicitement les fichiers JS et JSX
    },
  ],
  format: formatter({ lineNumbers: false }),
  compileNamespace: "es",
};