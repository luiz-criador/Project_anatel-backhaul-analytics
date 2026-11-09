-- Evolução anual de capacidade e ocupação por tecnologia
SELECT ano, tecnologia,
       ROUND(SUM(cap_total), 1)   AS cap_total,
       ROUND(SUM(cap_ocupada), 1) AS cap_ocupada,
       ROUND(100.0 * SUM(cap_ocupada) / SUM(cap_total), 2) AS taxa_ocupacao_pct,
       ROUND(100.0 * (SUM(cap_total) - LAG(SUM(cap_total)) OVER (PARTITION BY tecnologia ORDER BY ano))
             / LAG(SUM(cap_total)) OVER (PARTITION BY tecnologia ORDER BY ano), 2) AS crescimento_cap_pct
FROM backhaul
GROUP BY ano, tecnologia
HAVING SUM(cap_total) > 0
ORDER BY tecnologia, ano;
