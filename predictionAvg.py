import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error

# --- PREPARAÇÃO DOS DADOS (ETL) ---
def carregar_e_preparar():
    # Carregando o arquivo tratado
    df = pd.read_csv('dataLava.csv')
    
    # Garantindo que a data é data
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', dayfirst=True, errors='coerce')
    
    # Agrupa por dia (Soma o faturamento diário)
    # .asfreq('D') cria linhas para os dias que faltam (domingos) e preenche com 0
    df_diario = df.groupby('Data')['Valor (R$)'].sum().asfreq('D').fillna(0)
    
    return df_diario

# Carregando
y = carregar_e_preparar()

# Define Treino e Teste
# Vamos usar os últimos 7 dias para TESTE (Prova Final)
# O restante é TREINO (Estudo)
dias_teste = 7
y_treino = y.iloc[:-dias_teste]
y_teste = y.iloc[-dias_teste:]

print(f"Periodo de Treino: {len(y_treino)} dias")
print(f"Periodo de Teste: {len(y_teste)} dias (A semana que vamos tentar adivinhar)")
print("-" * 30)

# --- CRIAÇÃO DOS MODELOS ---

# DataFrame para guardar as previsões
previsoes = pd.DataFrame(index=y_teste.index)
previsoes['Real'] = y_teste

# Modelo Naive (Ingênuo): Previsão = Valor de ontem
# shift(1) pega o valor do dia anterior
previsoes['Naive'] = y.shift(1).loc[y_teste.index]

# Média Móvel Simples (3 dias)
previsoes['MMS_3'] = y.rolling(window=3).mean().shift(1).loc[y_teste.index]

# Média Móvel Simples (7 dias)
previsoes['MMS_7'] = y.rolling(window=7).mean().shift(1).loc[y_teste.index]

# --- CÁLCULO DOS ERROS  ---

resultados = []

def calcular_metricas(nome_modelo, y_real, y_previsto):
    # Removendo dias onde não houve previsão (ex: primeiros dias) ou dias zerados para o MAPE não explodir
    mask = ~np.isnan(y_previsto)
    y_r = y_real[mask]
    y_p = y_previsto[mask]
    
    mae = mean_absolute_error(y_r, y_p) # Erro em Reais
    rmse = np.sqrt(mean_squared_error(y_r, y_p)) # Penaliza erros grandes
    
    # MAPE (Erro Percentual) - Tratamento para não dividir por zero
    mask_nonzero = y_r != 0
    if mask_nonzero.sum() > 0:
        mape = np.mean(np.abs((y_r[mask_nonzero] - y_p[mask_nonzero]) / y_r[mask_nonzero])) * 100
    else:
        mape = np.nan
        
    return {'Modelo': nome_modelo, 'MAE (R$)': round(mae, 2), 'MAPE (%)': round(mape, 2), 'RMSE': round(rmse, 2)}

resultados.append(calcular_metricas('Naive (Ontem)', previsoes['Real'], previsoes['Naive']))
resultados.append(calcular_metricas('Média Móvel (3 dias)', previsoes['Real'], previsoes['MMS_3']))
resultados.append(calcular_metricas('Média Móvel (7 dias)', previsoes['Real'], previsoes['MMS_7']))

# --- EXIBIÇÃO ---

df_resultados = pd.DataFrame(resultados)
print("\n📊 PLACAR FINAL DOS MODELOS SIMPLES:")
print(df_resultados)

# Gráfico
plt.figure(figsize=(12, 6))
plt.plot(y_treino.index[-14:], y_treino[-14:], label='Treino (Histórico Recente)', color='gray', alpha=0.5)
plt.plot(y_teste.index, y_teste, label='REAL (Gabarito)', color='black', linewidth=2, marker='o')
plt.plot(y_teste.index, previsoes['Naive'], label='Naive', linestyle='--')
plt.plot(y_teste.index, previsoes['MMS_3'], label='Média Móvel (3d)', linestyle='--')
plt.plot(y_teste.index, previsoes['MMS_7'], label='Média Móvel (7d)', linestyle='--')

plt.title('Teste de Modelos de Predição: Última Semana')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()