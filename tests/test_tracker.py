import pandas as pd

from src.analyzer import analyze_ab_test
from src.report_writer import write_markdown_report
from src.tracker import register_analysis


files = [
    "data/raw/dataset_01_parceiroA.csv",
    "data/raw/dataset_02_parceiroB.csv",
    "data/raw/dataset_03_parceiroC.csv",
]


for file_path in files:
    result = analyze_ab_test(file_path)
    report_path = write_markdown_report(result)
    tracker_path = register_analysis(result, report_path=report_path)

    print(f"Teste registrado no tracker: {file_path}")


print()
print(f"Tracker atualizado: {tracker_path}")
print()

tracker_df = pd.read_csv(tracker_path)

print(
    tracker_df[
        [
            "test_name",
            "partner",
            "decision",
            "recommended_variant",
            "primary_metric_value_formatted",
            "report_path",
        ]
    ]
)