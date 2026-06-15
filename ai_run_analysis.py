import argparse
from pathlib import Path

from src.ai_interpreter import interpret_user_request
from src.analyzer import analyze_ab_test
from src.report_writer import write_markdown_report
from src.tracker import register_analysis
from src.formatting import format_currency_brl, format_percent


def build_ai_response(result, interpreted_request, report_path=None, tracker_path=None):
    """
    Monta uma resposta executiva depois que o pipeline roda.
    """

    metadata = result["metadata"]
    decision = result["decision"]

    lines = []

    lines.append(f"Análise concluída para {metadata['partner']}.")
    lines.append("")
    lines.append(f"Recomendação: {decision['decision']}.")
    lines.append("")

    lines.append("Justificativa:")
    lines.append(
        f"- A variante recomendada foi {decision['recommended_variant']}."
    )
    lines.append(
        f"- Receita líquida da variante vencedora: "
        f"{format_currency_brl(decision['primary_metric_value'])}."
    )

    if decision.get("winning_variant_margin") is not None:
        lines.append(
            f"- Margem líquida da variante vencedora: "
            f"{format_percent(decision['winning_variant_margin'])}."
        )

    if decision.get("relative_advantage_vs_runner_up") is not None:
        lines.append(
            f"- Vantagem contra a segunda melhor variante: "
            f"{format_percent(decision['relative_advantage_vs_runner_up'])}."
        )

    if decision["warnings"]:
        lines.append("")
        lines.append("Alertas:")
        for warning in decision["warnings"]:
            lines.append(f"- {warning}")

    lines.append("")
    lines.append("Arquivos gerados:")

    if report_path:
        lines.append(f"- Relatório: {report_path}")
    else:
        lines.append("- Relatório: não gerado.")

    if tracker_path:
        lines.append(f"- Tracker: {tracker_path}")
    else:
        lines.append("- Tracker: não atualizado.")

    lines.append("")
    lines.append("Interpretação do pedido pela IA:")
    lines.append(f"- Arquivo analisado: {interpreted_request.file_path}")
    lines.append(
        f"- Vantagem mínima considerada: "
        f"{format_percent(interpreted_request.min_relative_advantage)}"
    )
    lines.append(f"- Gerar relatório: {interpreted_request.generate_report}")
    lines.append(f"- Registrar tracker: {interpreted_request.register_tracker}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Executa a análise A/B a partir de um pedido em linguagem natural."
    )

    parser.add_argument(
        "--request",
        required=True,
        help="Pedido em linguagem natural."
    )

    args = parser.parse_args()

    try:
        interpreted_request = interpret_user_request(args.request)

    except Exception as erro:
        print("Não foi possível usar a camada AI-native no momento.")
        print()
        print("A chamada ao Gemini falhou antes de interpretar o pedido.")
        print("Isso pode acontecer por instabilidade temporária, alta demanda do modelo, chave inválida ou problema de conexão.")
        print()
        print("Detalhe técnico:")
        print(erro)
        print()
        print("Você ainda pode rodar o modo determinístico, por exemplo:")
        print("python run_analysis.py --file data/raw/dataset_01_parceiroA.csv")
        return

    if not interpreted_request.is_valid_request:
        print("Não consegui interpretar o pedido.")
        print()

        if interpreted_request.clarification_message:
            print(interpreted_request.clarification_message)
        else:
            print(
                "Informe Parceiro A, Parceiro B, Parceiro C "
                "ou um caminho .csv válido."
            )

        return

    if not interpreted_request.file_path:
        print("Nenhum arquivo CSV foi identificado no pedido.")
        print("Informe Parceiro A, Parceiro B, Parceiro C ou um caminho .csv válido.")
        return

    file_path = Path(interpreted_request.file_path)

    if not file_path.exists():
        print(f"O arquivo interpretado pela IA não existe: {file_path}")
        return

    if not file_path.is_file() or file_path.suffix.lower() != ".csv":
        print(f"O caminho interpretado não é um arquivo CSV válido: {file_path}")
        return

    result = analyze_ab_test(
        file_path=interpreted_request.file_path,
        min_relative_advantage=interpreted_request.min_relative_advantage,
    )

    report_path = None
    tracker_path = None

    if interpreted_request.generate_report:
        report_path = write_markdown_report(result)

    if interpreted_request.register_tracker:
        tracker_path = register_analysis(
            result,
            report_path=report_path,
        )

    response = build_ai_response(
        result=result,
        interpreted_request=interpreted_request,
        report_path=report_path,
        tracker_path=tracker_path,
    )

    print(response)


if __name__ == "__main__":
    main()