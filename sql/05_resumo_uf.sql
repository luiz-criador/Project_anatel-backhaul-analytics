-- Resumo por UF no ano mais recente
WITH u AS (SELECT MAX(ano) AS a FROM backhaul)
SELECT uf,
       COUNT(DISTINCT id_municipio) AS municipios,
       ROUND(SUM(cap_total), 1)     AS cap_total,
       ROUND(100.0 * SUM(cap_ocupada) / SUM(cap_total), 2) AS taxa_ocupacao_pct,
       ROUND(SUM(cap_disponivel) / COUNT(DISTINCT id_municipio), 1) AS folga_media_por_municipio
FROM backhaul, u
WHERE ano = u.a
GROUP BY uf
HAVING SUM(cap_total) > 0
ORDER BY taxa_ocupacao_pct DESC;
