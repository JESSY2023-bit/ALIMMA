/**
 * Erreurs 422 : chaque erreur de champ renvoyée par l’API s’affiche sous le champ concerné,
 * et le focus va au premier champ en erreur. Attendu : { errors: { champ: "message" | ["message"] } }
 * `map` renomme les champs API → champs du formulaire (ex. { code_parrainage: "codeParrainage" }).
 * Retourne true si au moins une erreur de champ a été appliquée.
 */
export function applyApiFieldErrors(error, setError, setFocus, map = {}) {
  const fields = error?.response?.data?.errors;
  if (!fields || typeof fields !== "object") return false;
  const entries = Object.entries(fields);
  if (!entries.length) return false;
  entries.forEach(([key, value]) => {
    setError(map[key] ?? key, { type: "server", message: Array.isArray(value) ? value[0] : String(value) });
  });
  setFocus(map[entries[0][0]] ?? entries[0][0]);
  return true;
}

/** Erreur serveur (5xx) ou réseau : on garde les saisies et on propose « Réessayer ». */
export const isNetworkOrServerError = (error) => !error?.response || error.response.status >= 500;
