export function getPasswordScore(v) {
  if (!v) return 0;
  if (v.length < 8 || !/\d/.test(v)) return 1;
  const rich = v.length >= 10 && (/[A-Z]/.test(v) || /[^A-Za-z0-9]/.test(v));
  return rich ? 3 : 2;
}
