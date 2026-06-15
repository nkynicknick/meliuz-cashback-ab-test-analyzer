from src.cleaning import load_and_clean_csv


df = load_and_clean_csv("data/raw/dataset_01_parceiroA.csv")

print("Arquivo lido e limpo com sucesso!")
print()
print("Primeiras linhas:")
print(df.head())
print()
print("Tipos das colunas:")
print(df.dtypes)
print()
print("Número de linhas:", len(df))
print("Grupos:", df["Grupos de usuários"].unique())
print("Parceiro:", df["Parceiro"].unique())