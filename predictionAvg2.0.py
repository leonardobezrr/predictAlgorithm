import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import SimpleExpSmoothing, ExponentialSmoothing
from sklearn.linear_model import LinearRegression

# --- CARREGAMENTO E PREPARAÇÃO ---
df = pd.read_csv('dataLava.csv')
df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', dayfirst=True, errors='coerce')
df_diario = df.groupby('Data')['Valor (R$)'].sum().asfreq('D').fillna(0)

# Divisão Treino/Teste (Últimos 7 dias)
dias_teste = 7
y_treino = df_diario.iloc[:-dias_teste]
y_teste = df_diario.iloc[-dias_teste:]

# --- TREINAMENTO DOS MODELOS AVANÇADOS ---

previsoes = pd.DataFrame(index=y_teste.index)
previsoes['Real'] = y_teste

# O Campeão Atual: Média Móvel 7 dias
previsoes['MMS_7'] = df_diario.rolling(window=7).mean().shift(1).loc[y_teste.index]

# Suavização Exponencial Simples (SES)
modelo_ses = SimpleExpSmoothing(y_treino).fit()
previsoes['SES'] = modelo_ses.forecast(dias_teste)

# Holt-Winters (Sazonalidade Aditiva)
# seasonal_periods=7 (Ciclo semanal)
try:
    modelo_hw = ExponentialSmoothing(y_treino, seasonal_periods=7, trend='add', seasonal='add').fit()
    previsoes['HoltWinters'] = modelo_hw.forecast(dias_teste)
except:
    previsoes['HoltWinters'] = np.nan
    print("Erro ao ajustar Holt-Winters (Dados insuficientes ou padrão não convergente)")

# Regressão Linear Sazonal (Dummy Variables)
# Preparando dados para regressão
df_reg = df_diario.reset_index()
df_reg['Dia_Semana'] = df_reg['Data'].dt.dayofweek
df_reg['Tempo'] = np.arange(len(df_reg)) # Tendência temporal (0, 1, 2...)

# Criando variáveis dummy (0 ou 1 para cada dia da semana)
df_dummies = pd.get_dummies(df_reg['Dia_Semana'], prefix='Dia', drop_first=True)
df_reg = pd.concat([df_reg, df_dummies], axis=1)

# Separando X (Variáveis) e Y (Alvo) para Treino e Teste
X = df_reg.drop(['Data', 'Valor (R$)', 'Dia_Semana'], axis=1)
Y = df_reg['Valor (R$)']

X_treino_reg = X.iloc[:-dias_teste]
Y_treino_reg = Y.iloc[:-dias_teste]
X_teste_reg = X.iloc[-dias_teste:]

modelo_reg = LinearRegression()
modelo_reg.fit(X_treino_reg, Y_treino_reg)
previsoes['Regressao'] = modelo_reg.predict(X_teste_reg)

# --- CÁLCULO DOS RESULTADOS ---

resultados = []

def avaliar(modelo, y_r, y_p):
    # Remove NaN se houver
    mask = ~np.isnan(y_p)
    y_r = y_r[mask]
    y_p = y_p[mask]
    
    mae = mean_absolute_error(y_r, y_p)
    rmse = np.sqrt(mean_squared_error(y_r, y_p))
    
    # MAPE ajustado (Ignora zeros reais para não dividir por zero)
    mask_valida = y_r != 0
    if mask_valida.sum() > 0:
        mape = np.mean(np.abs((y_r[mask_valida] - y_p[mask_valida]) / y_r[mask_valida])) * 100
    else:
        mape = 0
        
    return {'Modelo': modelo, 'MAE (R$)': round(mae, 2), 'MAPE (%)': round(mape, 2), 'RMSE': round(rmse, 2)}

for col in ['MMS_7', 'SES', 'HoltWinters', 'Regressao']:
    resultados.append(avaliar(col, previsoes['Real'], previsoes[col]))

df_res = pd.DataFrame(resultados).sort_values(by='MAE (R$)')

print("\n🏆 CLASSIFICAÇÃO FINAL DOS MODELOS:")
print(df_res)

# --- GRÁFICO COMPARATIVO ---
plt.figure(figsize=(14, 7))
plt.plot(y_teste.index, y_teste, label='REAL', color='black', linewidth=3, marker='o')
plt.plot(y_teste.index, previsoes['MMS_7'], label='Média Móvel (7d)', linestyle='--', alpha=0.7)
plt.plot(y_teste.index, previsoes['HoltWinters'], label='Holt-Winters', linewidth=4, color='red')
plt.plot(y_teste.index, previsoes['Regressao'], label='Regressão Sazonal', linewidth=2, color='green')


plt.title('Batalha de Predição: Quem acerta o ciclo semanal?')
plt.ylabel('Faturamento (R$)')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()