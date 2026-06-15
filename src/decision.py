from src.formatting import format_currency_brl, format_percent

def calculate_relative_difference(best_value, comparison_value):
    """
    Calcula a diferença percentual entre o melhor valor e o valor de comparação.

    Exemplo:
    best_value = 120
    comparison_value = 100
    retorno = 0.20, ou seja, 20%
    """
    
    if comparison_value == 0:
        return None # Evita divisão por zero.

    return (best_value - comparison_value) / abs(comparison_value)


def choose_winning_variant(summary, min_relative_advantage=0.02):
    """
    Escolhe a variante recomendada para escalar.

    Regra principal:
    - A métrica primária é receita líquida total;
    - A variante vencedora é a que maximiza receita líquida;
    - Se a diferença para a segunda melhor for "muito pequena", marcamos como inconclusivo (temos poucas métricas e dados pequenos);
    - Métricas de volume, margem e cashback são usadas como contexto para a recomendação.

    Parâmetros:
    - summary: DataFrame consolidado por variante;
    - min_relative_advantage: diferença mínima desejada entre a melhor e a segunda melhor variante;
      Valor padrão: 0.02 = 2% (pode ser ajustado, contudo, 2% não é significância estatística. É uma regra heurística/econômica).
    """

    # Tratamento simples de um edge case. 
    if summary.empty:
        raise ValueError("O resumo por variante está vazio. Não é possível tomar decisão.")
    ranked = summary.sort_values( 
        by="receita_liquida",
        ascending=False
    ).reset_index(drop=True)

    best = ranked.iloc[0] # Variante com maior receita líquida total.

    winning_variant = best["Grupos de usuários"] # Nome/ID da variante que ficou em primeiro lugar por receita líquida total.
    partner = best["parceiro"] # Nome do parceiro, que é o mesmo para todas as variantes do mesmo teste A/B.

    best_net_revenue = best["receita_liquida"] # Receita líquida total da variante vencedora.
    best_margin = best["margem_liquida"] # Margem líquida da variante vencedora.
    best_gmv = best["vendas_totais"] # GMV da variante vencedora.
    best_buyers = best["compradores"] # Número de compradores da variante vencedora.

    warnings = [] # Lista de alertas e limitações a serem considerados junto com a decisão.
    rationale = [] # Justificativas para a decisão, que serão apresentadas junto com a recomendação. Aqui explicamos o raciocínio por trás da decisão, destacando os pontos fortes da variante vencedora e as limitações da análise.

    rationale.append(
        f"A variante {winning_variant} apresentou a maior receita líquida total."
    )

    rationale.append(
        f"Receita líquida da variante vencedora: {format_currency_brl(best_net_revenue)}."
    )

    rationale.append(
        f"Margem líquida da variante vencedora: {format_percent(best_margin)}."
    )

    # Caso só exista uma variante, não há comparação real de A/B...
    # Se só houver uma variante, não existe comparação A/B real.
    # Ainda podemos reportar essa variante, mas a recomendação deve vir com alerta.
    if len(ranked) == 1:
        warnings.append(
            "O dataset possui apenas uma variante. Não há comparação A/B real."
        )

        return {
            "partner": partner,
            "recommended_variant": winning_variant,
            "decision": f"ESCALAR {winning_variant}",
            "decision_status": "scale_with_warning",
            "primary_metric": "receita_liquida",
            "primary_metric_value": best_net_revenue,
            "relative_advantage_vs_runner_up": None,
            "rationale": rationale,
            "warnings": warnings,
        }

    runner_up = ranked.iloc[1] # Segunda melhor variante por receita líquida total.
    runner_up_variant = runner_up["Grupos de usuários"] # Nome/ID da variante que ficou em segundo lugar por receita líquida total.
    runner_up_net_revenue = runner_up["receita_liquida"] # Receita líquida total da segunda melhor variante.

    relative_advantage = calculate_relative_difference(
        best_net_revenue,
        runner_up_net_revenue
    )

    # Se a vantagem relativa puder ser calculada, adicionamos isso como parte da justificativa.
    if relative_advantage is not None:
        rationale.append(
            f"A diferença de receita líquida contra a segunda melhor variante "
            f"({runner_up_variant}) foi de {format_percent(relative_advantage)}."
        )

    # Se a melhor variante não tiver receita líquida positiva, não recomendamos escalar, mesmo que seja a melhor.
    if best_net_revenue <= 0:
        decision_status = "do_not_scale"
        decision = (
            f"NÃO ESCALAR {winning_variant} — nenhuma variante apresentou "
            "receita líquida positiva suficiente."
        )
        warnings.append(
            "A melhor variante por receita líquida ainda apresenta resultado líquido não positivo."
        )

    # Se a vantagem relativa for menor que o mínimo desejado, marcamos como inconclusivo, mesmo que a receita líquida seja positiva.
    elif relative_advantage is not None and relative_advantage < min_relative_advantage:
        decision_status = "inconclusive"
        decision = (
            f"RESULTADO INCONCLUSIVO — {winning_variant} foi a melhor variante "
            "por receita líquida, mas a vantagem sobre a segunda melhor é pequena."
        )
        warnings.append(
            "A diferença entre as duas melhores variantes é pequena. Recomenda-se cautela antes de escalar."
        )

    else:
        decision_status = "scale"
        decision = f"ESCALAR {winning_variant}"

    # Checa se a variante mais rentável também foi a maior em volume.
    max_buyers_variant = ranked.loc[
        ranked["compradores"].idxmax(),
        "Grupos de usuários"
    ]

    # Checa se a variante mais rentável também foi a maior em GMV.
    max_gmv_variant = ranked.loc[
        ranked["vendas_totais"].idxmax(),
        "Grupos de usuários"
    ]

    # Se a variante recomendada não for a que trouxe mais compradores, é um alerta importante. 
    # Isso indica um trade-off entre rentabilidade e crescimento observado.
    # A variante recomendada é mais rentável, mas não lidera em volume.
    if winning_variant != max_buyers_variant:
        warnings.append(
            f"A variante recomendada não foi a que trouxe mais compradores. "
            f"A maior quantidade de compradores ocorreu em {max_buyers_variant}."
        )

    # Se a variante recomendada não for a que trouxe mais GMV, é um alerta importante.
    # Isso indica um trade-off entre rentabilidade e crescimento observado.
    # A variante recomendada é mais rentável, mas não lidera em volume.
    if winning_variant != max_gmv_variant:
        warnings.append(
            f"A variante recomendada não foi a que gerou maior GMV. "
            f"O maior GMV ocorreu em {max_gmv_variant}."
        )

    # Limitação importante do dataset.
    warnings.append(
        "O dataset não contém usuários expostos por grupo; portanto, a análise não estima conversão real."
    )

    return {
        "partner": partner,
        "recommended_variant": winning_variant,
        "decision": decision,
        "decision_status": decision_status,
        "primary_metric": "receita_liquida",
        "primary_metric_value": best_net_revenue,
        "runner_up_variant": runner_up_variant,
        "runner_up_primary_metric_value": runner_up_net_revenue,
        "relative_advantage_vs_runner_up": relative_advantage,
        "winning_variant_margin": best_margin,
        "winning_variant_gmv": best_gmv,
        "winning_variant_buyers": best_buyers,
        "rationale": rationale,
        "warnings": warnings,
    }