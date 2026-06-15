from src.analyzer import analyze_ab_test
from src.report_writer import write_markdown_report


files = [
    "data/raw/dataset_01_parceiroA.csv",
    "data/raw/dataset_02_parceiroB.csv",
    "data/raw/dataset_03_parceiroC.csv",
]


for file_path in files:
    result = analyze_ab_test(file_path)
    report_path = write_markdown_report(result)

    print(f"Relatório gerado: {report_path}")