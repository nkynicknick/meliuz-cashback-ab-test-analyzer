import os
from typing import Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


load_dotenv()


class InterpretedRequest(BaseModel):
    """
    Pedido do usuário convertido em parâmetros estruturados para o pipeline.
    """

    is_valid_request: bool = Field(
        description=(
            "Indica se o pedido contém informação suficiente para identificar "
            "um CSV ou parceiro válido."
        )
    )

    file_path: Optional[str] = Field(
        default=None,
        description="Caminho do arquivo CSV que deve ser analisado."
    )

    min_relative_advantage: float = Field(
        default=0.02,
        description=(
            "Vantagem relativa mínima entre a melhor variante e a segunda melhor. "
            "Exemplo: 0.02 representa 2%."
        ),
    )

    generate_report: bool = Field(
        default=True,
        description="Indica se o relatório Markdown deve ser gerado."
    )

    register_tracker: bool = Field(
        default=True,
        description="Indica se o resultado deve ser registrado no tracker CSV/Sheets."
    )

    user_intent_summary: Optional[str] = Field(
        default=None,
        description="Resumo curto do que o usuário pediu."
    )

    clarification_message: Optional[str] = Field(
        default=None,
        description=(
            "Mensagem curta explicando o que falta quando o pedido não é válido."
        )
    )


AVAILABLE_DATASETS = """
Datasets disponíveis:

- Parceiro A: data/raw/dataset_01_parceiroA.csv
- Parceiro B: data/raw/dataset_02_parceiroB.csv
- Parceiro C: data/raw/dataset_03_parceiroC.csv
"""


def get_gemini_client():
    """
    Cria o cliente Gemini usando a chave configurada no .env.
    """

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY não encontrada. "
            "Configure a chave no arquivo .env antes de usar a camada AI."
        )

    return genai.Client(api_key=api_key)


def build_interpretation_prompt(user_request):
    """
    Monta o prompt enviado ao Gemini.

    O Gemini deve apenas interpretar o pedido.
    Ele não deve calcular métricas nem decidir a variante vencedora.
    """

    return f"""
Você é uma camada de interpretação de linguagem natural para um pipeline Python
de análise de testes A/B de cashback.

Sua tarefa é converter o pedido do usuário em parâmetros estruturados.

Você NÃO deve calcular métricas.
Você NÃO deve escolher a variante vencedora.
Você NÃO deve inventar arquivos.
Você deve apenas identificar:
- qual CSV analisar;
- qual vantagem relativa mínima usar;
- se deve gerar relatório;
- se deve registrar no tracker.

{AVAILABLE_DATASETS}

Regras:
1. Se o usuário mencionar "Parceiro A", use data/raw/dataset_01_parceiroA.csv.
2. Se o usuário mencionar "Parceiro B", use data/raw/dataset_02_parceiroB.csv.
3. Se o usuário mencionar "Parceiro C", use data/raw/dataset_03_parceiroC.csv.
4. Se o usuário mencionar um caminho .csv explícito, use esse caminho.
5. Se o usuário mencionar uma porcentagem como "5%", converta para 0.05.
6. Se o usuário não mencionar vantagem mínima, use 0.02.
7. Por padrão, generate_report deve ser true.
8. Por padrão, register_tracker deve ser true.
9. Se o usuário pedir "sem relatório", generate_report deve ser false.
10. Se o usuário pedir "sem tracker", "não registre" ou "não atualizar tracker", register_tracker deve ser false.
11. Se o pedido não mencionar Parceiro A, Parceiro B, Parceiro C ou um caminho .csv explícito, marque is_valid_request como false.
12. Se is_valid_request for false, file_path deve ser null.
13. Se o pedido parecer texto aleatório, não tente adivinhar o dataset.
14. Quando is_valid_request for false, preencha clarification_message explicando que o usuário deve informar Parceiro A, Parceiro B, Parceiro C ou um caminho .csv válido.
15. Quando o pedido for válido, marque is_valid_request como true.

Pedido do usuário:
{user_request}
"""


def interpret_user_request(user_request):
    """
    Usa Gemini para transformar linguagem natural em parâmetros estruturados.
    """

    client = get_gemini_client()

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    prompt = build_interpretation_prompt(user_request)

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=InterpretedRequest,
        ),
    )

    interpreted_request = InterpretedRequest.model_validate_json(response.text)

    return interpreted_request