import argparse

from src.analyzer import analyze_ab_test
from src.report_writer import write_markdown_report
from src.tracker import register_analysis


def main():
    parser = argparse.ArgumentParser(
        description="Analisa um teste A/B de cashback e gera recomendação."
    )

    parser.add_argument(
        "--file",
        required=True,
        help="Caminho do arquivo CSV a ser analisado."
    )

    parser.add_argument(
        "--reports-dir",
        default="reports",
        help="Pasta onde o relatório Markdown será salvo."
    )

    parser.add_argument(
        "--tracker-path",
        default="outputs/ab_tests_tracker.csv",
        help="Caminho do arquivo CSV de tracker."
    )

    parser.add_argument(
        "--min-relative-advantage",
        type=float,
        default=0.02,
        help="Vantagem relativa mínima para considerar uma variante vencedora."
    )

    args = parser.parse_args()

    result = analyze_ab_test(
        args.file,
        min_relative_advantage=args.min_relative_advantage
    )

    report_path = write_markdown_report(
        result,
        output_dir=args.reports_dir
    )

    tracker_path = register_analysis(
        result,
        report_path=report_path,
        tracker_path=args.tracker_path
    )

    decision = result["decision"]

    print("Análise concluída com sucesso.")
    print()
    print(f"Arquivo analisado: {args.file}")
    print(f"Parceiro: {result['metadata']['partner']}")
    print(f"Decisão: {decision['decision']}")
    print(f"Variante recomendada: {decision['recommended_variant']}")
    print(f"Relatório gerado: {report_path}")
    print(f"Tracker atualizado: {tracker_path}")

    if decision["warnings"]:
        print()
        print("Alertas:")
        for warning in decision["warnings"]:
            print(f"- {warning}")


if __name__ == "__main__":
    main()