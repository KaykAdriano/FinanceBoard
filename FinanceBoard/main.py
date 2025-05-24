import streamlit as st
from modules.excel_handler import carregar_dados, salvar_dados, adicionar_entrada
from modules.calculos import calcular_totais
from modules.graficos import mostrar_graficos

CAMINHO_ARQUIVO = "data/receitas_despesas.xlsx"

st.set_page_config(page_title="FinanceBoard", layout="centered")
st.title("📊 FinanceBoard")

df = carregar_dados(CAMINHO_ARQUIVO)

with st.form("form_lancamento"):
    st.subheader("Adicionar Receita ou Despesa")
    data = st.date_input("Data")
    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
    valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")
    descricao = st.text_input("Descrição")
    enviar = st.form_submit_button("Adicionar")

    if enviar and valor > 0:
        df = adicionar_entrada(df, data, tipo, valor, descricao)
        salvar_dados(df, CAMINHO_ARQUIVO)
        st.success("Lançamento adicionado com sucesso!")

total_dia, total_mes = calcular_totais(df)
st.metric("Receita do Dia", f"R$ {total_dia:.2f}")
st.metric("Receita do Mês", f"R$ {total_mes:.2f}")

st.subheader("Gráfico de Fluxo Financeiro")
mostrar_graficos(df)
