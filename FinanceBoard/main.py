import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import pandas as pd
from datetime import datetime
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_USERS = os.path.join(BASE_DIR, "usuarios.csv")
CSV_TRANSACOES = os.path.join(BASE_DIR, "transacoes.csv")

FONT = ("Segoe UI", 11)
FONT_BOLD = ("Segoe UI", 12, "bold")

class FinanceBoardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FinanceBoard - Controle Financeiro")
        self.root.geometry("720x450")
        self.root.resizable(False, False)

        self.usuario_logado = None
        self.categorias = ["Alimentação", "Transporte", "Saúde", "Lazer", "Salário", "Outros"]

        self.df = pd.DataFrame()
        self.frame_login = None
        self.frame_main = None
        self.frame_historico = None

        self.create_login_widgets()

    # ----------------- LOGIN E CADASTRO ----------------- #
    def create_login_widgets(self):
        if self.frame_main:
            self.frame_main.destroy()
        if self.frame_historico:
            self.frame_historico.destroy()

        self.frame_login = ttk.Frame(self.root, padding=30)
        self.frame_login.pack(expand=True)

        ttk.Label(self.frame_login, text="Usuário:", font=FONT).grid(row=0, column=0, sticky="w", pady=8, padx=5)
        self.entry_usuario = ttk.Entry(self.frame_login, width=30)
        self.entry_usuario.grid(row=0, column=1, pady=8, padx=5)

        ttk.Label(self.frame_login, text="Senha:", font=FONT).grid(row=1, column=0, sticky="w", pady=8, padx=5)
        self.entry_senha = ttk.Entry(self.frame_login, width=30, show="*")
        self.entry_senha.grid(row=1, column=1, pady=8, padx=5)

        btn_login = ttk.Button(self.frame_login, text="Entrar", command=self.login)
        btn_login.grid(row=2, column=0, columnspan=2, pady=15, sticky="ew", padx=5)

        btn_cadastrar = ttk.Button(self.frame_login, text="Cadastrar Usuário", command=self.cadastrar_usuario)
        btn_cadastrar.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5)

    def login(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        if not usuario or not senha:
            messagebox.showerror("Erro", "Informe usuário e senha.", parent=self.root)
            return

        if not os.path.exists(CSV_USERS):
            messagebox.showerror("Erro", "Nenhum usuário cadastrado.", parent=self.root)
            return

        df_users = pd.read_csv(CSV_USERS)
        df_users["usuario"] = df_users["usuario"].astype(str).str.strip()
        df_users["senha"] = df_users["senha"].astype(str).str.strip()

        user_row = df_users[(df_users["usuario"] == usuario) & (df_users["senha"] == senha)]

        if user_row.empty:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.", parent=self.root)
            return

        self.usuario_logado = usuario
        self.frame_login.destroy()
        self.load_data()
        self.create_main_widgets()

    def cadastrar_usuario(self):
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        if not usuario or not senha:
            messagebox.showerror("Erro", "Informe usuário e senha para cadastro.", parent=self.root)
            return

        if os.path.exists(CSV_USERS):
            df_users = pd.read_csv(CSV_USERS)
        else:
            df_users = pd.DataFrame(columns=["usuario", "senha"])

        df_users["usuario"] = df_users["usuario"].astype(str).str.strip()
        df_users["senha"] = df_users["senha"].astype(str).str.strip()

        if usuario in df_users["usuario"].values:
            messagebox.showerror("Erro", "Usuário já cadastrado.", parent=self.root)
            return

        novo_usuario = {"usuario": usuario, "senha": senha}
        df_users = pd.concat([df_users, pd.DataFrame([novo_usuario])], ignore_index=True)
        df_users.to_csv(CSV_USERS, index=False)

        messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!", parent=self.root)
        self.entry_usuario.delete(0, tk.END)
        self.entry_senha.delete(0, tk.END)

    # ----------------- DADOS ----------------- #
    def load_data(self):
        if os.path.exists(CSV_TRANSACOES):
            self.df = pd.read_csv(CSV_TRANSACOES)
            self.df["Data"] = pd.to_datetime(self.df["Data"], errors="coerce")
            self.df = self.df.dropna(subset=["Data"])
        else:
            self.df = pd.DataFrame(columns=["Descrição", "Valor", "Categoria", "Data", "Tipo"])

    def save_data(self):
        self.df.to_csv(CSV_TRANSACOES, index=False)

    # ----------------- TELA PRINCIPAL ----------------- #
    def create_main_widgets(self):
        self.frame_main = ttk.Frame(self.root, padding=20)
        self.frame_main.pack(expand=True, fill="both")

        # Formulário
        form_frame = ttk.LabelFrame(self.frame_main, text="Adicionar Transação", padding=15)
        form_frame.place(x=20, y=20, width=320, height=320)

        labels = ["Descrição:", "Valor (R$):", "Categoria:", "Tipo:", "Data:"]
        for i, text in enumerate(labels):
            ttk.Label(form_frame, text=text, font=FONT).grid(row=i, column=0, sticky="w", pady=8)

        self.desc_entry = ttk.Entry(form_frame, width=30)
        self.desc_entry.grid(row=0, column=1, pady=8, sticky="ew")

        self.valor_entry = ttk.Entry(form_frame, width=15)
        self.valor_entry.grid(row=1, column=1, pady=8, sticky="w")

        self.cat_combobox = ttk.Combobox(form_frame, values=self.categorias, width=28)
        self.cat_combobox.grid(row=2, column=1, pady=8, sticky="w")
        self.cat_combobox.set(self.categorias[0])
        self.cat_combobox.config(state="normal")

        self.tipo_combobox = ttk.Combobox(form_frame, values=["Despesa", "Receita"], state="readonly", width=13)
        self.tipo_combobox.grid(row=3, column=1, pady=8, sticky="w")
        self.tipo_combobox.current(0)

        self.data_entry = DateEntry(form_frame, date_pattern='yyyy-mm-dd', width=15)
        self.data_entry.grid(row=4, column=1, pady=8, sticky="w")
        self.data_entry.set_date(datetime.now())

        self.add_button = ttk.Button(form_frame, text="Adicionar Transação", command=self.adicionar_transacao)
        self.add_button.grid(row=5, column=0, columnspan=2, pady=20, sticky="ew")

        # Resumo financeiro
        resumo_frame = ttk.LabelFrame(self.frame_main, text="Resumo Financeiro", padding=15)
        resumo_frame.place(x=370, y=20, width=320, height=320)

        self.label_receitas = ttk.Label(resumo_frame, text="Receitas: R$ 0.00", font=FONT_BOLD, foreground="#2e8b57")
        self.label_receitas.pack(pady=12)

        self.label_despesas = ttk.Label(resumo_frame, text="Despesas: R$ 0.00", font=FONT_BOLD, foreground="#b22222")
        self.label_despesas.pack(pady=12)

        self.label_saldo = ttk.Label(resumo_frame, text="Saldo: R$ 0.00", font=("Segoe UI", 16, "bold"))
        self.label_saldo.pack(pady=12)

        self.btn_historico = ttk.Button(resumo_frame, text="Ver Histórico", command=self.abrir_historico)
        self.btn_historico.pack(pady=20, fill="x")

        self.update_dashboard()

    def adicionar_transacao(self):
        descricao = self.desc_entry.get().strip()
        valor_text = self.valor_entry.get().strip()
        categoria = self.cat_combobox.get().strip()
        tipo = self.tipo_combobox.get()
        data = self.data_entry.get_date()

        if not descricao:
            messagebox.showerror("Erro", "Descrição não pode ficar vazia.", parent=self.root)
            return
        try:
            valor = float(valor_text)
            if valor <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "Valor deve ser um número maior que zero.", parent=self.root)
            return
        if not categoria:
            messagebox.showerror("Erro", "Selecione uma categoria.", parent=self.root)
            return

        nova_transacao = {
            "Descrição": descricao,
            "Valor": valor,
            "Categoria": categoria,
            "Data": data.strftime("%Y-%m-%d"),
            "Tipo": tipo,
        }

        self.df = pd.concat([self.df, pd.DataFrame([nova_transacao])], ignore_index=True)
        self.save_data()

        # Limpar campos
        self.desc_entry.delete(0, tk.END)
        self.valor_entry.delete(0, tk.END)
        self.cat_combobox.set(self.categorias[0])
        self.tipo_combobox.current(0)
        self.data_entry.set_date(datetime.now())

        self.update_dashboard()
        messagebox.showinfo("Sucesso", "Transação adicionada!", parent=self.root)

    def update_dashboard(self):
        df_user = self.df.copy()

        df_user["Valor"] = pd.to_numeric(df_user["Valor"], errors='coerce').fillna(0)

        receitas = df_user[df_user["Tipo"] == "Receita"]["Valor"].sum()
        despesas = df_user[df_user["Tipo"] == "Despesa"]["Valor"].sum()
        saldo = receitas - despesas

        self.label_receitas.config(text=f"Receitas: R$ {receitas:.2f}")
        self.label_despesas.config(text=f"Despesas: R$ {despesas:.2f}")
        self.label_saldo.config(text=f"Saldo: R$ {saldo:.2f}")

    # ----------------- TELA DE HISTÓRICO ----------------- #
    def abrir_historico(self):
        self.frame_main.pack_forget()
        self.create_historico_widgets()

    def create_historico_widgets(self):
        self.frame_historico = ttk.Frame(self.root, padding=20)
        self.frame_historico.pack(expand=True, fill="both")

        ttk.Label(self.frame_historico, text="Histórico de Transações", font=("Segoe UI", 16, "bold")).pack(pady=10)

        # Treeview para mostrar transações
        columns = ("Descrição", "Valor", "Categoria", "Data", "Tipo")
        self.tree = ttk.Treeview(self.frame_historico, columns=columns, show="headings", height=12)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.pack(pady=10)

        self.carregar_transacoes_no_tree()

        # Botões Voltar e Excluir
        btn_frame = ttk.Frame(self.frame_historico)
        btn_frame.pack(pady=10)

        btn_voltar = ttk.Button(btn_frame, text="Voltar", command=self.voltar_para_main)
        btn_voltar.grid(row=0, column=0, padx=10)

        btn_excluir = ttk.Button(btn_frame, text="Excluir Selecionada", command=self.excluir_transacao)
        btn_excluir.grid(row=0, column=1, padx=10)

    def carregar_transacoes_no_tree(self):
        # Limpa itens antigos
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Ordena por data descendente
        df_sorted = self.df.sort_values(by="Data", ascending=False)

        for index, row in df_sorted.iterrows():
            valor_str = f"R$ {row['Valor']:.2f}"
            self.tree.insert("", "end", iid=index, values=(
                row["Descrição"],
                valor_str,
                row["Categoria"],
                row["Data"],
                row["Tipo"],
            ))

    def voltar_para_main(self):
        self.frame_historico.destroy()
        self.frame_main.pack(expand=True, fill="both")

    def excluir_transacao(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma transação para excluir.", parent=self.root)
            return
        confirm = messagebox.askyesno("Confirmação", "Deseja realmente excluir a transação selecionada?", parent=self.root)
        if not confirm:
            return

        for item in selected:
            idx = int(item)
            self.df = self.df.drop(idx)

        self.df.reset_index(drop=True, inplace=True)
        self.save_data()
        self.carregar_transacoes_no_tree()
        self.update_dashboard()
        messagebox.showinfo("Sucesso", "Transação excluída!", parent=self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceBoardApp(root)
    root.mainloop()
