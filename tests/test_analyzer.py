from src.analyzer import analyze_ab_test


files = [
    "data/raw/dataset_01_parceiroA.csv",
    "data/raw/dataset_02_parceiroB.csv",
    "data/raw/dataset_03_parceiroC.csv",
]


for file_path in files:
    print("=" * 80)
    print(f"Analisando: {file_path}")
    print("=" * 80)

    result = analyze_ab_test(file_path)

    metadata = result["metadata"]
    summary = result["summary"]
    decision = result["decision"]

    print()
    print("Metadados:")
    print(metadata)

    print()
    print("Resumo por variante:")
    print(summary)

    print()
    print("Decisão:")
    print(decision["decision"])

    print()
    print("Alertas:")
    for warning in decision["warnings"]:
        print("-", warning)

    print()