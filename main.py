import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página (Título e Layout)
st.set_page_config(page_title="Dashboard Lava-Jato", layout="wide")

# --- FUNÇÃO DE CARREGAMENTO E TRATAMENTO DE DADOS (ETL) ---
@st.cache_data
def load_data():
    file = "dataLava.csv"
    try:
        # Carregando os dados 
        df = pd.read_csv(file)

        # Limpando os dados
        df = df.dropna(subset=['Data', 'Valor (R$)']) # Remove linhas vazias

        # Convertendo a coluna 'Data' para o formato datetime
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', dayfirst=True, errors='coerce')
        df = df.dropna(subset=['Data']) # Remove datas inválidas

        # Renomeando colunas para facilitar o uso
        df.rename(columns={'Valor (R$)': 'Faturamento', 'Descrição Original': 'Servico'}, inplace=True)

        # Extraindo novas colunas de data para auxiliar nas análises
        df['Dia_Semana'] = df['Data'].dt.day_name()
        df['Mes'] = df['Data'].dt.strftime('%Y-%m')
        df['Semana_Ano'] = df['Data'].dt.isocalendar().week


        # Traduzindo os dias para o gráfico ficar bonito em PT-BR
        mapa_dias = {
            'Monday': 'Segunda', 'Tuesday': 'Terça', 'Wednesday': 'Quarta',
            'Thursday': 'Quinta', 'Friday': 'Sexta', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
        }
        df['Dia_Semana_PT'] = df['Dia_Semana'].map(mapa_dias)   

        # Ordenando por data
        df = df.sort_values('Data')

        return df
    
    except FileNotFoundError:
        st.error(f"Erro ao carregar os dados: {file}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro
    
