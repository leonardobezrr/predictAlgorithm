import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.linear_model import LinearRegression
from statsmodels.tsa.holtwinters import ExponentialSmoothing
import warnings
warnings.filterwarnings("ignore") 

# --- CARREGAMENTO (ETL) ---
def carregar_dados():
    df = pd.read_csv('dataLava.csv')
    def corrigir(x):
        s = str(x).strip()
        return s + "/2025" if len(s) <= 5 else s
    df['Data'] = df['Data'].apply(corrigir)
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', dayfirst=True, errors='coerce')
    return df.groupby('Data')['Valor (R$)'].sum().asfreq('D').fillna(0)

y = carregar_dados()
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
reg = LinearRegression().fit(X.iloc[:-dias_teste], y_treino)
previsoes['Regressao'] = reg.predict(X.iloc[-dias_teste:])

# Holt-Winters Multiplicativo (Vice)
try:
    hw = ExponentialSmoothing(y_treino, seasonal_periods=7, trend='add', seasonal='add').fit()
    previsoes['HoltWinters'] = hw.forecast(dias_teste)
except:
    previsoes['HoltWinters'] = np.nan # Fallback

# --- OS NOVOS ALGORITMOS ---

# SARIMA (Seasonal ARIMA)
# Parâmetros (1,0,1) x (1,0,1,7) são padrão para sazonalidade semanal estável
# P = 1 (Autoregressivo Sazonal): A venda deste sábado depende do sábado passado.
# D = 0 (Integração): Os dados parecem estacionários na média.
# Q = 1 (Média Móvel Sazonal): Correção de erro baseada na semana anterior.
# s = 7 (Ciclo semanal)
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
    previsoes['SARIMA'] = np.nan

# ENSEMBLE (O Modelo "Média dos Campeões")
# Pega a Regressão + HoltWinters e divide por 2.
previsoes['Ensemble'] = (previsoes['Regressao'] + previsoes['HoltWinters']) / 2

# --- PLACAR FINAL ---
placar = []
for col in previsoes.columns:
    if col == 'Real': continue
    
    # Tratando erros
    serie_p = previsoes[col].fillna(0)
    serie_p = serie_p.apply(lambda x: max(x, 0)) # Não existe faturamento negativo
    
    mae = mean_absolute_error(y_teste, serie_p)
    placar.append({'Modelo': col, 'MAE (R$)': round(mae, 2)})

df_placar = pd.DataFrame(placar).sort_values('MAE (R$)')

print("\n🏆 RANKING DEFINITIVO DE PRECISÃO:")
print(df_placar)

# Visualização
plt.figure(figsize=(12, 6))
plt.plot(y_teste.index, y_teste, 'k-o', linewidth=3, label='REAL')
plt.plot(y_teste.index, previsoes['Regressao'], '--', color='red', linewidth=4, alpha=0.5, label='Regressão')
plt.plot(y_teste.index, previsoes['SARIMA'], '-.', color='blue', label='SARIMA')
plt.plot(y_teste.index, previsoes['Ensemble'], '-', color='green', linewidth=4, label='Ensemble (Híbrido)')
plt.plot(y_teste.index, previsoes['HoltWinters'], '-', color='orange', linewidth=3, label='Holtwinters')
plt.title('Duelo Final: Estatística Clássica vs Híbrida')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()