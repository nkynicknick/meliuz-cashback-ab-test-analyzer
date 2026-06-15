from src.ai_interpreter import interpret_user_request


requests = [
    "Analise o teste do Parceiro A, gere relatório e registre no tracker.",
    "Analise o Parceiro B usando 5% como vantagem mínima.",
    "Analise o teste do Parceiro C sem relatório.",
]


for request_text in requests:
    print("=" * 80)
    print("Pedido:")
    print(request_text)
    print()

    interpreted = interpret_user_request(request_text)

    print("Interpretação:")
    print(interpreted.model_dump())
    print()