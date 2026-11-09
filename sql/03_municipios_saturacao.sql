-- Taxa de ocupação por município (ano mais recente) com classificação de risco
-- Critério do projeto: >= 90% Crítico | >= 80% Alerta | demais Normal
WITH u AS (SELECT MAX(ano) AS a FROM backhaul),
m AS (
    SELECT uf, id_municipio, municipio,
           SUM(cap_total) AS cap_total, SUM(cap_ocupada) AS cap_ocupada,
           SUM(cap_disponivel) AS cap_disponivel
    FROM backhaul, u
    WHERE ano = u.a
    GROUP BY uf, id_municipio, municipio
)
SELECT uf, id_municipio, municipio,
       ROUND(cap_total, 1) AS cap_total, ROUND(cap_ocupada, 1) AS cap_ocupada,
       ROUND(cap_disponivel, 1) AS cap_disponivel,
       ROUND(100.0 * cap_ocupada / cap_total, 2) AS taxa_ocupacao_pct,
       CASE WHEN 100.0 * cap_ocupada / cap_total >= 90 THEN 'Crítico'
            WHEN 100.0 * cap_ocupada / cap_total >= 80 THEN 'Alerta'
            ELSE 'Normal' END AS status
FROM m
WHERE cap_total > 0
ORDER BY taxa_ocupacao_pct DESC;
