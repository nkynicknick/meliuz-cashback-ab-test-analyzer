import pandas as pd
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

WEBHOOK_URL = os.getenv("SHEETS_WEBHOOK_URL") # O link está no .env

from src.formatting import (
    format_currency_brl,
    format_percent,
    format_date,
)


def build_test_description(metadata):
    """
    Cria uma descrição curta do teste analisado.
    """

    variants = ", ".join(metadata["variants"])

    return (
        f"Teste A/B de cashback do {metadata['partner']} com "
        f"{metadata['number_of_variants']} variantes ({variants}), "
        f"observado de {format_date(metadata['period_start'])} "
        f"a {format_date(metadata['period_end'])}."
    )


def build_result_summary(analysis_result):
    """
    Cria um resumo textual do resultado do teste.
    """

    decision = analysis_result["decision"]

    result = (
        f"{decision['recommended_variant']} apresentou a maior receita líquida "
        f"({format_currency_brl(decision['primary_metric_value'])})"
    )

    if decision.get("winning_variant_margin") is not None:
        result += (
            f", com margem líquida de "
            f"{format_percent(decision['winning_variant_margin'])}"
        )

    relative_advantage = decision.get("relative_advantage_vs_runner_up")

    if relative_advantage is not None:
        result += (
            f" e vantagem de {format_percent(relative_advantage)} "
            "contra a segunda melhor variante"
        )

    result += "."

    return result


def build_tracker_row(analysis_result, report_path=None):
    """
    Constrói uma linha consolidada para o tracker de testes A/B.

    Essa linha resume:
    - nome do teste;
    - descrição;
    - parceiro;
    - período;
    - decisão;
    - variante recomendada;
    - métrica primária;
    - alertas;
    - caminho do relatório.
    """

    metadata = analysis_result["metadata"]
    decision = analysis_result["decision"]

    row = {
        "test_name": metadata["test_name"],
        "description": build_test_description(metadata),
        "partner": metadata["partner"],
        "source_file": metadata["source_file"],
        "period_start": metadata["period_start"].strftime("%Y-%m-%d"),
        "period_end": metadata["period_end"].strftime("%Y-%m-%d"),
        "number_of_variants": metadata["number_of_variants"],
        "variants": ", ".join(metadata["variants"]),
        "result": build_result_summary(analysis_result),
        "decision": decision["decision"],
        "decision_status": decision["decision_status"],
        "recommended_variant": decision["recommended_variant"],
        "primary_metric": decision["primary_metric"],
        "primary_metric_value": decision["primary_metric_value"],
        "primary_metric_value_formatted": format_currency_brl(
            decision["primary_metric_value"]
        ),
        "warnings": " | ".join(decision["warnings"]),
        "report_path": str(report_path) if report_path is not None else "",
    }

    return row


def register_analysis(analysis_result, report_path=None, tracker_path="outputs/ab_tests_tracker.csv"):
    """
    Registra uma análise no tracker CSV.

    Se o mesmo teste já existir no tracker, a linha antiga é substituída.
    Isso evita duplicatas quando rodamos o pipeline mais de uma vez.
    """

    tracker_path = Path(tracker_path)
    tracker_path.parent.mkdir(parents=True, exist_ok=True)

    new_row = build_tracker_row(
        analysis_result=analysis_result,
        report_path=report_path
    )

    # INÍCIO DA INTEGRAÇÃO COM GOOGLE SHEETS
    if WEBHOOK_URL:
        try:
            print("Enviando dados para o Google Sheets...")
            resposta = requests.post(WEBHOOK_URL, json=new_row)

            if resposta.status_code == 200:
                print("Salvo na planilha com sucesso")
            else:
                print(f"Erro ao salvar na planilha. Status: {resposta.status_code}")

        except Exception as erro:
            print(f"Aviso: Não foi possível conectar ao Google Sheets. Erro: {erro}")
    else:
        print("Webhook do Google Sheets não configurado. Salvando apenas no CSV local.")
    # FIM DA INTEGRAÇÃO

    new_row_df = pd.DataFrame([new_row])

    if tracker_path.exists():
        tracker_df = pd.read_csv(tracker_path)

        if {"test_name", "source_file"}.issubset(tracker_df.columns):
            duplicated_test = (
                (tracker_df["test_name"] == new_row["test_name"])
                & (tracker_df["source_file"] == new_row["source_file"])
            )

            tracker_df = tracker_df.loc[~duplicated_test]

        tracker_df = pd.concat([tracker_df, new_row_df], ignore_index=True)

    else:
        tracker_df = new_row_df

    tracker_df.to_csv(tracker_path, index=False, encoding="utf-8-sig")

    return tracker_path