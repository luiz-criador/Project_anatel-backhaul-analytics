-- Tabela fato agregada para o Power BI
SELECT ano, uf, id_municipio, municipio, concessionaria, tecnologia, situacao,
       SUM(cap_total) AS cap_total, SUM(cap_ocupada) AS cap_ocupada,
       SUM(cap_disponivel) AS cap_disponivel
FROM backhaul
GROUP BY ano, uf, id_municipio, municipio, concessionaria, tecnologia, situacao;
