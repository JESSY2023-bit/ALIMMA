import { useId } from "react";

/** tabs : [{ id, label }] · value : id actif · onChange(id). Flèches ← → pour naviguer. */
export function Tabs({ tabs, value, onChange, label = "Contenu" }) {
  const uid = useId();
  const onKeyDown = (e, i) => {
    if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
    const next = tabs[(i + (e.key === "ArrowRight" ? 1 : -1) + tabs.length) % tabs.length];
    onChange(next.id);
    document.getElementById(`${uid}-${next.id}`)?.focus();
  };
  return (
    <div role="tablist" aria-label={label} className="ui-tabs">
      {tabs.map((t, i) => (
        <button
          key={t.id} id={`${uid}-${t.id}`} role="tab" type="button" className="ui-tabs__tab"
          aria-selected={value === t.id} tabIndex={value === t.id ? 0 : -1}
          onClick={() => onChange(t.id)} onKeyDown={(e) => onKeyDown(e, i)}
        >
          {t.label}
        </button>
      ))}
    </div>
  );
}
