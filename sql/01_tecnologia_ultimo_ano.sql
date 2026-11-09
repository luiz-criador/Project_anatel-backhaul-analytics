-- Capacidade e taxa de ocupação por tecnologia no ano mais recente
WITH u AS (SELECT MAX(ano) AS a FROM backhaul)
SELECT tecnologia,
       ROUND(SUM(cap_total), 1)      AS cap_total,
       ROUND(SUM(cap_ocupada), 1)    AS cap_ocupada,
       ROUND(SUM(cap_disponivel), 1) AS cap_disponivel,
       ROUND(100.0 * SUM(cap_ocupada) / SUM(cap_total), 2) AS taxa_ocupacao_pct,
       COUNT(DISTINCT id_municipio)  AS municipios
FROM backhaul, u
WHERE ano = u.a
GROUP BY tecnologia
HAVING SUM(cap_total) > 0
ORDER BY taxa_ocupacao_pct DESC;
