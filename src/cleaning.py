from pathlib import Path
import unicodedata

import pandas as pd

# Colunas oficiais que o nosso pipeline espera usar internamente.
REQUIRED_COLUMNS = [
    "Data",
    "Grupos de usuários",
    "Parceiro",
    "compradores",
    "comissão",
    "cashback",
    "vendas totais",
]


# Colunas que representam dinheiro e precisam ser convertidas para número.
MONEY_COLUMNS = [
    "comissão",
    "cashback",
    "vendas totais",
]


# Pequenas variações aceitáveis nos nomes das colunas.
# A chave é o nome "normalizado"; o valor é o nome oficial usado no pipeline.
COLUMN_ALIASES = {
    "data": "Data",
    "grupo de usuarios": "Grupos de usuários",
    "grupos de usuarios": "Grupos de usuários",
    "grupos de usuário": "Grupos de usuários",
    "parceiro": "Parceiro",
    "compradores": "compradores",
    "comprador": "compradores",
    "comissao": "comissão",
    "comissão": "comissão",
    "cashback": "cashback",
    "vendas totais": "vendas totais",
    "venda total": "vendas totais",
}


def normalize_text(text):
    """
    Normaliza textos para comparação.

    Exemplo:
    "  Comissão  " -> "comissao"
    "Vendas Totais" -> "vendas totais"
    "Grupos_de_Usuários" -> "grupos de usuarios"
    """

    text = str(text).strip().lower()

    # Remove acentos.
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))

    # Trata separadores comuns.
    text = text.replace("_", " ")
    text = text.replace("-", " ")

    # Remove espaços duplicados.
    text = " ".join(text.split())

    return text


def standardize_column_names(df):
    """
    Padroniza os nomes das colunas para o formato oficial do pipeline.

    Exemplo:
    "data" vira "Data"
    "comissao" vira "comissão"
    "venda total" vira "vendas totais"
    """

    rename_map = {}

    for column in df.columns:
        normalized_column = normalize_text(column)

        if normalized_column in COLUMN_ALIASES:
            rename_map[column] = COLUMN_ALIASES[normalized_column]

    df = df.rename(columns=rename_map)

    return df


def validate_schema(df):
    """
    Verifica se todas as colunas obrigatórias existem.
    """

    missing_columns = []

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            missing_columns.append(column)

    # Precisamos dessas colunas para o nosso pipeline funcionar corretamente. O teste A/B não tem como ser analisado se alguma delas estiver faltando.
    if missing_columns:
        raise ValueError(
            f"Colunas obrigatórias ausentes no CSV: {missing_columns}"
        )


def parse_brl(value):
    """
    Converte valores monetários no padrão brasileiro para float.

    Exemplos:
    "R$ 10.273"     -> 10273.0
    "R$ 10.273,50"  -> 10273.50
    "10273"         -> 10273.0

    Premissa:
    valores monetários do case estão em reais (R$), usando padrão pt_BR.
    Essa premissa é necessária pois, sem ela, não temos como diferenciar "10.273" como milhar (BR) ou como decimal (US).
    """

    if pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip()

    if text == "":
        return None

    text = text.replace("R$", "")
    text = text.replace(" ", "")
    text = text.replace("\xa0", "")

    # Padrão brasileiro:
    # ponto = separador de milhar
    # vírgula = separador decimal
    text = text.replace(".", "")
    text = text.replace(",", ".")

    return float(text)


def validate_missing_values(df):
    """
    Verifica se existem valores nulos nas colunas obrigatórias.
    """

    missing = df[REQUIRED_COLUMNS].isna().sum()
    missing = missing[missing > 0]

    if not missing.empty:
        raise ValueError(
            f"Valores ausentes encontrados nas colunas: {missing.to_dict()}"
        )


def validate_duplicates(df):
    """
    Verifica se existe mais de uma linha para a mesma combinação:
    Data + Grupo + Parceiro.
    """

    duplicated_rows = df.duplicated(
        subset=["Data", "Grupos de usuários", "Parceiro"]
    )

    if duplicated_rows.any():
        duplicated_sample = df.loc[
            duplicated_rows,
            ["Data", "Grupos de usuários", "Parceiro"]
        ]

        raise ValueError(
            "Foram encontradas linhas duplicadas por Data + Grupo + Parceiro:\n"
            f"{duplicated_sample}"
        )


def validate_non_negative_values(df):
    """
    Verifica se compradores, comissão, cashback ou vendas totais possuem valores negativos.
    """

    numeric_columns = ["compradores"] + MONEY_COLUMNS

    for column in numeric_columns:
        if (df[column] < 0).any():
            raise ValueError(
                f"Foram encontrados valores negativos na coluna: {column}"
            )


def load_csv_with_fallback_encoding(file_path):
    """
    Não sabemos de antemão se o arquivo está em UTF-8 ou Latin-1.
    Isso pode fazer com que saiam coisas como "ComissÃ£o" em vez de "Comissão".
    """

    try:
        return pd.read_csv(file_path, encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(file_path, encoding="latin1")


def load_and_clean_csv(file_path):
    """
    Lê um CSV bruto do teste A/B e devolve um DataFrame limpo.

    Saída:
    - colunas padronizadas;
    - datas convertidas;
    - compradores como inteiro (número inteiro de pessoas);
    - dinheiro como float;
    - sem nulos nas colunas obrigatórias;
    - sem duplicatas Data + Grupo + Parceiro (se houver duas observações distintas para a mesma combinação, é melhor falhar do que tentar adivinhar qual é a correta);
    - sem valores negativos.
    """

    file_path = Path(file_path)

    # Verificação de existência do arquivo
    if not file_path.exists(): 
        raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

    # Tenta ler o CSV primeiro como UTF-8, e se falhar, tenta Latin1. Isso ajuda a lidar com arquivos que podem ter sido salvos com diferentes codificações.
    df = load_csv_with_fallback_encoding(file_path) 

    # Padroniza os nomes das colunas, para lidar com variações como "comissao" vs "comissão" ou "data" vs "Data".
    df = standardize_column_names(df) 

    # Verifica se todas as colunas obrigatórias estão presentes, após padronizar os nomes.
    validate_schema(df) 

    # Mantemos apenas as colunas necessárias para a análise.
    # Se o CSV tiver colunas extras, elas são ignoradas.
    extra_columns = [
        column for column in df.columns
        if column not in REQUIRED_COLUMNS
    ]

    if extra_columns:
        print(f"Aviso: colunas extras ignoradas na análise: {extra_columns}")

    df = df[REQUIRED_COLUMNS].copy()

    # Limpa espaços em branco e converte para string, para evitar problemas de formatação.
    df["Grupos de usuários"] = df["Grupos de usuários"].astype(str).str.strip()
    df["Parceiro"] = df["Parceiro"].astype(str).str.strip()

    # Converte a coluna "Data" para datetime. Se tiver um formato inválido, é melhor falhar aqui do que tentar adivinhar a data correta.
    df["Data"] = pd.to_datetime(df["Data"], errors="raise")

    # Aqui, "compradores" deve ser um número inteiro, representando o número de pessoas. Se tiver casas decimais, provavelmente é um erro no CSV.
    df["compradores"] = pd.to_numeric(
        df["compradores"],
        errors="raise"
    ).astype(int)

    # Converte as colunas de dinheiro para float, usando a função de parsing que lida com o formato brasileiro.
    for column in MONEY_COLUMNS:
        df[column] = df[column].apply(parse_brl)
        df[column] = pd.to_numeric(df[column], errors="raise")

    # Validações finais para garantir que os dados estão consistentes e prontos para análise.
    validate_missing_values(df)
    validate_duplicates(df)
    validate_non_negative_values(df)

    # Ordena o DataFrame por Data, Parceiro e Grupos de usuários para facilitar a leitura e análise.
    df = df.sort_values(
        by=["Data", "Parceiro", "Grupos de usuários"]
    ).reset_index(drop=True)

    return df