import pandas as pd

"""
1. Crescimento observado: vendeu mais? trouxe mais compradores? 
   Como não temos usuários expostos por grupo, não medimos conversão real. 
   Medimos apenas volume observado: compradores e GMV (venda total).
2. Rentabilidade: sobrou mais dinheiro para o Méliuz?
3. Eficiência: o cashback adicional se pagou? O cashback adicional gerou aumento suficiente de compradores/GMV para compensar o custo adicional?
4. Qualidade dos compradores: o ticket médio aumentou? O cashback por comprador aumentou?
5. Consistência: a receita líquida diária se manteve estável ou aumentou?

"""


def safe_divide(numerator, denominator):
    """
    Faz uma divisão protegida.

    Se houver divisão por zero, infinito ou valor nulo, retorna 0.
    Funciona tanto para números simples quanto para colunas do pandas.
    """

    try:
        result = numerator / denominator
    except ZeroDivisionError:
        return 0

    if isinstance(result, pd.Series):
        result = result.replace([float("inf"), -float("inf")], 0)
        result = result.fillna(0)

    else:
        if pd.isna(result) or result in [float("inf"), -float("inf")]:
            result = 0

    return result


def add_business_metrics(df):
    """
    Recebe um DataFrame limpo e adiciona métricas de negócio.

    Métricas criadas:
    - receita_liquida = comissão - cashback                             receita_liquida               -> quanto sobra
    - margem_liquida = receita_liquida / vendas totais                  margem_liquida                -> quanto sobra por real vendido
    - take_rate = comissão / vendas totais                              take_rate                     -> quanto o Méliuz ganha por real vendido
    - cashback_rate = cashback / vendas totais                          cashback_rate                 -> quão agressivo foi o cashback
    - ticket_medio = vendas totais / compradores                        ticket_medio                  -> qualidade/tamanho médio da compra
    - cashback_por_comprador = cashback / compradores                   cashback_por_comprador        -> quanto cashback cada comprador recebeu em média
    - receita_liquida_por_comprador = receita_liquida / compradores     receita_liquida_por_comprador -> quanto sobra por comprador

    1. Crescimento observado -> compradores, vendas totais
    2. Rentabilidade         -> receita_liquida, margem_liquida
    3. Eficiência            -> cashback_rate, cashback_por_comprador, receita_liquida_por_comprador
    4. Qualidade             -> ticket_medio
    5. Consistência          -> receita_liquida_media_diaria, receita_liquida_desvio_diario

    Seria ótimo ter: conversão = compradores / usuários expostos, mas não temos os usuários expostos.
    """

    df = df.copy()

    df["receita_liquida"] = df["comissão"] - df["cashback"]

    df["margem_liquida"] = safe_divide(
        df["receita_liquida"],
        df["vendas totais"]
    )

    df["take_rate"] = safe_divide(
        df["comissão"],
        df["vendas totais"]
    )

    df["cashback_rate"] = safe_divide(
        df["cashback"],
        df["vendas totais"]
    )

    df["ticket_medio"] = safe_divide(
        df["vendas totais"],
        df["compradores"]
    )

    df["cashback_por_comprador"] = safe_divide(
        df["cashback"],
        df["compradores"]
    )

    df["receita_liquida_por_comprador"] = safe_divide(
        df["receita_liquida"],
        df["compradores"]
    )

    return df


def summarize_by_variant(df):
    """
    Consolida os resultados por variante do teste; pega o histórico diário e resume tudo por grupo.

    ANTES
    Data        Grupo     compradores   comissão   cashback   vendas totais
    2011-01-01  Grupo 1   ...
    2011-01-02  Grupo 1   ...
    2011-01-03  Grupo 1   ...
    2011-01-01  Grupo 2   ...
    2011-01-02  Grupo 2   ...

    DEPOIS
    Grupo     compradores totais   comissão total   cashback total   receita líquida total
    Grupo 1   ...
    Grupo 2   ...
    Grupo 3   ...

    Cada linha da saída representa um grupo/variante.
    Essa tabela será a base para a decisão de qual grupo escalar.
    """

    summary = (
        df
        .groupby("Grupos de usuários", as_index=False)
        .agg(
            parceiro=("Parceiro", "first"),
            data_inicio=("Data", "min"),
            data_fim=("Data", "max"),
            dias_observados=("Data", "nunique"),
            compradores=("compradores", "sum"),
            comissao=("comissão", "sum"),
            cashback=("cashback", "sum"),
            vendas_totais=("vendas totais", "sum"),
            receita_liquida=("receita_liquida", "sum"),
            receita_liquida_media_diaria=("receita_liquida", "mean"),
            receita_liquida_desvio_diario=("receita_liquida", "std"),
        )
    )

    summary["receita_liquida_desvio_diario"] = (
        summary["receita_liquida_desvio_diario"].fillna(0) # Se só tiver um dia, o desvio padrão é NaN. Mas nesse caso, a receita líquida diária é constante, então o desvio é 0.
    )

    summary["margem_liquida"] = safe_divide(
        summary["receita_liquida"],
        summary["vendas_totais"]
    )

    summary["take_rate"] = safe_divide(
        summary["comissao"],
        summary["vendas_totais"]
    )

    summary["cashback_rate"] = safe_divide(
        summary["cashback"],
        summary["vendas_totais"]
    )

    summary["ticket_medio"] = safe_divide(
        summary["vendas_totais"],
        summary["compradores"]
    )

    summary["cashback_por_comprador"] = safe_divide(
        summary["cashback"],
        summary["compradores"]
    )

    summary["receita_liquida_por_comprador"] = safe_divide(
        summary["receita_liquida"],
        summary["compradores"]
    )

    # Ordena do melhor para o pior pela métrica mais importante: receita líquida total; grupo mais rentável.
    # Isso ainda não é a decisão final, mas prepara o terreno para o decision.py que vai comparar os grupos e escolher o melhor.
    summary = summary.sort_values( 
        by="receita_liquida",
        ascending=False
    ).reset_index(drop=True)

    return summary

    """
    dados diários limpos
            ↓
    agrupa por variante/grupo
            ↓
    soma compradores, comissão, cashback, GMV e receita líquida
            ↓
    calcula métricas consolidadas
            ↓
    ordena pela receita líquida
            ↓
    devolve tabela comparativa por grupo
    """