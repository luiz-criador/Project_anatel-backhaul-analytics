-- Ranking de operadoras: capacidade, folga e ocupação (ano mais recente)
WITH u AS (SELECT MAX(ano) AS a FROM backhaul)
SELECT concessionaria,
       ROUND(SUM(cap_total), 1)      AS cap_total,
       ROUND(SUM(cap_disponivel), 1) AS cap_disponivel,
       ROUND(100.0 * SUM(cap_ocupada) / SUM(cap_total), 2) AS taxa_ocupacao_pct,
       COUNT(DISTINCT id_municipio)  AS municipios_atendidos,
       RANK() OVER (ORDER BY SUM(cap_total) DESC) AS ranking_capacidade
FROM backhaul, u
WHERE ano = u.a
GROUP BY concessionaria
HAVING SUM(cap_total) > 0
ORDER BY cap_total DESC;
