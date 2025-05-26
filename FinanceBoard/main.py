import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# === Auxiliares ===

def gerar_grafico(df):
    if df.empty:
        return None
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    grp = (
        df.groupby(["data", "tipo"])["valor"]
        .sum()
        .unstack(fill_value=0)
        .reset_index()
    )
    if "Receita" not in grp.columns: grp["Receita"] = 0
    if "Despesa" not in grp.columns: grp["Despesa"] = 0
    grp = grp.sort_values("data")
    fig = px.line(
        grp,
        x="data",
        y=["Receita", "Despesa"],
        markers=True,
        labels={"value": "Valor (R$)", "data": "Data", "variable": "Tipo"},
        title="Evolução de Receitas e Despesas"
    )
    fig.update_layout(legend_title_text="Tipo", margin=dict(t=50, b=20))
    return fig

def formatar_valor(v):
    s = f"R$ {v:,.2f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# === Callbacks ===

def remover(idx):
    st.session_state.dados.pop(idx)

def editar(idx):
    st.session_state.editing = idx

def salvar(idx, tipo, descricao, valor, data):
    st.session_state.dados[idx] = {
        "tipo": tipo,
        "descricao": descricao.strip(),
        "valor": valor,
        "data": data.strftime("%Y-%m-%d")
    }
    st.session_state.editing = None

def cancelar():
    st.session_state.editing = None

# === Interface ===

def mostrar_historico():
    df = pd.DataFrame(st.session_state.dados)
    if df.empty:
        st.info("Nenhuma transação registrada.")
        return

    filtro = st.text_input("🔎 Filtrar descrição:", key="filtro")
    if filtro:
        df = df[df["descricao"].str.contains(filtro, case=False, na=False)]

    for i, row in df.iterrows():
        st.markdown("---")
        c1, c2, c3, c4 = st.columns([4, 2, 0.5, 0.5])
        with c1:
            st.markdown(f"**📅 {row['data']} | {row['tipo']}**")
            st.markdown(f"🔸 {row['descricao']}")
        with c2:
            cor = "green" if row["tipo"] == "Receita" else "red"
            st.markdown(
                f"<div style='color:{cor}; font-weight:bold;'>{formatar_valor(row['valor'])}</div>",
                unsafe_allow_html=True
            )
        with c3:
            st.button("✏️", key=f"edit_{i}", help="Editar", on_click=editar, args=(i,))
        with c4:
            st.button("🗑️", key=f"del_{i}", help="Excluir", on_click=remover, args=(i,))

def main():
    st.set_page_config(layout="wide")
    st.title("💰 FinanceBoard")

    if "dados" not in st.session_state:
        st.session_state.dados = []
    if "editing" not in st.session_state:
        st.session_state.editing = None

    col1, col2 = st.columns([1, 1])

    # Coluna esquerda: adicionar + histórico
    with col1:
        st.subheader("➕ Adicionar Transação")
        with st.form("add", clear_on_submit=True):
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            desc = st.text_input("Descrição")
            val  = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
            dt   = st.date_input("Data", datetime.today())
            if st.form_submit_button("Adicionar"):
                if not desc.strip():
                    st.warning("Descrição é obrigatória.")
                else:
                    st.session_state.dados.append({
                        "tipo": tipo,
                        "descricao": desc.strip(),
                        "valor": val,
                        "data": dt.strftime("%Y-%m-%d")
                    })

        st.markdown("---")
        st.subheader("📋 Histórico de Transações")
        mostrar_historico()

    # Coluna direita: gráfico + painel de edição
    with col2:
        st.subheader("📈 Evolução de Receitas e Despesas")
        df = pd.DataFrame(st.session_state.dados)
        fig = gerar_grafico(df)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhuma transação para exibir no gráfico.")

        if st.session_state.editing is not None:
            idx = st.session_state.editing
            trans = st.session_state.dados[idx]
            st.subheader("✏️ Editar Transação")
            with st.form("edit", clear_on_submit=False):
                tipo_e = st.selectbox(
                    "Tipo", ["Receita", "Despesa"],
                    index=0 if trans["tipo"] == "Receita" else 1
                )
                desc_e = st.text_input("Descrição", value=trans["descricao"])
                val_e  = st.number_input(
                    "Valor (R$)", min_value=0.01,
                    value=trans["valor"], format="%.2f"
                )
                dt_e   = st.date_input(
                    "Data", datetime.strptime(trans["data"], "%Y-%m-%d")
                )
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.form_submit_button("💾 Salvar"):
                        salvar(idx, tipo_e, desc_e, val_e, dt_e)
                with col_b:
                    if st.form_submit_button("❌ Cancelar"):
                        cancelar()

if __name__ == "__main__":
    main()
