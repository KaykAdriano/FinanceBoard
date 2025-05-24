import pandas as pd
import os

def carregar_dados(caminho_arquivo):
    if os.path.exists(caminho_arquivo):
        df = pd.read_excel(caminho_arquivo)
    else:
        df = pd.DataFrame(columns=["data", "tipo", "valor", "descricao"])
        df.to_excel(caminho_arquivo, index=False)
    return df

def salvar_dados(df, caminho_arquivo):
    df.to_excel(caminho_arquivo, index=False)

def adicionar_entrada(df, data, tipo, valor, descricao):
    nova_entrada = pd.DataFrame([{
        "data": data,
        "tipo": tipo,
        "valor": valor,
        "descricao": descricao
    }])
    df = pd.concat([df, nova_entrada], ignore_index=True)
    return df
