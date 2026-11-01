import { Icon } from "./Icon";

function pagesToShow(page, count) {
  if (count <= 7) return Array.from({ length: count }, (_, i) => i + 1);
  const set = new Set([1, count, page - 1, page, page + 1]);
  const list = [...set].filter((n) => n >= 1 && n <= count).sort((a, b) => a - b);
  return list.flatMap((n, i) => (i > 0 && n - list[i - 1] > 1 ? ["…", n] : [n]));
}

export function Pagination({ page, pageCount, onChange }) {
  if (pageCount <= 1) return null;
  return (
    <nav aria-label="Pagination" className="ui-pag">
      <button type="button" aria-label="Page précédente" disabled={page === 1} onClick={() => onChange(page - 1)}>
        <Icon name="chevron_left" />
      </button>
      {pagesToShow(page, pageCount).map((n, i) =>
        n === "…" ? (
          <span key={`gap-${i}`} aria-hidden="true">…</span>
        ) : (
          <button key={n} type="button" aria-current={n === page ? "page" : undefined} onClick={() => onChange(n)}>{n}</button>
        ),
      )}
      <button type="button" aria-label="Page suivante" disabled={page === pageCount} onClick={() => onChange(page + 1)}>
        <Icon name="chevron_right" />
      </button>
    </nav>
  );
}
