# Méliuz Cashback A/B Test Analyzer

Projeto desenvolvido para automatizar a análise de testes A/B de cashback e recomendar qual variante deve ser escalada para 100% do tráfego.

A solução foi construída com foco em:

* reprodutibilidade;
* robustez contra dados inconsistentes;
* decisão auditável;
* geração automática de relatório;
* registro consolidado em tracker CSV;
* integração opcional com Google Sheets;
* camada AI-native para execução por linguagem natural.

---

## 1. Problema

O objetivo é responder, para cada teste A/B de cashback:

> Dado esse teste A/B, qual variante de cashback devemos escalar para 100% do tráfego?

---

## 2. Visão geral da solução

O projeto pode ser executado de duas formas:

### 2.1. Modo determinístico

Execução direta via terminal, informando o caminho do CSV:

```bash
python run_analysis.py --file data/raw/dataset_01_parceiroA.csv
```

Esse modo não exige chave de API nem configuração externa.

Ele gera:

* recomendação no terminal;
* relatório Markdown em `reports/`;
* tracker CSV em `outputs/ab_tests_tracker.csv`;
* envio opcional para Google Sheets, se `SHEETS_WEBHOOK_URL` estiver configurado no `.env`.

Fluxo:

```text
Execução direta via terminal
        ↓
Pipeline Python
        ↓
Relatório + tracker CSV + Google Sheets (opcional)
        ↓
Resposta no terminal
```

### 2.2. Modo AI-native

Execução por linguagem natural usando Gemini API:

```bash
python ai_run_analysis.py --request "Analise o teste do Parceiro A, gere relatório e registre no tracker."
```

Nesse modo, o Gemini interpreta o pedido do usuário e transforma a solicitação em parâmetros estruturados para o pipeline.

A IA não calcula métricas e não decide a variante vencedora. A decisão continua sendo feita pelo programa.

Fluxo:

```text
Pedido em linguagem natural
        ↓
Gemini interpreta o pedido
        ↓
Parâmetros estruturados
        ↓
Pipeline Python
        ↓
Relatório + tracker CSV + Google Sheets (opcional)
        ↓
Resposta executiva no terminal
```

---

## 3. Arquitetura

```text
app/
│
├── run_analysis.py
├── ai_run_analysis.py
├── requirements.txt
├── .env.example
│
├── data/
│   └── raw/
│       ├── dataset_01_parceiroA.csv (local recomendado para armazenar os dados)
│       ├── dataset_02_parceiroB.csv (local recomendado para armazenar os dados)
│       └── dataset_03_parceiroC.csv (local recomendado para armazenar os dados)
│ 
├── reports/
│   ├── dataset_01_parceiroA_report.md (após execução do programa, o relatório aparecerá aqui)
│   ├── dataset_02_parceiroB_report.md (após execução do programa, o relatório aparecerá aqui)
│   └── dataset_03_parceiroC_report.md (após execução do programa, o relatório aparecerá aqui)
│
├── outputs/
│   └── ab_tests_tracker.csv (após execução do programa, o tracker aparecerá aqui)
│
└── src/
    ├── cleaning.py
    ├── metrics.py
    ├── decision.py
    ├── analyzer.py
    ├── formatting.py
    ├── report_writer.py
    ├── tracker.py
    └── ai_interpreter.py
```

### Responsabilidade de cada módulo

| Arquivo              | Responsabilidade                                         |
| -------------------- | -------------------------------------------------------- |
| `cleaning.py`        | Lê, padroniza e valida o CSV                             |
| `metrics.py`         | Calcula métricas de negócio                              |
| `decision.py`        | Escolhe a variante recomendada                           |
| `analyzer.py`        | Orquestra limpeza, métricas e decisão                    |
| `formatting.py`      | Padroniza moeda, percentual, data e inteiros             |
| `report_writer.py`   | Gera relatórios Markdown                                 |
| `tracker.py`         | Atualiza tracker CSV e, opcionalmente, Google Sheets     |
| `ai_interpreter.py`  | Usa Gemini para interpretar pedidos em linguagem natural |
| `run_analysis.py`    | Entrada tradicional via terminal                         |
| `ai_run_analysis.py` | Entrada AI-native via linguagem natural                  |

---

## 4. Instalação

Antes de instalar as dependências, verifique se o Python está instalado no computador:

```bash
python --version
```

Este projeto foi desenvolvido para **Python 3.10 ou superior**. Também é recomendado utilizar um ambiente virtual (`venv`) para isolar as dependências do projeto.


### 4.1. Criar ambiente virtual

```bash
python -m venv .venv
```

No Windows PowerShell:

```bash
.venv\Scripts\Activate.ps1
```

### 4.2. Instalar dependências

```bash
pip install -r requirements.txt
```

---

## 5. Configuração de ambiente

O projeto funciona sem nenhuma chave externa (API).

Para recursos opcionais (uso de Gemini e Sheets), crie um arquivo `.env` na raiz do projeto com base em `.env.example`.

Exemplo:

```env
SHEETS_WEBHOOK_URL=cole_a_url_do_webhook_aqui
GEMINI_API_KEY=cole_sua_chave_gemini_aqui
GEMINI_MODEL=gemini-2.5-flash
```

NOTA: caso você tenha acesso a outro modelo de Gemini, ou, quiser utilizar OUTRA máquina (não recomendado), você deverá substituir `gemini-2.5-flash` pelo modelo respectivo.  

### Variáveis

| Variável             | Obrigatória? | Uso                                             |
| -------------------- | ------------ | ----------------------------------------------- |
| `SHEETS_WEBHOOK_URL` | Não          | Enviar registros para Google Sheets via webhook |
| `GEMINI_API_KEY`     | Não          | Ativar modo AI-native com Gemini                |
| `GEMINI_MODEL`       | Não          | Definir modelo Gemini usado na interpretação    |


---

## 6. Como usar

### 6.1. Modo determinístico

EXEMPLO

Parceiro A:

```bash
python run_analysis.py --file data/raw/dataset_01_parceiroA.csv
```

Parceiro B:

```bash
python run_analysis.py --file data/raw/dataset_02_parceiroB.csv
```

Parceiro C:

```bash
python run_analysis.py --file data/raw/dataset_03_parceiroC.csv
```

Também é possível ajustar a vantagem relativa mínima exigida (parâmetro escolhido como abordagem para solucionar o problema) para considerar uma variante vencedora:

```bash
python run_analysis.py --file data/raw/dataset_01_parceiroA.csv --min-relative-advantage 0.05
```

Nesse exemplo, a vantagem mínima é de 5%.

---

### 6.2. Modo AI-native

Exemplo 1:

```bash
python ai_run_analysis.py --request "Analise o teste do Parceiro A, gere relatório e registre no tracker."
```

Exemplo 2:

```bash
python ai_run_analysis.py --request "Analise o Parceiro B usando 5% como vantagem mínima."
```

Exemplo 3:

```bash
python ai_run_analysis.py --request "Analise o teste do Parceiro C sem relatório."
```

A IA interpreta o pedido e identifica:

* arquivo CSV;
* vantagem relativa mínima;
* se deve gerar relatório;
* se deve registrar no tracker.

Depois disso, o pipeline Python executa a análise.

---

### 6.3. Exemplo de execução

### Exemplo usando o modo determinístico para analisar o dataset do Parceiro C:

```bash
python run_analysis.py --file data/raw/dataset_03_parceiroC.csv
```

Saída esperada:

```text
Enviando dados para o Google Sheets...
Salvo na planilha com sucesso
Análise concluída com sucesso.

Arquivo analisado: data/raw/dataset_03_parceiroC.csv
Parceiro: Parceiro C
Decisão: ESCALAR Grupo 1
Variante recomendada: Grupo 1
Relatório gerado: reports/dataset_03_parceiroC_report.md
Tracker atualizado: outputs/ab_tests_tracker.csv

Alertas:
- O dataset não contém usuários expostos por grupo; portanto, a análise não estima conversão real.
```


### Exemplo usando o modo AI-native com linguagem natural para analisar o dataset do Parceiro A:

```bash
python ai_run_analysis.py --request "Analise o teste do Parceiro A"
```

```text
Enviando dados para o Google Sheets...
Salvo na planilha com sucesso
Análise concluída para Parceiro A.

Recomendação: ESCALAR Grupo 1.

Justificativa:
- A variante recomendada foi Grupo 1.
- Receita líquida da variante vencedora: R$ 404.711,00.
- Margem líquida da variante vencedora: 7,22%.
- Vantagem contra a segunda melhor variante: 13,20%.

Alertas:
- A variante recomendada não foi a que trouxe mais compradores. A maior quantidade de compradores ocorreu em Grupo 3.
- A variante recomendada não foi a que gerou maior GMV. O maior GMV ocorreu em Grupo 3.
- O dataset não contém usuários expostos por grupo; portanto, a análise não estima conversão real.

Arquivos gerados:
- Relatório: reports\dataset_01_parceiroA_report.md
- Tracker: outputs\ab_tests_tracker.csv

Interpretação do pedido pela IA:
- Arquivo analisado: data/raw/dataset_01_parceiroA.csv
- Vantagem mínima considerada: 2,00%
- Gerar relatório: True
- Registrar tracker: True
```

---

## 7. Entrada esperada

O CSV deve conter, minimamente, as seguintes colunas:

| Coluna               | Descrição               |
| -------------------- | ----------------------- |
| `Data`               | Data da observação      |
| `Grupos de usuários` | Variante/grupo do teste |
| `Parceiro`           | Nome do parceiro        |
| `compradores`        | Número de compradores   |
| `comissão`           | Comissão gerada         |
| `cashback`           | Cashback concedido      |
| `vendas totais`      | GMV/vendas totais       |

O pipeline também tenta lidar com pequenas variações de nomes de colunas, acentos e separadores.

---

## 8. Métricas calculadas

A métrica primária de decisão (função objetivo) é:

```text
receita_liquida = comissão - cashback
```

Também são calculadas métricas auxiliares:

| Métrica                         | Interpretação                       |
| ------------------------------- | ----------------------------------- |
| `compradores`                   | Volume observado de compradores     |
| `vendas_totais`                 | GMV observado                       |
| `margem_liquida`                | Receita líquida sobre vendas totais |
| `take_rate`                     | Comissão sobre vendas totais        |
| `cashback_rate`                 | Cashback sobre vendas totais        |
| `ticket_medio`                  | Vendas totais por comprador         |
| `cashback_por_comprador`        | Cashback médio por comprador        |
| `receita_liquida_por_comprador` | Receita líquida média por comprador |
| `receita_liquida_media_diaria`  | Receita líquida média diária        |
| `receita_liquida_desvio_diario` | Variação diária da receita líquida  |

---

## 9. Regra de decisão

A variante recomendada é, em geral, aquela com maior receita líquida total.

A lógica considera:

1. rentabilidade total;
2. margem líquida;
3. volume observado de compradores;
4. GMV (venda total);
5. eficiência do cashback;
6. diferença relativa contra a segunda melhor variante;
7. alertas e limitações dos dados.

Se a vantagem entre a melhor e a segunda melhor variante for muito pequena, o pipeline pode marcar o resultado como inconclusivo, de acordo com o parâmetro `min_relative_advantage`.

Esse parâmetro é uma regra heurística de negócio, não um teste estatístico formal.

---

## 10. Resultados dos datasets fornecidos

### Parceiro A

Recomendação:

```text
ESCALAR Grupo 1
```

Resumo:

* Grupo 1 teve a maior receita líquida.
* Grupo 3 teve mais compradores e maior GMV.
* Existe trade-off entre rentabilidade e crescimento observado.

### Parceiro B

Recomendação:

```text
ESCALAR Grupo 1
```

Resumo:

* Grupo 1 apresentou maior receita líquida.
* Também liderou em compradores e GMV.
* Foi o caso mais dominante entre os datasets fornecidos.

### Parceiro C

Recomendação:

```text
ESCALAR Grupo 1
```

Resumo:

* Grupo 1 apresentou receita líquida positiva.
* Grupo 2 teve receita líquida igual a zero.
* O aumento de cashback não se pagou.

---

## 11. Relatórios gerados

Os relatórios individuais são salvos em:

```text
reports/
```

Cada relatório contém:

* visão geral do teste;
* decisão recomendada;
* justificativa;
* tabela comparativa por variante;
* alertas e limitações;
* observação metodológica.

Exemplo:

```text
reports/dataset_01_parceiroA_report.md
```

---

## 12. Tracker

O tracker consolidado é salvo (e atualizado) em:

```text
outputs/ab_tests_tracker.csv
```

Cada linha representa um teste analisado e contém, entre outros campos:

* nome do teste;
* descrição;
* parceiro;
* período;
* variantes;
* resultado;
* decisão;
* variante recomendada;
* métrica primária;
* alertas;
* caminho do relatório.

Se `SHEETS_WEBHOOK_URL` estiver configurado no `.env`, o mesmo registro também é enviado para uma planilha Google Sheets via Apps Script (Webhook).

Se `SHEETS_WEBHOOK_URL` não estiver configurado, o projeto salva apenas o CSV local (na pasta outputs/) e continua funcionando normalmente.

---

## 13. Integração com Google Sheets

A integração com Google Sheets é opcional.

Ela foi implementada por meio de um webhook do Google Apps Script. O pipeline envia uma requisição HTTP `POST` com a linha do tracker em JSON. O Apps Script recebe os dados e insere/atualiza a planilha.

Essa abordagem evita a necessidade de credenciais complexas de Google Cloud no projeto local. Mas, em contrapartida, é menos seguro, e, dessa forma, torna-se necessária a utilização de um `.env`.

Para usar:

1. criar uma planilha Google;
2. criar um Apps Script (na aba extensões);
3. colocar como Web App;
4. configurar a execução e o acesso de terceiros com o devido cuidado;
5. publicar (deploy);
6. colocar a URL no `.env`:

```env
SHEETS_WEBHOOK_URL=cole_a_url_do_webhook_aqui
```

---

## 14. Camada AI-native

A camada AI-native usa Gemini API para interpretar linguagem natural.

Exemplo de execução no terminal:

```bash
python ai_run_analysis.py --request "Analise o Parceiro B usando 5% como vantagem mínima."
```

O Gemini retorna uma estrutura com:

```text
file_path
min_relative_advantage
generate_report
register_tracker
user_intent_summary
```

Depois disso, o pipeline Python executa a análise.

Ponto importante:

```text
A IA não calcula métricas nem escolhe manualmente a variante vencedora.
A IA apenas interpreta o pedido e aciona o pipeline determinístico.
```

Isso mantém a solução auditável e reduz risco de decisões opacas.

---

## 15. Limitações

A principal limitação dos datasets é a ausência do número de usuários expostos por grupo.

Por isso, o pipeline não calcula conversão real.

Compradores e GMV são tratados como medidas de volume observado, não como taxa de conversão.

Exemplo de métrica desejável, mas indisponível:

```text
conversão = compradores / usuários expostos
```

Sem usuários expostos (usuários que viram a possibilidade de cashback), não é possível estimar a taxa de conversão de cada variante.

---

## 16. Segurança

Arquivos sensíveis não devem ser versionados:

```text
.env
credentials/
```

O arquivo `.env.example` pode ser versionado porque contém apenas placeholders.

---

## 17. Resumo da proposta

Esta solução combina:

* pipeline analítico determinístico;
* validação e limpeza de dados;
* cálculo padronizado de métricas;
* regra de decisão explícita;
* relatórios automáticos;
* tracker CSV;
* integração opcional com Google Sheets;
* camada AI-native com Gemini para interface conversacional.

A arquitetura separa claramente:

```text
IA pré-treinada → interpreta o pedido
Python → calcula, decide e registra
```

O projeto mantém a experiência conversacional esperada em uma solução AI-native sem abrir mão de rastreabilidade, reprodutibilidade e controle analítico.
