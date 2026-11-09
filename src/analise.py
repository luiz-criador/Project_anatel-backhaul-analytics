"""
Roda as consultas SQL (sql/*.sql), exporta CSVs para o Power BI e gera gráficos.
Uso: python src/analise.py
"""
import sqlite3
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "anatel_backhaul.db"
SQL_DIR = ROOT / "sql"
OUT_CSV = ROOT / "outputs" / "powerbi"
OUT_IMG = ROOT / "outputs" / "graficos"
for p in (OUT_CSV, OUT_IMG):
    p.mkdir(parents=True, exist_ok=True)

DESTAQUE = "CLARO"
ALERTA, CRITICO = 80, 90   # limites de ocupação (%) usados na classificação


def roda_sql():
    con = sqlite3.connect(DB)
    res = {}
    for f in sorted(SQL_DIR.glob("*.sql")):
        df = pd.read_sql_query(f.read_text(encoding="utf-8"), con)
        df.to_csv(OUT_CSV / f"{f.stem}.csv", index=False, encoding="utf-8-sig", sep=";")
        res[f.stem] = df
        print(f"{f.name:<36} -> {len(df):>7,} linhas")
    con.close()
    return res


def estilo(ax, titulo, xlabel="", ylabel=""):
    ax.set_title(titulo, loc="left", fontsize=12, fontweight="bold")
    ax.set_xlabel(xlabel); ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)


def cor_taxa(v):
    return "#d62828" if v >= CRITICO else "#f4a261" if v >= ALERTA else "#2a9d8f"


def g_tecnologia(df):
    d = df.sort_values("taxa_ocupacao_pct")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(d["tecnologia"], d["taxa_ocupacao_pct"], color=[cor_taxa(v) for v in d["taxa_ocupacao_pct"]])
    for y, v in enumerate(d["taxa_ocupacao_pct"]):
        ax.text(v + 0.5, y, f"{v:.1f}%", va="center", fontsize=9)
    ax.axvline(ALERTA, ls="--", color="gray", lw=1)
    estilo(ax, "Taxa de ocupação do backhaul por tecnologia (ano mais recente)", "% da capacidade ocupada")
    ax.set_xlim(0, 105)
    fig.tight_layout(); fig.savefig(OUT_IMG / "01_ocupacao_tecnologia.png", dpi=150); plt.close(fig)


def g_operadoras(df):
    d = df.sort_values("taxa_ocupacao_pct")
    cores = ["#d62828" if DESTAQUE in c.upper() else "#9aa5b1" for c in d["concessionaria"]]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.barh(d["concessionaria"], d["taxa_ocupacao_pct"], color=cores)
    for y, v in enumerate(d["taxa_ocupacao_pct"]):
        ax.text(v + 0.5, y, f"{v:.1f}%", va="center", fontsize=9)
    estilo(ax, "Taxa de ocupação por operadora (ano mais recente)", "% da capacidade ocupada")
    fig.tight_layout(); fig.savefig(OUT_IMG / "02_ocupacao_operadoras.png", dpi=150); plt.close(fig)


def g_municipios(df):
    base = df[df["cap_total"] >= df["cap_total"].median()]
    d = base.nlargest(15, "taxa_ocupacao_pct").sort_values("taxa_ocupacao_pct")
    fig, ax = plt.subplots(figsize=(8, 5.5))
    rot = d["municipio"].astype(str) + " (" + d["uf"] + ")"
    ax.barh(rot, d["taxa_ocupacao_pct"], color=[cor_taxa(v) for v in d["taxa_ocupacao_pct"]])
    estilo(ax, "15 municípios com backhaul mais saturado", "% da capacidade ocupada")
    ax.text(0, -0.12, "Considera municípios com capacidade acima da mediana.",
            transform=ax.transAxes, fontsize=8, color="gray")
    fig.tight_layout(); fig.savefig(OUT_IMG / "03_municipios_saturados.png", dpi=150); plt.close(fig)


def g_evolucao(df):
    p = df.pivot(index="ano", columns="tecnologia", values="taxa_ocupacao_pct")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    p.plot(ax=ax, marker="o", lw=2)
    ax.axhline(ALERTA, ls="--", color="gray", lw=1)
    estilo(ax, "Evolução da taxa de ocupação por tecnologia", "", "% ocupado")
    ax.legend(frameon=False, fontsize=8, loc="center left", bbox_to_anchor=(1.01, 0.5))
    ax.set_xticks(p.index)
    fig.tight_layout(); fig.savefig(OUT_IMG / "04_evolucao_ocupacao.png", dpi=150); plt.close(fig)


def resumo(r):
    t, o, m, q = r["01_tecnologia_ultimo_ano"], r["02_ranking_operadoras"], r["03_municipios_saturacao"], r["07_qualidade_dados"]
    print("\n=== RESUMO ===")
    print(f"Tecnologia mais ocupada: {t.iloc[0]['tecnologia']} ({t.iloc[0]['taxa_ocupacao_pct']}%)")
    print(f"Tecnologia com mais folga: {t.iloc[-1]['tecnologia']} ({t.iloc[-1]['taxa_ocupacao_pct']}%)")
    print(f"Operadora com maior capacidade: {o.iloc[0]['concessionaria']}")
    n = len(m)
    crit, alert = (m["status"] == "Crítico").sum(), (m["status"] == "Alerta").sum()
    print(f"Municípios analisados: {n:,} | Crítico: {crit} ({100*crit/n:.1f}%) | Alerta: {alert} ({100*alert/n:.1f}%)")
    print("\nQualidade dos dados:")
    print(q.to_string(index=False))


if __name__ == "__main__":
    r = roda_sql()
    g_tecnologia(r["01_tecnologia_ultimo_ano"])
    g_operadoras(r["02_ranking_operadoras"])
    g_municipios(r["03_municipios_saturacao"])
    g_evolucao(r["04_evolucao_anual_tecnologia"])
    resumo(r)
    print(f"\nCSVs: {OUT_CSV}\nGráficos: {OUT_IMG}")
