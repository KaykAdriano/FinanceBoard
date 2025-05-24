import matplotlib.pyplot as plt
import streamlit as st
import pandas as pd

def mostrar_graficos(df):
    if df.empty:
        st.info("Nenhum dado disponível para exibir gráficos.")
        return

    df['data'] = pd.to_datetime(df['data'])
    receitas = df[df['tipo'] == 'Receita']
    despesas = df[df['tipo'] == 'Despesa']

    receitas_dia = receitas.groupby(df['data'].dt.date)['valor'].sum()
    despesas_dia = despesas.groupby(df['data'].dt.date)['valor'].sum()

    fig, ax = plt.subplots()
    receitas_dia.plot(ax=ax, label="Receitas", marker='o')
    despesas_dia.plot(ax=ax, label="Despesas", marker='o')
    ax.set_title("Fluxo Diário de Receitas e Despesas")
    ax.set_ylabel("Valor (R$)")
    ax.legend()
    st.pyplot(fig)
