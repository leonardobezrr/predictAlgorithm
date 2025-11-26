import pandas as pd

# 1. Carrega o seu arquivo
df = pd.read_csv('dataLavaBruto.csv') # Ou o nome do seu arquivo atual

# --- O ALGORITMO (A Lógica) ---
def completar_ano(valor):
    # Converte para texto e remove espaços vazios
    if pd.isna(valor) or str(valor).strip() == "":
        return None  # Devolvemos Nulo para o Pandas saber que ali não tem nada
    
    data_str = str(valor).strip()
    
    # REGRA: Se o texto for curto (ex: "08/11" tem 5 letras), adiciona o ano
    # Se for "08/11", o tamanho é 5. Se for "08/11/2025", o tamanho é 10.
    if len(data_str) <= 5:
        return data_str + "/2025"
    
    # Se já for grande, devolve como está
    return data_str

# 2. Aplica a lógica na coluna inteira
df['Data'] = df['Data'].apply(completar_ano)

# 3. Visualiza o resultado para conferir
print(df['Data'].head(10)) # Mostra as 10 primeiras linhas
print(df['Data'].tail(10)) # Mostra as 10 últimas (onde estava o erro)

# 4. Salva o arquivo corrigido
df.to_csv('dataLava.csv', index=False)