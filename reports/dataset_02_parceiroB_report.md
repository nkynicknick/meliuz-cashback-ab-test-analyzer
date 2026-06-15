# Relatório do teste A/B — dataset_02_parceiroB

## 1. Visão geral

- Parceiro: Parceiro B
- Arquivo analisado: `data\raw\dataset_02_parceiroB.csv`
- Período analisado: 01/05/2011 a 30/06/2011
- Linhas analisadas: 183
- Número de variantes: 3
- Variantes: Grupo 1, Grupo 2, Grupo 3

## 2. Recomendação

**Decisão:** ESCALAR Grupo 1

**Métrica primária:** receita_liquida (R$ 286.570,00)

## 3. Justificativa

- A variante Grupo 1 apresentou a maior receita líquida total.
- Receita líquida da variante vencedora: R$ 286.570,00.
- Margem líquida da variante vencedora: 7,00%.
- A diferença de receita líquida contra a segunda melhor variante (Grupo 2) foi de 100,18%.

## 4. Resumo por variante

| Variante | Compradores | GMV | Comissão | Cashback | Receita líquida | Margem líquida | Cashback rate | Ticket médio | Receita líquida / comprador |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Grupo 1 | 7.990 | R$ 4.093.818,00 | R$ 450.321,00 | R$ 163.751,00 | R$ 286.570,00 | 7,00% | 4,00% | R$ 512,37 | R$ 35,87 |
| Grupo 2 | 5.452 | R$ 2.863.019,00 | R$ 314.935,00 | R$ 171.778,00 | R$ 143.157,00 | 5,00% | 6,00% | R$ 525,13 | R$ 26,26 |
| Grupo 3 | 5.029 | R$ 2.629.963,00 | R$ 289.290,00 | R$ 236.697,00 | R$ 52.593,00 | 2,00% | 9,00% | R$ 522,96 | R$ 10,46 |

## 5. Alertas e limitações

- O dataset não contém usuários expostos por grupo; portanto, a análise não estima conversão real.

## 6. Observação metodológica

A decisão usa receita líquida como métrica primária, definida como comissão menos cashback. Métricas de volume, margem e eficiência são usadas como apoio para interpretar trade-offs entre crescimento observado e rentabilidade.

Como os datasets não informam o número de usuários expostos por grupo, a análise não estima conversão real. Portanto, compradores e GMV são tratados como medidas de volume observado, não como taxa de conversão.
