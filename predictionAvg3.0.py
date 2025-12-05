import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings("ignore") 

# --- CARREGAMENTO (ETL) ---
def carregar_dados():
    try:
        df = pd.read_csv('dataLava.csv')
        def corrigir(x):
            s = str(x).strip()
            return s + "/2025" if len(s) <= 5 else s
        df['Data'] = df['Data'].apply(corrigir)
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', dayfirst=True, errors='coerce')
        # Verifica se coluna de valor existe, senão tenta 'Faturamento'
        col_valor = 'Valor (R$)' if 'Valor (R$)' in df.columns else 'Faturamento'
        return df.groupby('Data')[col_valor].sum().asfreq('D').fillna(0)
    except Exception as e:
        print(f"Erro ao carregar: {e}")
        return pd.Series()

y = carregar_dados()

if len(y) > 0:
    dias_teste = 7
    y_treino = y.iloc[:-dias_teste]
    y_teste = y.iloc[-dias_teste:]

    previsoes = pd.DataFrame(index=y_teste.index)
    previsoes['Real'] = y_teste

    # --- OS MODELOS ANTERIORES ---

    # Regressão Sazonal (Campeão Atual)
    df_reg = y.reset_index()
    df_reg['Dia'] = df_reg['Data'].dt.dayofweek
    X = pd.get_dummies(df_reg['Dia'], prefix='D', drop_first=True)
    X['Tempo'] = np.arange(len(df_reg))
    
    # Ajuste de índices para treino/teste
    X_treino = X.iloc[:-dias_teste]
    X_teste = X.iloc[-dias_teste:]
    
    reg = LinearRegression().fit(X_treino, y_treino)
    previsoes['Regressao'] = reg.predict(X_teste)

    # Holt-Winters Multiplicativo (Vice)
    try:
        hw = ExponentialSmoothing(y_treino, seasonal_periods=7, trend='add', seasonal='add').fit()
        previsoes['HoltWinters'] = hw.forecast(dias_teste)
    except:
        previsoes['HoltWinters'] = 0 # Fallback

    # --- OS NOVOS ALGORITMOS ---

    # SARIMA
    print("⏳ Treinando SARIMA (pode demorar um pouco)...")
    try:
        modelo_sarima = SARIMAX(y_treino, 
                                order=(1, 0, 1), 
                                seasonal_order=(1, 1, 1, 7),
                                enforce_stationarity=False,
                                enforce_invertibility=False)
        resultado_sarima = modelo_sarima.fit(disp=False)
        previsoes['SARIMA'] = resultado_sarima.get_forecast(steps=dias_teste).predicted_mean
    except Exception as e:
        print(f"Erro no SARIMA: {e}")
        previsoes['SARIMA'] = 0

    # ENSEMBLE (O Modelo "Média dos Campeões")
    previsoes['Ensemble'] = (previsoes['Regressao'] + previsoes['HoltWinters']) / 2

    # --- PLACAR FINAL (Com MAE, MAPE e RMSE) ---
    placar = []
    for col in previsoes.columns:
        if col == 'Real': continue
        
        # Tratando erros e negativos
        serie_p = previsoes[col].fillna(0)
        serie_p = serie_p.apply(lambda x: max(x, 0)) # Não existe faturamento negativo
        
        # 1. MAE (Erro Absoluto Médio)
        mae = mean_absolute_error(y_teste, serie_p)
        
        # 2. RMSE (Raiz do Erro Quadrático Médio)
        # Calcula o erro ao quadrado e tira a raiz
        mse = mean_squared_error(y_teste, serie_p)
        rmse = np.sqrt(mse)
        
        # 3. MAPE (Erro Percentual) - COM PROTEÇÃO CONTRA ZERO
        # Filtramos onde o Real > 0 para evitar divisão por zero (Domingos)
        mask = y_teste > 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_teste[mask] - serie_p[mask]) / y_teste[mask])) * 100
        else:
            mape = 0.0

        placar.append({
            'Modelo': col, 
            'MAE (R$)': round(mae, 2),
            'MAPE (%)': round(mape, 2),
            'RMSE': round(rmse, 2)
        })

    df_placar = pd.DataFrame(placar).sort_values('MAE (R$)')

    print("\n🏆 RANKING DEFINITIVO DE PRECISÃO:")
    print(df_placar.to_string(index=False))

    # Visualização
    plt.figure(figsize=(12, 6))
    plt.plot(y_teste.index, y_teste, 'k-o', linewidth=3, label='REAL')
    plt.plot(y_teste.index, previsoes['Regressao'], '--', color='red', linewidth=2, alpha=0.7, label='Regressão')
    plt.plot(y_teste.index, previsoes['SARIMA'], '-.', color='blue', alpha=0.5, label='SARIMA')
    plt.plot(y_teste.index, previsoes['Ensemble'], '-', color='green', linewidth=3, label='Ensemble')
    # plt.plot(y_teste.index, previsoes['HoltWinters'], ':', color='orange', label='HoltWinters') # Opcional se poluir muito
    
    plt.title('Duelo Final: Comparativo de Modelos')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()
else:
    print("Erro: Nenhum dado carregado. Verifique o arquivo 'dataLava.csv'.")