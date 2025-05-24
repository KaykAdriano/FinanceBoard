import pandas as pd
from datetime import datetime

def calcular_totais(df):
    hoje = datetime.now().date()
    df['data'] = pd.to_datetime(df['data']).dt.date

    receitas = df[df['tipo'] == 'Receita']
    total_dia = receitas[receitas['data'] == hoje]['valor'].sum()
    total_mes = receitas[
        (pd.to_datetime(receitas['data']).dt.month == hoje.month) &
        (pd.to_datetime(receitas['data']).dt.year == hoje.year)
    ]['valor'].sum()
    return total_dia, total_mes
