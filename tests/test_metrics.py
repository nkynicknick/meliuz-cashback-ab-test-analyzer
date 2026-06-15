from src.cleaning import load_and_clean_csv
from src.metrics import add_business_metrics, summarize_by_variant


df = load_and_clean_csv("data/raw/dataset_01_parceiroA.csv")
df = add_business_metrics(df)

summary = summarize_by_variant(df)

print("Métricas adicionadas com sucesso!")
print()
print("Primeiras linhas com métricas:")
print(
    df[
        [
            "Data",
            "Grupos de usuários",
            "compradores",
            "comissão",
            "cashback",
            "vendas totais",
            "receita_liquida",
            "margem_liquida",
            "cashback_rate",
            "ticket_medio",
        ]
    ].head()
)

print()
print("Resumo por variante:")
print(summary)