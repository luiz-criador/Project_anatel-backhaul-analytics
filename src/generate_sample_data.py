"""
Gera uma AMOSTRA FICTÍCIA com as mesmas colunas do CSV de backhaul que você baixou.
Serve só para testar o pipeline. Os números NÃO são reais.
"""
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(7)
OUT = Path(__file__).resolve().parents[1] / "data" / "sample" / "backhaul_FICTICIO.csv"

UFS_MUN = [("RJ", 3304557, 10), ("RJ", 3303302, 3), ("RJ", 3301702, 2), ("RJ", 3303500, 2),
           ("RJ", 3304904, 2.5), ("SP", 3550308, 18), ("MG", 3106200, 5), ("BA", 2927408, 4),
           ("CE", 2304400, 4), ("PR", 4106902, 4), ("RS", 4314902, 3.5), ("PE", 2611606, 3),
           ("AM", 1302603, 2), ("DF", 5300108, 5), ("PA", 1501402, 2), ("MT", 5103403, 1.5)]
CONC = ["CLARO S.A.", "VIVO", "TIM S.A.", "OI S.A.", "BRISANET", "PROVEDOR REGIONAL A"]
TEC = [("Fibra Óptica", 1.0), ("Rádio", 0.35), ("Satélite", 0.08), ("Cabo Metálico", 0.2)]

rows = []
for ano in range(2019, 2025):
    for uf, cod, peso in UFS_MUN:
        for c in CONC:
            for tec, tw in TEC:
                if rng.random() < 0.15:
                    continue
                total = 1000 * peso * tw * rng.lognormal(0, 0.4) * (1 + 0.15 * (ano - 2019))
                taxa = np.clip(rng.normal(0.52 + 0.03 * (ano - 2019) + (0.1 if tec == "Rádio" else 0), 0.15), 0.05, 0.99)
                ocup = total * taxa
                rows.append([uf, cod, "Em operação", ano, c, tec,
                             round(total, 2), round(ocup, 2), round(total - ocup, 2)])

df = pd.DataFrame(rows, columns=["sigla_uf", "id_municipio", "situacao", "ano_atendimento",
                                 "concessionaria", "tecnologia", "capacidade_backhaul",
                                 "capacidade_ocupada", "capacidade_disponivel"])
# injeta alguns erros de qualidade para testar a checagem
idx = rng.choice(len(df), 8, replace=False)
df.loc[idx, "capacidade_ocupada"] = df.loc[idx, "capacidade_backhaul"] * 1.3
OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"Amostra FICTÍCIA gerada: {OUT} ({len(df):,} linhas)")
