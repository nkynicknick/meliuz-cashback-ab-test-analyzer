from pathlib import Path

from src.cleaning import load_and_clean_csv
from src.metrics import add_business_metrics, summarize_by_variant
from src.decision import choose_winning_variant


def build_analysis_metadata(file_path, df, summary):
    """
    Cria metadados gerais sobre o teste analisado.

    Esses metadados ajudam depois na geração do relatório e no tracker.
    """

    file_path = Path(file_path)

    partners = df["Parceiro"].unique()

    # Se tiver mais de um parceiro, é um sinal de que o teste A/B não foi bem conduzido, pois cada teste deve ter um único parceiro.
    if len(partners) != 1:
        raise ValueError(
            "O arquivo contém mais de um parceiro. "
            "Este pipeline espera um teste A/B por arquivo."
        )
    # Resumo geral de cada csv
    metadata = {
        "test_name": file_path.stem,
        "source_file": str(file_path),
        "partner": partners[0],
        "period_start": df["Data"].min(),
        "period_end": df["Data"].max(),
        "total_rows": len(df),
        "variants": summary["Grupos de usuários"].tolist(),
        "number_of_variants": len(summary),
        "days_observed": int(df["Data"].nunique()),
    }

    return metadata


def analyze_ab_test(file_path, min_relative_advantage=0.02):
    """
    Executa a análise completa de um teste A/B de cashback.

    Etapas:
    1. Lê e limpa o CSV;
    2. Calcula métricas de negócio linha a linha;
    3. Consolida os resultados por variante;
    4. Escolhe a variante recomendada;
    5. Devolve tudo em um dict organizado.
    """

    clean_df = load_and_clean_csv(file_path)

    enriched_df = add_business_metrics(clean_df)

    summary = summarize_by_variant(enriched_df)

    decision = choose_winning_variant(
        summary,
        min_relative_advantage=min_relative_advantage
    )

    metadata = build_analysis_metadata(
        file_path=file_path,
        df=enriched_df,
        summary=summary
    )

    analysis_result = {
        "metadata": metadata,
        "clean_data": clean_df,
        "enriched_data": enriched_df,
        "summary": summary,
        "decision": decision,
    }

    return analysis_result