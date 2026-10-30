// // src/i18n.js
// import { i18n } from "@lingui/core";

// // Import direct des messages compilés par Lingui (générés dans src/locales/)
// import { messages as messagesFr } from "./locales/fr/messages.js";
// import { messages as messagesEn } from "./locales/en/messages.js";

// i18n.load({
//   fr: messagesFr,
//   en: messagesEn,
// });

// export async function dynamicActivate(locale) {
//   i18n.activate(locale);
// }

// // Activer le français par défaut au démarrage
// i18n.activate("fr");

// export { i18n };




// src/i18n.js
import { i18n } from "@lingui/core";

// Import direct des messages compilés par Lingui
import { messages as messagesFr } from "./locales/fr/messages.mjs";
import { messages as messagesEn } from "./locales/en/messages.mjs";

i18n.load({
  fr: messagesFr,
  en: messagesEn,
});

export async function dynamicActivate(locale) {
  i18n.activate(locale);
}

// Activer le français par défaut
i18n.activate("fr");

export { i18n };