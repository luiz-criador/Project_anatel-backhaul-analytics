"""
ETL do dataset de BACKHAUL da Anatel: lê o(s) CSV(s), padroniza colunas, limpa,
(opcionalmente) junta nomes de municípios e carrega num banco SQLite.

Uso:
    python src/etl_load.py                       # lê data/raw
    python src/etl_load.py --input data/sample   # lê a amostra fictícia
"""
import argparse
import sqlite3
import unicodedata
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "data" / "anatel_backhaul.db"
LOOKUP = ROOT / "data" / "lookup" / "municipios.csv"   # opcional: id_municipio;municipio

COLUNAS = {  # nome normalizado -> nome canônico
    "sigla uf": "uf", "uf": "uf",
    "id municipio": "id_municipio", "codigo ibge municipio": "id_municipio",
    "municipio": "municipio_nome",
    "situacao": "situacao",
    "ano atendimento": "ano", "ano": "ano",
    "concessionaria": "concessionaria", "empresa": "concessionaria",
    "tecnologia": "tecnologia",
    "capacidade backhaul": "cap_total",
    "capacidade ocupada": "cap_ocupada",
    "capacidade disponivel": "cap_disponivel",
}
OBRIGATORIAS = ["uf", "id_municipio", "ano", "concessionaria", "tecnologia",
                "cap_total", "cap_ocupada", "cap_disponivel"]


def normaliza(txt) -> str:
    txt = unicodedata.normalize("NFKD", str(txt)).encode("ascii", "ignore").decode()
    return " ".join(txt.lower().replace("_", " ").split())


def le_csv(path: Path) -> pd.DataFrame:
    for enc in ("utf-8-sig", "latin-1"):
        for sep in (",", ";"):
            try:
                df = pd.read_csv(path, sep=sep, encoding=enc, low_memory=False)
                if df.shape[1] > 3:
                    return df
            except Exception:
                continue
    raise ValueError(f"Não consegui ler {path.name}")


def para_numero(s: pd.Series) -> pd.Series:
    """Converte para número tratando formatos '1234.5' e '1.234,5'."""
    n = pd.to_numeric(s, errors="coerce")
    if s.dtype != object or n.isna().mean() <= s.isna().mean() + 0.01:
        return n
    alt = pd.to_numeric(s.astype(str).str.replace(".", "", regex=False)
                        .str.replace(",", ".", regex=False), errors="coerce")
    return alt if alt.isna().mean() < n.isna().mean() else n


def limpa(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={c: COLUNAS[normaliza(c)] for c in df.columns if normaliza(c) in COLUNAS})
    faltando = [c for c in OBRIGATORIAS if c not in df.columns]
    if faltando:
        raise ValueError(f"Colunas ausentes: {faltando}. Encontradas: {list(df.columns)}")
    if "situacao" not in df.columns:
        df["situacao"] = "N/D"
    for c in ("cap_total", "cap_ocupada", "cap_disponivel"):
        df[c] = para_numero(df[c])
    df["ano"] = pd.to_numeric(df["ano"], errors="coerce")
    df = df.dropna(subset=["ano", "id_municipio"]).copy()
    df["ano"] = df["ano"].astype(int)
    df["id_municipio"] = pd.to_numeric(df["id_municipio"], errors="coerce").astype("Int64").astype(str)
    for c in ("uf", "concessionaria", "tecnologia", "situacao"):
        df[c] = df[c].astype(str).str.strip()
    df["uf"] = df["uf"].str.upper()
    return df.drop_duplicates()


def junta_nomes(df: pd.DataFrame) -> pd.DataFrame:
    if LOOKUP.exists():
        lk = pd.read_csv(LOOKUP, sep=None, engine="python", dtype=str)
        lk.columns = ["id_municipio", "municipio"] + list(lk.columns[2:])
        df = df.merge(lk[["id_municipio", "municipio"]], on="id_municipio", how="left")
        print(f"Nomes de municípios juntados ({lk.shape[0]} no lookup).")
    elif "municipio_nome" in df.columns:
        df["municipio"] = df["municipio_nome"]
    else:
        df["municipio"] = None
    df["municipio"] = df["municipio"].fillna(df["id_municipio"])
    return df.drop(columns=[c for c in ("municipio_nome",) if c in df.columns])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="data/raw")
    args = ap.parse_args()
    pasta = ROOT / args.input
    arquivos = sorted(pasta.glob("*.csv"))
    if not arquivos:
        raise SystemExit(f"Nenhum CSV em {pasta}. Veja o README.")

    df = pd.concat([limpa(le_csv(a)) for a in arquivos], ignore_index=True)
    df = junta_nomes(df)

    print(f"\n{len(arquivos)} arquivo(s) | {len(df):,} linhas | anos {df['ano'].min()}–{df['ano'].max()}")
    print("\n--- PERFIL DOS DADOS (confira com o dicionário da Anatel) ---")
    print("situacao  :", df["situacao"].value_counts().head(8).to_dict())
    print("tecnologia:", df["tecnologia"].value_counts().head(8).to_dict())
    print("nulos     :", df[["cap_total", "cap_ocupada", "cap_disponivel"]].isna().sum().to_dict())

    con = sqlite3.connect(DB)
    df.to_sql("backhaul", con, if_exists="replace", index=False)
    con.executescript("""
        CREATE INDEX IF NOT EXISTS ix_ano ON backhaul(ano);
        CREATE INDEX IF NOT EXISTS ix_uf  ON backhaul(uf);
        CREATE INDEX IF NOT EXISTS ix_mun ON backhaul(id_municipio);
    """)
    con.close()
    print(f"\nBanco criado: {DB}")


if __name__ == "__main__":
    main()
