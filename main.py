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
    
df = load_data()

# Se o DataFrame não estiver vazio, monta o dashboard
if not df.empty:

    # --- BARRA LATERAL (FILTROS) ---
    st.sidebar.header("Filtros")

    # Filtro de Data
    data_min = df['Data'].min()
    data_max = df['Data'].max()
    data_inicial = st.sidebar.date_input("Data Inicial", data_min)
    data_final = st.sidebar.date_input("Data Final", data_max)

    # Aplicando o filtro
    df_filtrado = df[(df['Data'].dt.date >= data_inicial) & (df['Data'].dt.date <= data_final)]

    # --- CABEÇALHO E KPIs (INDICADORES) ---
    st.title("🚿 Dashboard Financeiro - Lava Jato")
    st.markdown("---")

    # Cálculos dos KPIs
    faturamento_total = df_filtrado['Faturamento'].sum()
    qtd_servicos = len(df_filtrado)
    ticket_medio = faturamento_total / qtd_servicos if qtd_servicos > 0 else 0
    
    # Identificando o melhor dia da semana
    faturamento_por_dia = df_filtrado.groupby('Dia_Semana_PT')['Faturamento'].sum()
    melhor_dia = faturamento_por_dia.idxmax() if not faturamento_por_dia.empty else "N/A"

    # Exibindo KPIs em colunas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Faturamento Total", f"R$ {faturamento_total:,.2f}")
    col2.metric("Serviços Realizados", qtd_servicos)
    col3.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
    col4.metric("Melhor Dia da Semana", melhor_dia)

    st.markdown("---")

    