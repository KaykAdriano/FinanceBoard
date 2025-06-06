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
    df = df.dropna(subset=["Data"])
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

def reload_page():
    st.markdown(
        """
        <script>
        window.location.reload();
        </script>
        """,
        unsafe_allow_html=True
    )

def formulario_adicionar(df):
    st.subheader("Adicionar Nova Transação")

    if "desc" not in st.session_state:
        st.session_state.desc = ""
    if "valor" not in st.session_state:
        st.session_state.valor = 0.01
    if "cat" not in st.session_state:
        st.session_state.cat = ""
    if "tipo" not in st.session_state:
        st.session_state.tipo = "Despesa"
    if "data" not in st.session_state:
        st.session_state.data = datetime.now()
    if "reset_flag" not in st.session_state:
        st.session_state.reset_flag = False

    if st.session_state.reset_flag:
        st.session_state.desc = ""
        st.session_state.valor = 0.01
        st.session_state.cat = ""
        st.session_state.tipo = "Despesa"
        st.session_state.data = datetime.now()
        st.session_state.reset_flag = False

    with st.container():
        col1, col2 = st.columns([2, 1])
        with col1:
            descricao = st.text_input("Descrição", key="desc")
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.01, format="%.2f", key="valor")

        col3, col4 = st.columns([2, 1])
        with col3:
            categoria = st.text_input("Categoria", key="cat")
        with col4:
            tipo = st.selectbox("Tipo", ["Despesa", "Receita"], key="tipo")

        data = st.date_input("Data", st.session_state.data, key="data")

        st.markdown("<br>", unsafe_allow_html=True)

        # Estilo CSS para os botões
        botao_css = """
            <style>
                .botao-estilizado {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 22px;
                    text-align: center;
                    font-size: 16px;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                    width: 100%;
                }
                .botao-estilizado:hover {
                    background-color: #0056b3;
                }
                .botao-secundario {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 10px 22px;
                    text-align: center;
                    font-size: 16px;
                    border-radius: 8px;
                    cursor: pointer;
                    transition: background-color 0.3s ease;
                    width: 100%;
                }
                .botao-secundario:hover {
                    background-color: #565e64;
                }
            </style>
        """
        st.markdown(botao_css, unsafe_allow_html=True)

        btn_col1, btn_col2, _ = st.columns([1,1,2])
        with btn_col1:
            if st.button("Adicionar"):
                if descricao.strip() == "":
                    st.error("Descrição não pode ficar vazia.")
                elif valor <= 0:
                    st.error("Valor deve ser maior que zero.")
                elif categoria.strip() == "":
                    st.error("Categoria não pode ficar vazia.")
                else:
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
                    st.session_state.reset_flag = True
                    st.info("Por favor, recarregue a página para limpar o formulário.")
                    
                    # Forçar atualização com script para limpar após adicionar (se quiser descomente)
                    # st.experimental_rerun()

        with btn_col2:
            if st.button("Atualizar"):
                reload_page()

    return df

def dashboard(df):
    st.markdown("<h1 style='text-align: center; font-size: 2.5rem;'>FinanceBoard - Dashboard</h1>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        df = formulario_adicionar(df)

    with col2:
        grafico_semanal(df)

    st.markdown("---")

    total_receitas = df.loc[df["Tipo"] == "Receita", "Valor"].sum()
    total_despesas = df.loc[df["Tipo"] == "Despesa", "Valor"].sum()
    saldo = total_receitas - total_despesas

    st.markdown(
        f"""
        <div style='display: flex; justify-content: center; gap: 60px; padding: 10px 0;'>
            <div style='text-align: center;'>
                <h3 style='color: green; margin-bottom: 0;'>Receitas</h3>
                <p style='font-size: 24px; margin-top: 0;'>R$ {total_receitas:,.2f}</p>
            </div>
            <div style='text-align: center;'>
                <h3 style='color: red; margin-bottom: 0;'>Despesas</h3>
                <p style='font-size: 24px; margin-top: 0;'>R$ {total_despesas:,.2f}</p>
            </div>
            <div style='text-align: center;'>
                <h3 style='margin-bottom: 0;'>Saldo</h3>
                <p style='font-size: 28px; font-weight: bold; margin-top: 0;'>{saldo:,.2f}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    grafico_mensal(df)

    return df

def historico(df):
    st.title("Histórico de Transações")
    st.write("Aqui você pode editar e excluir as transações.")

    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    if not edited_df.equals(df):
        save_data(edited_df)
        st.success("Dados atualizados! Por favor, recarregue a página para refletir as mudanças.")

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
