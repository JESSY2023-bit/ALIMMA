const MONTHS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août", "septembre", "octobre", "novembre", "décembre"];
const MONTHS_SHORT = ["janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc."];

const toDate = (value) => {
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
};

export const formatNumber = (n) => new Intl.NumberFormat("fr-FR").format(n ?? 0);

/** « juin 2024 » */
export const memberSince = (value) => {
  const d = toDate(value);
  return d ? `${MONTHS[d.getMonth()]} ${d.getFullYear()}` : "";
};

/** « 14 mars 2026 » */
export const formatDateLong = (value) => {
  const d = toDate(value);
  return d ? `${d.getDate()} ${MONTHS[d.getMonth()]} ${d.getFullYear()}` : "";
};

/** « 12 oct. 2026 » */
export const formatDateShort = (value) => {
  const d = toDate(value);
  return d ? `${d.getDate()} ${MONTHS_SHORT[d.getMonth()]} ${d.getFullYear()}` : "";
};

/** « il y a 2 h », « hier », « il y a 3 j », « il y a 1 sem. » */
export const timeAgo = (value) => {
  const d = toDate(value);
  if (!d) return "";
  const minutes = Math.max(0, Math.round((Date.now() - d.getTime()) / 60000));
  if (minutes < 60) return `il y a ${Math.max(1, minutes)} min`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `il y a ${hours} h`;
  const days = Math.floor(hours / 24);
  if (days < 2) return "hier";
  if (days < 7) return `il y a ${days} j`;
  if (days < 30) return `il y a ${Math.floor(days / 7)} sem.`;
  return formatDateShort(value);
};

export const getInitials = (name = "") =>
  name.split(" ").filter(Boolean).slice(0, 2).map((w) => w[0]).join("").toUpperCase();

/** 670123456 → « 670 12 34 56 » */
export const formatPhoneLocal = (digits = "") => digits.replace(/(\d{3})(\d{2})(\d{2})(\d{2})/, "$1 $2 $3 $4");
