# 🚿 Dashboard de Gestão Inteligente - Lava Jato

![Status](https://img.shields.io/badge/Status-Em_Desenvolvimento-yellow)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)

Sistema de Apoio à Decisão (SAD) desenvolvido para digitalizar a gestão financeira, monitorar metas semanais e prever demanda de serviços de lavagem automotiva.

## 🎯 Funcionalidades

- **Dashboard Interativo:** Visualização de faturamento diário, semanal e mensal.
- **Gamificação de Metas:** Acompanhamento em tempo real do progresso semanal (Gráfico de Velocímetro).
- **Análise Preditiva:** Utilização de Machine Learning para projetar faturamento futuro.
- **Gestão de Dados:** Módulo de cadastro (CRUD) para inserção de novos serviços diretamente na interface.
- **Relatórios Automatizados:** Visualização limpa com foco em tomada de decisão rápida.

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **Interface:** Streamlit
* **Visualização:** Plotly Express & Graph Objects
* **Manipulação de Dados:** Pandas & NumPy
* **Machine Learning:** Scikit-Learn (Regressão Linear Sazonal)

## 🚀 Como Executar o Projeto

Siga os passos abaixo para rodar o dashboard na sua máquina local:

### 1. Pré-requisitos
Certifique-se de ter o Python e o pip instalados. 

### 2. Instalação das Dependências
Rode o seguinte comando no terminal para instalar as bibliotecas necessárias:
```bash
pip install streamlit pandas numpy plotly scikit-learn
```

### 3. Executando o Dashboard
No terminal, navegue até a pasta do projeto e digite:

```bash
streamlit run ./main.py
```
