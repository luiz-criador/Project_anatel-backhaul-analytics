# 🌐 Saturação da Rede de Transporte (Backhaul) no Brasil

Análise de dados abertos da **Anatel** sobre capacidade de **backhaul** (rede de transporte
que liga as redes de acesso ao núcleo da operadora). O projeto identifica **onde a rede está
mais ocupada, quais tecnologias e operadoras têm mais folga** e quais municípios exigem
atenção, com foco no estado do Rio de Janeiro.

**Stack:** Python • Pandas • SQL (SQLite) • Matplotlib • Power BI

## 🎯 Perguntas de negócio
1. Qual a taxa de ocupação do backhaul por tecnologia (fibra, rádio, satélite etc.)?
2. Quais operadoras têm mais capacidade e mais folga?
3. Quais municípios estão **saturados** (≥ 80% de ocupação) ou **críticos** (≥ 90%)?
4. Como a ocupação evoluiu ao longo dos anos?
5. Como está o Rio de Janeiro frente às demais UFs?

## 📐 Definições
- **Taxa de ocupação** = capacidade ocupada ÷ capacidade de backhaul
- **Status do município:** Crítico ≥ 90% • Alerta ≥ 80% • Normal < 80%
  (critério definido neste projeto; ajuste em `sql/03_*.sql` e `src/analise.py`)
- Análises "atuais" usam o **ano mais recente** do arquivo, para não somar o mesmo
  município em vários anos.
- A unidade das capacidades e o significado de `situacao` e `ano_atendimento` seguem o
  **dicionário de dados da Anatel** (confira e documente aqui: `[unidade]`).

## 🗂️ Estrutura
```
├── data/raw/               # CSV da Anatel (não vai pro Git)
├── data/lookup/            # (opcional) municipios.csv com id_municipio;municipio
├── sql/                    # 8 consultas (CTEs, window functions, checagem de qualidade)
├── src/
│   ├── etl_load.py         # limpeza + carga em SQLite + perfil dos dados
│   ├── analise.py          # roda o SQL, exporta CSVs e gera gráficos
│   └── generate_sample_data.py   # amostra FICTÍCIA para testes
├── outputs/graficos/       # PNGs
├── outputs/powerbi/        # CSVs para o Power BI
├── powerbi/GUIA_DASHBOARD.md
└── docs/                   # prints do dashboard
```

## 📥 Dados
Fonte: Anatel – Dados Abertos (https://www.gov.br/anatel/pt-br/dados/dados-abertos),
dataset de **Backhaul**. Colunas esperadas:
`sigla_uf, id_municipio, situacao, ano_atendimento, concessionaria, tecnologia,
capacidade_backhaul, capacidade_ocupada, capacidade_disponivel`.

O arquivo traz só o **código IBGE** do município. Para mostrar nomes nos gráficos, crie
`data/lookup/municipios.csv` com duas colunas (`id_municipio;municipio`), usando a tabela
de municípios do IBGE. Sem esse arquivo, o projeto funciona mostrando os códigos.

## ▶️ Como rodar
```bash
pip install -r requirements.txt

# Teste com amostra FICTÍCIA
python src/generate_sample_data.py
python src/etl_load.py --input data/sample
python src/analise.py

# Dados reais (CSV em data/raw)
python src/etl_load.py
python src/analise.py
```

## 🧪 Qualidade dos dados
`sql/07_qualidade_dados.sql` verifica: capacidade nula/zero, ocupada > total e
ocupada + disponível ≠ total. **Documente aqui o que encontrou** e como tratou.

## 🔍 Principais achados
> Preencha com os números reais (3 a 5 bullets).

- A tecnologia mais ocupada é **[tecnologia]**, com **[X]%** de ocupação
- **[N]** municípios (**[X]%**) estão em nível crítico; **[M]** em alerta
- No RJ, **[município]** tem a maior ocupação (**[X]%**)
- A operadora com maior folga é **[operadora]**

## 💡 Por que esse projeto?
Trabalho há 6 anos com redes e infraestrutura de telecom. Capacidade de backhaul é o
tipo de gargalo que aparece em campo como lentidão e instabilidade para o cliente. Aqui
transformo isso em dados para priorizar onde investir em expansão.

## 🚀 Próximos passos
- [ ] Cruzar com **acessos de banda larga** (acessos por Mbps de backhaul)
- [ ] Cruzar com população do IBGE
- [ ] Incluir indicadores de qualidade e reclamações

## 👤 Autor
**Luiz Carlos** — Profissional de TI em transição para Análise de Dados
LinkedIn: [[https://www.linkedin.com/in/devluiiz/)] • GitHub: [[https://github.com/luiz-criador]
