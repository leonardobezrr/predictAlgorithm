import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

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
    st.title("🚿🚗 Dashboard Financeiro - Gorgônio Lava Jato")
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
    
    # --- WIDGET DE META SEMANAL (Gamificação) ---
    st.sidebar.markdown("---")
    st.sidebar.header("🎯 Meta da Semana")

    # Definindo a Meta (R$)
    META_SEMANAL = 2000.00  
    
    # Calculando o Faturamento da Semana Atual
    ultima_data_arquivo = df['Data'].max()
    
    # Encontrando o início dessa semana (Segunda-feira correspondente)
    inicio_semana = ultima_data_arquivo - pd.Timedelta(days=ultima_data_arquivo.dayofweek)
    
    # Filtrando apenas as vendas dessa semana específica
    vendas_semana_atual = df[
        (df['Data'] >= inicio_semana) & 
        (df['Data'] <= ultima_data_arquivo)
    ]
    
    faturamento_atual = vendas_semana_atual['Faturamento'].sum()
    
    # Criando o Gráfico de Velocímetro 
    fig_meta = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = faturamento_atual,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Faturamento Atual (R$)"},
        delta = {'reference': META_SEMANAL, 'relative': False, 'valueformat': '.2f'},
        gauge = {
            'axis': {'range': [None, META_SEMANAL * 1.2]}, # Eixo vai até 120% da meta
            'bar': {'color': "#27AE60"}, # Cor da barra de progresso (Verde)
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, META_SEMANAL * 0.5], 'color': "#FCBCBC"}, # Vermelho claro (Zona de Perigo)
                {'range': [META_SEMANAL * 0.5, META_SEMANAL * 0.8], 'color': "#FBEEBB"} # Amarelo (Atenção)
            ],
            'threshold': {
                'line': {'color': "green", 'width': 4},
                'thickness': 0.75,
                'value': META_SEMANAL # A linha de chegada
            }
        }
    ))

    fig_meta.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    st.sidebar.plotly_chart(fig_meta, use_container_width=True)
    
    # Mensagem motivacional simples
    falta = META_SEMANAL - faturamento_atual
    if falta > 0:
        st.sidebar.warning(f"🏃‍♂️ Só falta **R$ {falta:.2f}** para bater a meta!\n\n 🚀Simbora!!")
    else:
        st.sidebar.success("🏆 **META BATIDA! PARABÉNS!** 🎉")

    # --- GRÁFICOS DE TENDÊNCIA DIÁRIA E SEMANAL ---
    # 2 colunas para gráficos de tempo
    g_col1, g_col2 = st.columns(2)

    # Gráfico de Faturamento Diário 
    with g_col1:
        st.subheader("📈 Faturamento Diário")
        
        # Agrupando
        vendas_diarias = df_filtrado.groupby('Data')['Faturamento'].sum().reset_index()
        
        # Rótulos (Apenas Iniciais: S, T, Q...)
        mapa_letras = {0: 'S', 1: 'T', 2: 'Q', 3: 'Q', 4: 'S', 5: 'S', 6: 'D'}
        rotulos_eixo = [mapa_letras[d.dayofweek] for d in vendas_diarias['Data']]
        
        # Gráfico Base
        fig_diario = px.line(
            vendas_diarias, 
            x='Data', 
            y='Faturamento', 
            markers=True,
            template="plotly_white", 
            line_shape='spline'
        )
        
        # Configurando o Eixo X (Com a Linha Vertical Interativa)
        fig_diario.update_xaxes(
            tickmode='array',
            tickvals=vendas_diarias['Data'],
            ticktext=rotulos_eixo,
            title=None,
            showgrid=False,        # Garante que não tenha grade vertical também
            
            # Spike Line (Linha Guia Vertical)
            showspikes=True,
            spikemode='toaxis',
            spikesnap='cursor',
            spikedash='dot',
            spikecolor='#999999',
            spikethickness=1
        )
        
        # Configurando o Eixo Y 
        fig_diario.update_yaxes(title=None, showgrid=False) 

        # Interação
        fig_diario.update_layout(hovermode="x") # Linha vertical segue o mouse
        
        # Tooltip
        fig_diario.update_traces(hovertemplate='<b>%{x|%d/%m/%Y}</b><br>R$ %{y:,.2f}')
        
        st.plotly_chart(fig_diario, use_container_width=True)

    with g_col2:
        st.subheader("📅 Faturamento Semanal")
        
        # Agrupando os dados por semana 
        vendas_semanais = df_filtrado.set_index('Data').resample('W-SUN')['Faturamento'].sum().reset_index()
        
        # Gráfico Limpo
        fig_semanal = px.bar(
            vendas_semanais, 
            x='Data', 
            y='Faturamento', 
            # Sem text_auto, para não poluir
            template="plotly_white", 
            color_discrete_sequence=['#2E86C1']
        )
        
        # Configurando o Tooltip (Hover)
        fig_semanal.update_traces(
            hovertemplate='<b>Semana até %{x|%d/%m/%Y}</b><br>💰 Total: R$ %{y:,.2f}<extra></extra>'
        )
        
        # Limpando os Eixos
        fig_semanal.update_layout(xaxis_title=None, yaxis_title=None)
        
        st.plotly_chart(fig_semanal, use_container_width=True)

    # --- GRÁFICO MENSAL ---
    st.markdown("---") 
    st.subheader("🗓️ Faturamento Mensal")

    # Agregando os dados 
    vendas_mensais = df_filtrado.set_index('Data').resample('MS')['Faturamento'].agg(['sum', 'count']).reset_index()
    
    # Renomeando as colunas para facilitar (sum -> Faturamento, count -> Quantidade)
    vendas_mensais.columns = ['Data', 'Faturamento', 'Quantidade']
    
    # Criando a string de Data (Jan/2025)
    vendas_mensais['Mes_Ano'] = vendas_mensais['Data'].dt.strftime('%b/%Y')

    # Criando o gráfico
    fig_mensal = px.bar(
        vendas_mensais, 
        x='Mes_Ano', 
        y='Faturamento',
        template="plotly_white",
        title="Evolução do Faturamento e Volume de Serviços",
        hover_data=['Quantidade'] 
    )
    
    # Personalizando o tooltip (hover)
    fig_mensal.update_traces(
        marker_color='#1F618D', 
        showlegend=False,
        # HTML Básico para formatar o texto flutuante
        # %{x} = Mês | %{y} = Valor | %{customdata[0]} = Quantidade
        hovertemplate='<br><b>%{x}</b><br>💰 R$ %{y:,.2f}<br>🚗 %{customdata[0]} Lavagens<extra></extra>'
    )
    
    fig_mensal.update_layout(xaxis_title=None, yaxis_title="Total (R$)")
    
    st.plotly_chart(fig_mensal, use_container_width=True)
   
    # --- GRÁFICOS DE RAIO-X DA OPERAÇÃO ---

    st.markdown("---")
    st.subheader("📊 Médias: Dinheiro vs. Quantidade")

    col_raio_x1, col_raio_x2 = st.columns(2)
    ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']

    # Média de faturamento por dia da semana
    media_dia_semana = df_filtrado.groupby('Dia_Semana_PT')['Faturamento'].mean().reindex(ordem_dias).reset_index()
    
    # --- GRÁFICO FATURAMENTO MÉDIO ---
    with col_raio_x1:      
        fig_fat_medio = px.bar(
            media_dia_semana, 
            x='Dia_Semana_PT', 
            y='Faturamento',
            title="Média de Faturamento (R$)",
            # REMOVIDO: text_auto='.2f' (Isso limpa os números fixos)
            template="plotly_white",
            color_discrete_sequence=['#2E86C1'] # Azul
        )
        
        # Configuração do Tooltip (Mouse por cima)
        fig_fat_medio.update_traces(
            hovertemplate='<b>%{x}</b><br>💰 Média: R$ %{y:,.2f}<extra></extra>'
        )
        
        fig_fat_medio.update_layout(xaxis_title=None, yaxis_title="R$")
        st.plotly_chart(fig_fat_medio, use_container_width=True)

    # --- GRÁFICO VOLUME MÉDIO ---
    with col_raio_x2:
        # Lógica de cálculo (mantida)
        volume_diario = df_filtrado.groupby(['Data', 'Dia_Semana_PT']).size().reset_index(name='Qtd_Servicos')
        media_volume_semana = volume_diario.groupby('Dia_Semana_PT')['Qtd_Servicos'].mean().reindex(ordem_dias).reset_index()
        
        fig_vol = px.bar(
            media_volume_semana, 
            x='Dia_Semana_PT', 
            y='Qtd_Servicos',
            title="Média de Veículos Atendidos (Qtd)",
            # REMOVIDO: text_auto='.2f'
            template="plotly_white",
            color_discrete_sequence=['#E67E22'] # Laranja
        )
        
        # Configuração do Tooltip (Mouse por cima)
        # %{y:.1f} mostra com 1 casa decimal (ex: 8.5 carros)
        fig_vol.update_traces(
            hovertemplate='<b>%{x}</b><br>🚗 Média: %{y:.1f} Veículos<extra></extra>'
        )
        
        fig_vol.update_layout(xaxis_title=None, yaxis_title="Veículos")
        st.plotly_chart(fig_vol, use_container_width=True)

    # --- TABELA DE DADOS BRUTOS ---
    with st.expander("Ver Dados Detalhados"):
        st.dataframe(df_filtrado.style.format({"Faturamento": "R$ {:.2f}"}))

    # --- SEÇÃO DE PREVISÃO DE DEMANDA ---

    # Criando abas para separar o "Passado" do "Futuro"
    tab_historico, tab_previsao = st.tabs(["📊 Visão Histórica", "🔮 Previsão de Metas (IA)"])

    with tab_historico:
        with g_col1:
            
            # Agrupando
            vendas_diarias = df_filtrado.groupby('Data')['Faturamento'].sum().reset_index()
            
            # Rótulos (Apenas Iniciais: S, T, Q...)
            mapa_letras = {0: 'S', 1: 'T', 2: 'Q', 3: 'Q', 4: 'S', 5: 'S', 6: 'D'}
            rotulos_eixo = [mapa_letras[d.dayofweek] for d in vendas_diarias['Data']]
            
            # Gráfico Base
            fig_diario = px.line(
                vendas_diarias, 
                x='Data', 
                y='Faturamento', 
                markers=True,
                template="plotly_white", 
                line_shape='spline'
            )
            
            # Configurando o Eixo X (Com a Linha Vertical Interativa)
            fig_diario.update_xaxes(
                tickmode='array',
                tickvals=vendas_diarias['Data'],
                ticktext=rotulos_eixo,
                title=None,
                showgrid=False,        # Garante que não tenha grade vertical também
                
                # Spike Line (Linha Guia Vertical)
                showspikes=True,
                spikemode='toaxis',
                spikesnap='cursor',
                spikedash='dot',
                spikecolor='#999999',
                spikethickness=1
            )
            
            # Configurando o Eixo Y 
            fig_diario.update_yaxes(title=None, showgrid=False) 

            # Interação
            fig_diario.update_layout(hovermode="x") # Linha vertical segue o mouse
            
            # Tooltip
            fig_diario.update_traces(hovertemplate='<b>%{x|%d/%m/%Y}</b><br>R$ %{y:,.2f}')
            
        st.info("👆 Aqui estão os dados que analisamos anteriormente.")

    with tab_previsao:
        st.header("🤖 Inteligência Artificial: Previsão para Próxima Semana")
        
        # Executar a previsão apenas se houver dados suficientes
        if len(df) > 14: # Precisa de pelo menos 2 semanas pra brincar
            
            # 1. Preparar dados para o Modelo (Regressão - O mais robusto para produção)
            # Vamos usar a Regressão Linear pois ela é mais rápida e estável para o App
            from sklearn.linear_model import LinearRegression
            
            # Agrupamento diário
            df_prev = df.groupby('Data')['Faturamento'].sum().asfreq('D').fillna(0).reset_index()
            df_prev['Dia_Semana'] = df_prev['Data'].dt.dayofweek
            df_prev['Tempo'] = np.arange(len(df_prev))
            
            # Treino (Usa tudo até hoje)
            X = pd.get_dummies(df_prev['Dia_Semana'], prefix='D', drop_first=True)
            X['Tempo'] = df_prev['Tempo']
            y = df_prev['Faturamento']
            
            modelo = LinearRegression()
            modelo.fit(X, y)
            
            # 2. Criar Datas Futuras (Próximos 7 dias)
            ultima_data = df_prev['Data'].max()
            datas_futuras = pd.date_range(start=ultima_data + pd.Timedelta(days=1), periods=7)
            
            df_futuro = pd.DataFrame({'Data': datas_futuras})
            df_futuro['Dia_Semana'] = df_futuro['Data'].dt.dayofweek
            df_futuro['Tempo'] = np.arange(len(df_prev), len(df_prev) + 7)
            
            # Preparar X do futuro (garantindo as mesmas colunas)
            X_futuro = pd.get_dummies(df_futuro['Dia_Semana'], prefix='D', drop_first=True)
            X_futuro['Tempo'] = df_futuro['Tempo']
            # Alinha as colunas (se faltar alguma dummy no futuro, preenche com 0)
            X_futuro = X_futuro.reindex(columns=X.columns, fill_value=0)
            
            # Prevendo o Futuro
            y_pred = modelo.predict(X_futuro)
            df_futuro['Previsao'] = np.maximum(y_pred, 0) # Garante que não seja negativo
            
            # Exibindo Métricas e Gráfico
            total_previsto = df_futuro['Previsao'].sum()
            col_meta, col_sabado = st.columns(2)
            
            col_meta.metric(
                "💰 Meta de Faturamento (Próx. 7 Dias)", 
                f"R$ {total_previsto:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            )
            
            # Pega a previsão do próximo Sábado (Dia 5 da semana)
            prev_sabado = df_futuro[df_futuro['Dia_Semana'] == 5]['Previsao']
            valor_sabado = prev_sabado.values[0] if not prev_sabado.empty else 0
            
            col_sabado.metric(
                "🚗 Previsão para o Próximo Sábado", 
                f"R$ {valor_sabado:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            )
            
            # Gráfico de Linha (Conectando Passado e Futuro)
            # Pegamos os últimos 14 dias reais + 7 dias futuros
            df_historico_recente = df_prev.tail(14).copy()
            df_historico_recente['Tipo'] = 'Realizado'
            df_historico_recente.rename(columns={'Faturamento': 'Valor'}, inplace=True)
            
            df_futuro_plot = df_futuro[['Data', 'Previsao']].copy()
            df_futuro_plot['Tipo'] = 'Previsão IA'
            df_futuro_plot.rename(columns={'Previsao': 'Valor'}, inplace=True)
            
            df_final_plot = pd.concat([df_historico_recente[['Data', 'Valor', 'Tipo']], df_futuro_plot])
            
            # Gráfico de Linha (Conectando Passado e Futuro)            
            fig_prev = px.line(
                df_final_plot, 
                x='Data', 
                y='Valor', 
                color='Tipo',
                markers=True,
                title="Tendência Recente vs. Previsão",
                color_discrete_map={
                    'Realizado': '#FFFFFF',  # Branco Puro (para destacar no fundo escuro)
                    'Previsão IA': '#00BFFF' # Azul Cyan Neon (para destacar a previsão)
                }
            )
            
            # Estilo tracejado para o futuro
            fig_prev.update_traces(patch={"line": {"dash": "dot"}}, selector={"legendgroup": "Previsão IA"})
            
            # Isso garante que ele respeite o modo escuro do Streamlit
            fig_prev.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white") # Garante que os textos dos eixos fiquem brancos também
            )
            
            st.plotly_chart(fig_prev, use_container_width=True)
            
            # Estilo tracejado para o futuro
            fig_prev.update_traces(patch={"line": {"dash": "dot"}}, selector={"legendgroup": "Previsão IA"})
                        
            with st.expander("Ver Tabela de Metas Diárias"):
                tabela_show = df_futuro[['Data', 'Previsao']].copy()
                tabela_show['Dia'] = tabela_show['Data'].dt.day_name()
                tabela_show['Previsao'] = tabela_show['Previsao'].apply(lambda x: f"R$ {x:,.2f}")
                st.dataframe(tabela_show)

        else:
            st.warning("⚠️ Precisamos de mais dados! Continue cadastrando o faturamento diário para liberar a IA.")

else:
    st.warning("Aguardando carregamento dos dados...")