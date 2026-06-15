from pathlib import Path

from src.formatting import (
    format_currency_brl,
    format_percent,
    format_integer,
    format_date,
)


def build_summary_table(summary):
    """
    Cria uma tabela Markdown (melhor pro Git) com as principais métricas por variante.
    """

    headers = [
        "Variante",
        "Compradores",
        "GMV",
        "Comissão",
        "Cashback",
        "Receita líquida",
        "Margem líquida",
        "Cashback rate",
        "Ticket médio",
        "Receita líquida / comprador",
    ]

    lines = []

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for _, row in summary.iterrows():
        line = [
            row["Grupos de usuários"],
            format_integer(row["compradores"]),
            format_currency_brl(row["vendas_totais"]),
            format_currency_brl(row["comissao"]),
            format_currency_brl(row["cashback"]),
            format_currency_brl(row["receita_liquida"]),
            format_percent(row["margem_liquida"]),
            format_percent(row["cashback_rate"]),
            format_currency_brl(row["ticket_medio"]),
            format_currency_brl(row["receita_liquida_por_comprador"]),
        ]

        lines.append("| " + " | ".join(line) + " |")

    return "\n".join(lines)


def build_markdown_report(analysis_result):
    """
    Monta o texto completo do relatório em Markdown.
    """

    metadata = analysis_result["metadata"]
    summary = analysis_result["summary"]
    decision = analysis_result["decision"]

    report_lines = []

    report_lines.append(f"# Relatório do teste A/B — {metadata['test_name']}")
    report_lines.append("")

    report_lines.append("## 1. Visão geral")
    report_lines.append("")
    report_lines.append(f"- Parceiro: {metadata['partner']}")
    report_lines.append(f"- Arquivo analisado: `{metadata['source_file']}`")
    report_lines.append(
        f"- Período analisado: {format_date(metadata['period_start'])} "
        f"a {format_date(metadata['period_end'])}"
    )
    report_lines.append(f"- Linhas analisadas: {format_integer(metadata['total_rows'])}")
    report_lines.append(f"- Número de variantes: {metadata['number_of_variants']}")
    report_lines.append(f"- Variantes: {', '.join(metadata['variants'])}")
    report_lines.append("")

    report_lines.append("## 2. Recomendação")
    report_lines.append("")
    report_lines.append(f"**Decisão:** {decision['decision']}")
    report_lines.append("")
    report_lines.append(
        f"**Métrica primária:** {decision['primary_metric']} "
        f"({format_currency_brl(decision['primary_metric_value'])})"
    )
    report_lines.append("")

    report_lines.append("## 3. Justificativa")
    report_lines.append("")

    for item in decision["rationale"]:
        report_lines.append(f"- {item}")

    report_lines.append("")

    report_lines.append("## 4. Resumo por variante")
    report_lines.append("")
    report_lines.append(build_summary_table(summary))
    report_lines.append("")

    report_lines.append("## 5. Alertas e limitações")
    report_lines.append("")

    for warning in decision["warnings"]:
        report_lines.append(f"- {warning}")

    report_lines.append("")

    report_lines.append("## 6. Observação metodológica")
    report_lines.append("")
    report_lines.append(
        "A decisão usa receita líquida como métrica primária, definida como "
        "comissão menos cashback. Métricas de volume, margem e eficiência são "
        "usadas como apoio para interpretar trade-offs entre crescimento observado "
        "e rentabilidade."
    )
    report_lines.append("")
    report_lines.append(
        "Como os datasets não informam o número de usuários expostos por grupo, "
        "a análise não estima conversão real. Portanto, compradores e GMV são "
        "tratados como medidas de volume observado, não como taxa de conversão."
    )
    report_lines.append("")

    return "\n".join(report_lines)


def write_markdown_report(analysis_result, output_dir="reports"):
    """
    Salva o relatório Markdown em disco.
    """

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    test_name = analysis_result["metadata"]["test_name"]
    output_path = output_dir / f"{test_name}_report.md"

    report_text = build_markdown_report(analysis_result)

    output_path.write_text(report_text, encoding="utf-8")

    return output_path