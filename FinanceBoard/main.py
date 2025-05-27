import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def load_data():
    try:
        df = pd.read_csv("transacoes.csv")
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=["Descrição", "Valor", "Categoria", "Data", "Tipo"])

def save_data(df):
    df.to_csv("transacoes.csv", index=False)

def format_data(df):
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df.dropna(subset=["Data"], inplace=True)
    return df

def grafico_semanal(df):
    hoje = datetime.now().date()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    dias_semana = [inicio_semana + timedelta(days=i) for i in range(7)]
    df_base = pd.DataFrame({"Data": pd.to_datetime(dias_semana)})

    df_semana = df[(df["Data"].dt.date >= inicio_semana) & (df["Data"].dt.date <= inicio_semana + timedelta(days=6))]
    df_agrupado = df_semana.groupby(["Data", "Tipo"])["Valor"].sum().unstack(fill_value=0).reset_index()

    df_final = pd.merge(df_base, df_agrupado, on="Data", how="left").fillna(0)

    if "Receita" not in df_final.columns:
        df_final["Receita"] = 0
    if "Despesa" not in df_final.columns:
        df_final["Despesa"] = 0

    dias_abrev = {
        "Monday": "Seg", "Tuesday": "Ter", "Wednesday": "Qua",
        "Thursday": "Qui", "Friday": "Sex", "Saturday": "Sáb", "Sunday": "Dom"
    }
    df_final["DiaSemana"] = df_final["Data"].dt.day_name().map(dias_abrev)

    fig = px.bar(
        df_final,
        x="DiaSemana",
        y=["Despesa", "Receita"],
        barmode="group",
        title="Resumo Semanal (Segunda a Domingo)",
        labels={"value": "Valor (R$)", "DiaSemana": "Dia da Semana"},
        text_auto='.2s'
    )
    fig.update_layout(yaxis_title="Valor em R$", xaxis_title="Dia da Semana")
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def grafico_mensal(df):
    if df.empty:
        st.warning("Sem dados para o gráfico mensal.")
        return

    df["AnoMes"] = df["Data"].dt.to_period("M").astype(str)
    df_agrupado = df.groupby(["AnoMes", "Tipo"])["Valor"].sum().unstack(fill_value=0)

    if "Receita" not in df_agrupado.columns:
        df_agrupado["Receita"] = 0
    if "Despesa" not in df_agrupado.columns:
        df_agrupado["Despesa"] = 0

    df_agrupado = df_agrupado.reset_index()

    fig = px.bar(
        df_agrupado,
        x="AnoMes",
        y=["Despesa", "Receita"],
        barmode="group",
        title="Resumo Mensal",
        labels={"AnoMes": "Mês", "value": "Valor (R$)"},
        text_auto='.2s'
    )
    fig.update_layout(yaxis_title="Valor em R$", xaxis_title="Mês")
    fig.update_traces(textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

def formulario_adicionar(df):
    st.subheader("Adicionar Nova Transação")
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
    categoria = st.text_input("Categoria")
    tipo = st.selectbox("Tipo", ["Despesa", "Receita"])
    data = st.date_input("Data", datetime.now())

    if st.button("Adicionar"):
        if descricao and valor > 0 and categoria:
            nova_transacao = {
                "Descrição": descricao,
                "Valor": valor,
                "Categoria": categoria,
                "Data": pd.to_datetime(data),
                "Tipo": tipo
            }
            df = pd.concat([df, pd.DataFrame([nova_transacao])], ignore_index=True)
            save_data(df)
            st.success("Transação adicionada!")
            st.experimental_rerun()  # <== Aqui força o reload da página
        else:
            st.error("Preencha todos os campos corretamente.")
    return df

def dashboard(df):
    st.title("FinanceBoard - Dashboard")

    total_receitas = df.loc[df["Tipo"] == "Receita", "Valor"].sum()
    total_despesas = df.loc[df["Tipo"] == "Despesa", "Valor"].sum()
    saldo = total_receitas - total_despesas

    st.markdown(
        f"""
        <div style='display: flex; justify-content: space-around; padding: 10px 0;'>
            <div style='text-align: center;'>
                <h3 style='color: green;'>Receitas</h3>
                <p style='font-size: 24px;'>R$ {total_receitas:,.2f}</p>
            </div>
            <div style='text-align: center;'>
                <h3 style='color: red;'>Despesas</h3>
                <p style='font-size: 24px;'>R$ {total_despesas:,.2f}</p>
            </div>
            <div style='text-align: center;'>
                <h3>Saldo</h3>
                <p style='font-size: 28px; font-weight: bold;'>{saldo:,.2f}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 1])

    with col1:
        df = formulario_adicionar(df)

    with col2:
        grafico_semanal(df)

    st.markdown("---")
    grafico_mensal(df)

    return df

def historico(df):
    st.title("Histórico de Transações")
    st.write("Aqui você pode editar e excluir as transações.")
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if not edited_df.equals(df):
        save_data(edited_df)
        st.success("Dados atualizados! Recarregue a página para refletir as mudanças.")

def main():
    st.set_page_config(page_title="FinanceBoard", layout="wide")
    df = load_data()
    df = format_data(df)

    menu = st.sidebar.radio("Navegação", ["Dashboard", "Histórico"])

    if menu == "Dashboard":
        df = dashboard(df)
    else:
        historico(df)

if __name__ == "__main__":
    main()
