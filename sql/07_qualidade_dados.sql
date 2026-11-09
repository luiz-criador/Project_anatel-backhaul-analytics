-- Checagens de qualidade dos dados (documente os achados no README)
SELECT 'total_de_linhas' AS checagem, COUNT(*) AS linhas FROM backhaul
UNION ALL SELECT 'capacidade_total_nula_ou_zero', COUNT(*) FROM backhaul
    WHERE cap_total IS NULL OR cap_total = 0
UNION ALL SELECT 'ocupada_maior_que_total', COUNT(*) FROM backhaul
    WHERE cap_ocupada > cap_total
UNION ALL SELECT 'ocupada+disponivel difere do total (>1%)', COUNT(*) FROM backhaul
    WHERE cap_total > 0 AND ABS(cap_ocupada + cap_disponivel - cap_total) > 0.01 * cap_total;
