/** Chiffres du numéro camerounais (retire +237, espaces, tirets). */
export const digitsOf = (value = "") => {
  let d = String(value).replace(/\D/g, "");
  if (d.startsWith("237") && d.length > 9) d = d.slice(3);
  return d;
};

export const toE164 = (value) => `+237${digitsOf(value)}`;

/** Identifiant de connexion : email tel quel, sinon numéro au format +237XXXXXXXXX. */
export const normalizeIdentifier = (value = "") => {
  const t = value.trim();
  return t.includes("@") ? t.toLowerCase() : toE164(t);
};

/** +237 670123456 → « +237 6•• •• 34 56 » (null si ce n’est pas un numéro). */
export const maskPhone = (value = "") => {
  const d = digitsOf(value);
  return d.length === 9 ? `+237 ${d[0]}•• •• ${d.slice(5, 7)} ${d.slice(7)}` : null;
};
