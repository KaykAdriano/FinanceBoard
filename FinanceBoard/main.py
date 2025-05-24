import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="FinanceBoard", layout="wide")

# Função para colorir linhas baseado no tipo
def cor_linha(row):
    if row["tipo"] == "Receita":
        return ['background-color: #28a745; color: white; font-weight: bold;'] * len(row)  # verde forte
    elif row["tipo"] == "Despesa":
        return ['background-color: #dc3545; color: white; font-weight: bold;'] * len(row)  # vermelho forte
    else:
        return [''] * len(row)

def carregar_dados():
    if "df" not in st.session_state:
        df = pd.DataFrame(columns=["data", "tipo", "valor", "descricao"])
        df["data"] = pd.to_datetime(df["data"], errors='coerce')
        st.session_state.df = df
    return st.session_state.df

def salvar_dados(df):
    st.session_state.df = df

def main():
    st.title("💰 FinanceBoard - Controle Financeiro")

    df = carregar_dados()

    with st.form("form_add"):
        col1, col2, col3, col4, col5 = st.columns([2,2,2,4,1])
        with col1:
            data = st.date_input("📅 Data")
        with col2:
            tipo = st.selectbox("🔖 Tipo", ["Receita", "Despesa"])
        with col3:
            valor = st.number_input("💵 Valor (R$)", min_value=0.0, format="%.2f")
        with col4:
            descricao = st.text_input("📝 Descrição")
        with col5:
            add = st.form_submit_button("➕ Adicionar")

    if add:
        nova_linha = {"data": pd.to_datetime(data), "tipo": tipo, "valor": valor, "descricao": descricao}
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        salvar_dados(df)
        st.success("✅ Entrada adicionada!")

    st.markdown("---")
    st.subheader("📋 Registros")

    if not df.empty:
        for i, row in df.iterrows():
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                st.markdown(f"**{row['data'].date()}** - **{row['tipo']}** - R$ **{row['valor']:.2f}** - *{row['descricao']}*")
            with col2:
                if st.button("🗑️", key=f"del_{i}", help="Excluir essa linha"):
                    df = df.drop(i).reset_index(drop=True)
                    salvar_dados(df)
                    st.success("🗑️ Linha deletada!")
                    st.experimental_rerun()

        st.dataframe(df.style.apply(cor_linha, axis=1), height=300)

        resumo = df.groupby(["data", "tipo"])["valor"].sum().unstack(fill_value=0).sort_index()

        plt.figure(figsize=(12, 5))
        if "Receita" in resumo.columns:
            plt.plot(resumo.index, resumo["Receita"], label="Receita", marker='o', color="#28a745", linewidth=2)
        if "Despesa" in resumo.columns:
            plt.plot(resumo.index, resumo["Despesa"], label="Despesa", marker='o', color="#dc3545", linewidth=2)

        plt.xlabel("Data", fontsize=12)
        plt.ylabel("Valor (R$)", fontsize=12)
        plt.title("Receita e Despesa por Dia", fontsize=16, fontweight='bold')
        plt.legend(fontsize=12)
        plt.grid(alpha=0.3)
        plt.tight_layout()

        st.pyplot(plt)

        total_dia = df[df["data"] == pd.to_datetime(pd.Timestamp.now().date())]["valor"].sum()
        total_mes = df[df["data"].dt.month == pd.Timestamp.now().month]["valor"].sum()

        st.markdown("---")
        st.markdown(
            f"<h3 style='color:#28a745'>Total do dia: R$ {total_dia:.2f}</h3>", unsafe_allow_html=True)
        st.markdown(
            f"<h3 style='color:#dc3545'>Total do mês: R$ {total_mes:.2f}</h3>", unsafe_allow_html=True)

    else:
        st.info("Nenhum registro para exibir.")

if __name__ == "__main__":
    main()
