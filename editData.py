import pandas as pd
import os

# --- CONFIGURAÇÕES ---
arquivo_entrada = 'dataLavaBruto.csv'
arquivo_saida = 'dataLava.csv'

def processar_dados():
    print(f"🔄 Iniciando leitura de: {arquivo_entrada}...")
    
    # Verificando a segurança
    if not os.path.exists(arquivo_entrada):
        print(f"❌ Erro: O arquivo '{arquivo_entrada}' não foi encontrado na pasta.")
        return

    # Carregando os dados
    df = pd.read_csv(arquivo_entrada)
    linhas_iniciais = len(df)
    print(f"📊 Linhas lidas originalmente: {linhas_iniciais}")

    