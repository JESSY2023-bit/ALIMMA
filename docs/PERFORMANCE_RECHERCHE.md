# Performance de la recherche

La liste publique exécute principalement la requête suivante :

```sql
EXPLAIN ANALYZE
SELECT id FROM annonces
WHERE statut = 'active'
ORDER BY date_publication DESC, id DESC
LIMIT 20;
```

L'index composite `idx_ann_statut_pub` couvre le filtre invariant
`statut = 'active'` et l'ordre de consultation principal. Il évite un tri des
annonces actives lorsque le volume approche 10 000 enregistrements.

La recherche approximative utilise l'opérateur PostgreSQL `%` et les index GIN
`idx_annonces_titre_trgm` et `idx_ann_desc_trgm`, sur le titre et la description.
Avant toute évolution d'index, exécuter cet `EXPLAIN ANALYZE` sur un jeu de données
représentatif de production et conserver le plan dans la revue technique.
