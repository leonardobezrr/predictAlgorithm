import streamlit as st
import pandas as pd
import plotly.express as px

# Configuração da Página (Título e Layout)
st.set_page_config(page_title="Dashboard Lava-Jato", layout="wide")

# --- FUNÇÃO DE CARREGAMENTO E TRATAMENTO DE DADOS (ETL - Extrair, transformar e carregar) ---
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

if not df.empty:

    # --- BARRA LATERAL ---
    st.sidebar.header("Filtros")

    # Filtro de Data
    data_min = df['Data'].min()
    data_max = df['Data'].max()
    data_inicial = st.sidebar.date_input("Data Inicial", data_min)
    data_final = st.sidebar.date_input("Data Final", data_max)

    # Aplicando o filtro
    df_filtrado = df[(df['Data'].dt.date >= data_inicial) & (df['Data'].dt.date <= data_final)]

    # --- CABEÇALHO E KPIs (Indicadores-chave de desempenho) ---
    st.title("🚿 Dashboard Financeiro - Lava Jato")
    st.markdown("---")

    # Cálculos dos indicadores
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

    # --- ÁREA DE GRÁFICOS ---
    
    # 2 colunas para gráficos de tempo
    g_col1, g_col2 = st.columns(2)

    with g_col1:
        st.subheader("📈 Faturamento Diário")
        # Agrupando por dia
        vendas_diarias = df_filtrado.groupby('Data')['Faturamento'].sum().reset_index()
        fig_diario = px.line(vendas_diarias, x='Data', y='Faturamento', markers=True, 
                             template="plotly_white", line_shape='spline')
        st.plotly_chart(fig_diario, use_container_width=True)

    with g_col2:
        st.subheader("📅 Faturamento Semanal")
        # Agrupando por semana
        vendas_semanais = df_filtrado.set_index('Data').resample('W-MON')['Faturamento'].sum().reset_index()
        fig_semanal = px.bar(vendas_semanais, x='Data', y='Faturamento', 
                             template="plotly_white", color_discrete_sequence=['#2E86C1'])
        fig_semanal.update_xaxes(title="Semana (Início)")
        st.plotly_chart(fig_semanal, use_container_width=True)

    # --- GRÁFICO MENSAL ---
    st.markdown("---") 
    st.subheader("🗓️ Faturamento Mensal")

    # Agrupando por Mês 
    vendas_mensais = df_filtrado.set_index('Data').resample('MS')['Faturamento'].sum().reset_index()
    
    # Formatando a data para exibir apenas Mês/Ano no gráfico (ex: out/2025)
    vendas_mensais['Mes_Ano'] = vendas_mensais['Data'].dt.strftime('%b/%Y')

    fig_mensal = px.bar(vendas_mensais, x='Mes_Ano', y='Faturamento',
                        text_auto='R$ .2s', # Mostra o valor em cima da barra
                        template="plotly_white",
                        title="Evolução do Faturamento Mês a Mês")
    
    # Melhorando o visual das barras
    fig_mensal.update_traces(marker_color='#1F618D', showlegend=False)
    fig_mensal.update_layout(xaxis_title="Mês", yaxis_title="Total (R$)")
    
    st.plotly_chart(fig_mensal, use_container_width=True)

    # Gráfico de Sazonalidade (Dia da Semana)
    st.subheader("📊 Performance por Dia da Semana (Sazonalidade)")
    
    # Ordenando corretamente os dias da semana
    ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    # Média de faturamento por dia da semana
    media_dia_semana = df_filtrado.groupby('Dia_Semana_PT')['Faturamento'].mean().reindex(ordem_dias).reset_index()
    
    fig_dias = px.bar(media_dia_semana, x='Dia_Semana_PT', y='Faturamento',
                      title="Média de Faturamento Diário",
                      template="plotly_white",
                      color='Faturamento',
                      color_continuous_scale='Blues')
    
    fig_dias.update_layout(xaxis_title="Dia da Semana", yaxis_title="Média (R$)")
    st.plotly_chart(fig_dias, use_container_width=True)

    # --- TABELA DE DADOS BRUTOS ---
    with st.expander("Ver Dados Detalhados"):
        st.dataframe(df_filtrado.style.format({"Faturamento": "R$ {:.2f}"}))

else:
    st.warning("Aguardando carregamento dos dados...")