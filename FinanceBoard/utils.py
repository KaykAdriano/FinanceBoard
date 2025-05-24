import pandas as pd
import os

ARQUIVO_DADOS = "dados.csv"

def carregar_dados():
    if os.path.exists(ARQUIVO_DADOS):
        return pd.read_csv(ARQUIVO_DADOS, parse_dates=["data"])
    else:
        return pd.DataFrame(columns=["data", "tipo", "valor", "descricao", "categoria"])

def salvar_dados(df):
    df.to_csv(ARQUIVO_DADOS, index=False)

def filtrar_dados(df, busca, data_ini, data_fim):
    if busca:
        df = df[df["descricao"].str.contains(busca, case=False, na=False)]
    if data_ini and data_fim:
        df = df[(df["data"] >= pd.to_datetime(data_ini)) & (df["data"] <= pd.to_datetime(data_fim))]
    return df
