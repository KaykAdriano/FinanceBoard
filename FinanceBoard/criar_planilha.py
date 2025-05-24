import pandas as pd
import os

# Dados de exemplo
data = {
    "Data": [
        "2025-05-01",
        "2025-05-02",
        "2025-05-03",
        "2025-05-04",
        "2025-05-05",
        "2025-05-06",
    ],
    "Tipo": [
        "Receita",
        "Despesa",
        "Receita",
        "Despesa",
        "Receita",
        "Despesa",
    ],
    "Valor": [
        1500.00,
        200.00,
        250.00,
        100.00,
        300.00,
        50.00,
    ],
    "Descrição": [
        "Salário",
        "Supermercado",
        "Freelance",
        "Conta de luz",
        "Venda de produto",
        "Transporte",
    ],
}

# Cria o DataFrame e salva na pasta data/
df = pd.DataFrame(data)
os.makedirs("data", exist_ok=True)
df.to_excel("data/receitas_despesas.xlsx", index=False)
print("✅ Arquivo criado: data/receitas_despesas.xlsx")
