from src.cleaning import load_and_clean_csv
from src.metrics import add_business_metrics, summarize_by_variant
from src.decision import choose_winning_variant


files = [
    "data/raw/dataset_01_parceiroA.csv",
    "data/raw/dataset_02_parceiroB.csv",
    "data/raw/dataset_03_parceiroC.csv",
]


for file_path in files:
    print("=" * 80)
    print(f"Arquivo: {file_path}")
    print("=" * 80)

    df = load_and_clean_csv(file_path)
    df = add_business_metrics(df)

    summary = summarize_by_variant(df)
    decision = choose_winning_variant(summary)

    print()
    print("Resumo por variante:")
    print(summary)

    print()
    print("Decisão:")
    print(decision["decision"])

    print()
    print("Justificativas:")
    for item in decision["rationale"]:
        print("-", item)

    print()
    print("Alertas:")
    for warning in decision["warnings"]:
        print("-", warning)

    print()