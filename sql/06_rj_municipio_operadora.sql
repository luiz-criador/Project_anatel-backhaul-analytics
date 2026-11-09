-- Foco RJ: ocupação por município e operadora (ano mais recente)
WITH u AS (SELECT MAX(ano) AS a FROM backhaul)
SELECT municipio, id_municipio, concessionaria,
       ROUND(SUM(cap_total), 1) AS cap_total,
       ROUND(100.0 * SUM(cap_ocupada) / SUM(cap_total), 2) AS taxa_ocupacao_pct,
       RANK() OVER (PARTITION BY municipio ORDER BY SUM(cap_ocupada) / SUM(cap_total) DESC) AS posicao_mais_saturada
FROM backhaul, u
WHERE uf = 'RJ' AND ano = u.a
GROUP BY municipio, id_municipio, concessionaria
HAVING SUM(cap_total) > 0
ORDER BY municipio, posicao_mais_saturada;
