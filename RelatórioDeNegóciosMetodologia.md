
# 📑 Relatório de Inteligência de Negócios

## 1. O Problema de Negócio
O Lava Jato operava historicamente com gestão baseada na intuição. Os principais desafios identificados foram:
1.  **Falta de Visibilidade:** O gestor não sabia exatamente quanto faturava por semana até fechar o caixa manualmente.
2.  **Sazonalidade Desconhecida:** Dificuldade em prever a demanda de finais de semana para alocar equipe extra.
3.  **Metas Inexistentes:** A equipe operacional trabalhava sem um objetivo financeiro claro e visual.

## 2. Metodologia Aplicada

### 2.1 Coleta e Tratamento (ETL)
Os dados foram digitalizados a partir dos registros manuais diários.
* **Limpeza:** Tratamento de datas e padronização monetária.
* **Feature Engineering:** Criação de variáveis temporais (Dia da Semana, Mês, Ano) para análise de sazonalidade.

### 2.2 Modelagem Preditiva
Para a previsão de demanda, realizou-se um estudo comparativo entre três abordagens:
* *Médias Móveis:* Descartado por atraso na resposta (lag).
* *Holt-Winters:* Descartado devido à sensibilidade excessiva aos zeros dos domingos.
* **Regressão Linear com Dummies (Escolhido):** O modelo vencedor. Utilizou-se variáveis categóricas (One-Hot Encoding) para os dias da semana.
    * **Justificativa:** O modelo capturou com precisão o padrão de negócio onde "Sábado" é consistentemente o dia de maior pico, independente da tendência geral de crescimento.

## 3. Guia do Usuário

### Painel Principal
* **Velocímetro de Meta:** Mostra o quanto falta para atingir o objetivo semanal.
    * 🔴 **Vermelho:** Início da meta.
    * 🟡 **Amarelo:** Progresso em andamento.
    * 🟢 **Verde:** Meta próxima ou batida.
* **Gráficos de Barras:** Ao passar o mouse, visualize o valor monetário e a quantidade de veículos.

## 4. Conclusão e Resultados
A implementação do dashboard permitiu:
* Monitoramento em tempo real do fluxo de caixa.
* Aumento do engajamento da equipe através da gamificação da meta visual.
* Redução de incerteza na compra de insumos para os finais de semana.
