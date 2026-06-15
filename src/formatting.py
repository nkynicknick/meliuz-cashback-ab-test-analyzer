def format_currency_brl(value):
    """
    Formata número em padrão monetário brasileiro. A criação do "formatting.py" torna o programa mais flexível e mais reutilizável. 

    Exemplo:
    404711.0 -> R$ 404.711,00
    """

    if value is None:
        return "N/A"

    formatted = f"R$ {value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted


def format_percent(value):
    """
    Formata número decimal como percentual brasileiro.

    Exemplo:
    0.0722 -> 7,22%
    """

    if value is None:
        return "N/A"

    return f"{value:.2%}".replace(".", ",")


def format_integer(value):
    """
    Formata inteiro com separador de milhar brasileiro.

    Exemplo:
    9633 -> 9.633
    """

    if value is None:
        return "N/A"

    return f"{int(value):,}".replace(",", ".")


def format_date(value):
    """
    Formata datas no padrão brasileiro.
    """

    if value is None:
        return "N/A"

    return value.strftime("%d/%m/%Y")