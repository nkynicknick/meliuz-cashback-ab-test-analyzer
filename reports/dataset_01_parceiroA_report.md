# Relatório do teste A/B — dataset_01_parceiroA

## 1. Visão geral

- Parceiro: Parceiro A
- Arquivo analisado: `data\raw\dataset_01_parceiroA.csv`
- Período analisado: 01/01/2011 a 02/04/2011
- Linhas analisadas: 276
- Número de variantes: 3
- Variantes: Grupo 1, Grupo 2, Grupo 3

## 2. Recomendação

**Decisão:** ESCALAR Grupo 1

**Métrica primária:** receita_liquida (R$ 404.711,00)

## 3. Justificativa

- A variante Grupo 1 apresentou a maior receita líquida total.
- Receita líquida da variante vencedora: R$ 404.711,00.
- Margem líquida da variante vencedora: 7,22%.
- A diferença de receita líquida contra a segunda melhor variante (Grupo 2) foi de 13,20%.

## 4. Resumo por variante

| Variante | Compradores | GMV | Comissão | Cashback | Receita líquida | Margem líquida | Cashback rate | Ticket médio | Receita líquida / comprador |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Grupo 1 | 9.633 | R$ 5.605.173,00 | R$ 638.135,00 | R$ 233.424,00 | R$ 404.711,00 | 7,22% | 4,16% | R$ 581,87 | R$ 42,01 |
| Grupo 2 | 10.814 | R$ 6.423.096,00 | R$ 728.178,00 | R$ 370.659,00 | R$ 357.519,00 | 5,57% | 5,77% | R$ 593,96 | R$ 33,06 |
| Grupo 3 | 11.410 | R$ 6.785.856,00 | R$ 767.887,00 | R$ 503.600,00 | R$ 264.287,00 | 3,89% | 7,42% | R$ 594,73 | R$ 23,16 |

## 5. Alertas e limitações

- A variante recomendada não foi a que trouxe mais compradores. A maior quantidade de compradores ocorreu em Grupo 3.
- A variante recomendada não foi a que gerou maior GMV. O maior GMV ocorreu em Grupo 3.
- O dataset não contém usuários expostos por grupo; portanto, a análise não estima conversão real.

## 6. Observação metodológica

A decisão usa receita líquida como métrica primária, definida como comissão menos cashback. Métricas de volume, margem e eficiência são usadas como apoio para interpretar trade-offs entre crescimento observado e rentabilidade.

Como os datasets não informam o número de usuários expostos por grupo, a análise não estima conversão real. Portanto, compradores e GMV são tratados como medidas de volume observado, não como taxa de conversão.
