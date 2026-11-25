import { Icon } from "./Icon";

export function getPasswordScore(v) {
  if (!v) return 0;
  if (v.length < 8 || !/\d/.test(v)) return 1;
  const rich = v.length >= 10 && (/[A-Z]/.test(v) || /[^A-Za-z0-9]/.test(v));
  return rich ? 3 : 2;
}

const LABELS = ["", "Faible", "Correct · ajoutez une majuscule ou un symbole pour le renforcer", "Solide"];

/** Jauge à 3 niveaux. rules : [{ label, ok }] pour afficher la liste de critères. */
export function PasswordStrength({ value, rules }) {
  const score = getPasswordScore(value);
  return (
    <div className="ui-strength" data-score={score}>
      <div className="ui-strength__bars" aria-hidden="true"><i /><i /><i /></div>
      <p className="ui-strength__label" aria-live="polite">{score ? LABELS[score] : ""}</p>
      {rules && (
        <ul className="ui-rules">
          {rules.map((r) => (
            <li key={r.label} data-ok={r.ok || undefined}>
              <Icon name="check_circle" filled size={18} />
              {r.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
