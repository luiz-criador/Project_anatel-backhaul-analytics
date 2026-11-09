# Guia do Dashboard no Power BI

## 1. Importar
1. **Obter dados → Texto/CSV** → `outputs/powerbi/08_fato_powerbi.csv` (separador `;`, UTF-8).
2. Power Query: `ano` → Número inteiro; `cap_total`, `cap_ocupada`, `cap_disponivel` → Número decimal.
3. Importe também `03_municipios_saturacao.csv` e `02_ranking_operadoras.csv`.

## 2. Medidas (DAX)
```DAX
Capacidade Total      = SUM(fato[cap_total])
Capacidade Ocupada    = SUM(fato[cap_ocupada])
Capacidade Disponível = SUM(fato[cap_disponivel])

Taxa de Ocupação % = DIVIDE([Capacidade Ocupada], [Capacidade Total])

Taxa Ano Anterior % =
CALCULATE([Taxa de Ocupação %], SAMEPERIODLASTYEAR(dAno[Date]))   -- se usar tabela de datas

Municípios Críticos =
COUNTROWS(
    FILTER(
        VALUES(fato[id_municipio]),
        [Taxa de Ocupação %] >= 0.90
    )
)

Municípios em Alerta =
COUNTROWS(
    FILTER(
        VALUES(fato[id_municipio]),
        [Taxa de Ocupação %] >= 0.80 && [Taxa de Ocupação %] < 0.90
    )
)

Total de Municípios = DISTINCTCOUNT(fato[id_municipio])

% Municípios em Risco =
DIVIDE([Municípios Críticos] + [Municípios em Alerta], [Total de Municípios])
```
Se não quiser tabela de datas, use `ano` direto e dispense `Taxa Ano Anterior %`
(a evolução anual já está na consulta `04`).

> Formate `Taxa de Ocupação %` como porcentagem. Use **formatação condicional** de cor
> (verde < 80%, laranja 80–90%, vermelho ≥ 90%).

## 3. Layout (3 páginas)

**Página 1 – Visão geral**
- Cartões: Capacidade Total, Taxa de Ocupação %, Municípios Críticos, % Municípios em Risco
- Barras: Taxa de Ocupação por tecnologia
- Linhas: Taxa de Ocupação por ano, legenda = tecnologia
- Segmentações: Ano, UF, Situação

**Página 2 – Operadoras**
- Barras: Taxa de Ocupação por operadora (destaque Claro em vermelho)
- Matriz: operadora × tecnologia com Taxa de Ocupação %
- Dispersão: Capacidade Total (x) × Taxa de Ocupação % (y), um ponto por operadora

**Página 3 – Municípios e RJ**
- Tabela: municípios ordenados por Taxa de Ocupação (limite aos 20 maiores)
- Barras: Municípios Críticos por UF
- Filtro UF = RJ + matriz município × operadora
- Caixa de texto com 3 insights escritos por você

## 4. Dicas
- Escreva as **unidades** (conforme o dicionário de dados da Anatel) nos títulos.
- Uma frase de insight por página.
- Salve como `Dashboard_Backhaul_Anatel.pbix` e coloque prints em `docs/`.
