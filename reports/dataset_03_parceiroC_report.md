# Relatório do teste A/B — dataset_03_parceiroC

## 1. Visão geral

- Parceiro: Parceiro C
- Arquivo analisado: `data\raw\dataset_03_parceiroC.csv`
- Período analisado: 01/07/2011 a 14/08/2011
- Linhas analisadas: 90
- Número de variantes: 2
- Variantes: Grupo 1, Grupo 2

## 2. Recomendação

**Decisão:** ESCALAR Grupo 1

**Métrica primária:** receita_liquida (R$ 34.769,00)

## 3. Justificativa

- A variante Grupo 1 apresentou a maior receita líquida total.
- Receita líquida da variante vencedora: R$ 34.769,00.
- Margem líquida da variante vencedora: 2,00%.

## 4. Resumo por variante

| Variante | Compradores | GMV | Comissão | Cashback | Receita líquida | Margem líquida | Cashback rate | Ticket médio | Receita líquida / comprador |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Grupo 1 | 4.549 | R$ 1.738.460,00 | R$ 121.693,00 | R$ 86.924,00 | R$ 34.769,00 | 2,00% | 5,00% | R$ 382,16 | R$ 7,64 |
| Grupo 2 | 4.522 | R$ 1.685.235,00 | R$ 117.967,00 | R$ 117.967,00 | R$ 0,00 | 0,00% | 7,00% | R$ 372,67 | R$ 0,00 |

## 5. Alertas e limitações

- O dataset não contém usuários expostos por grupo; portanto, a análise não estima conversão real.

## 6. Observação metodológica

A decisão usa receita líquida como métrica primária, definida como comissão menos cashback. Métricas de volume, margem e eficiência são usadas como apoio para interpretar trade-offs entre crescimento observado e rentabilidade.

Como os datasets não informam o número de usuários expostos por grupo, a análise não estima conversão real. Portanto, compradores e GMV são tratados como medidas de volume observado, não como taxa de conversão.
