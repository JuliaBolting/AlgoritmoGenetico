import pandas as pd
import streamlit as st
from algoritmo_genetico import algoritmo_genetico
from carregar_dados import carregar_dados
from utils import normalizar_colunas

st.set_page_config(page_title="Distribuição Logística", layout="wide")
st.title("📦 Otimização de Distribuição de Produtos")

with st.sidebar:
    st.header("📂 Upload dos Arquivos (opcional)")
    
    estoque_cd = st.file_uploader("Estoque CD", type="csv")
    capacidade_lojas = st.file_uploader("Capacidade das Lojas", type="csv")
    demanda = st.file_uploader("Demanda Semanal", type="csv")
    custos = st.file_uploader("Custo por Caminhão", type="csv")

# Define os caminhos padrão
DEFAULT_PATHS = {
    "estoque_cd": "archives/estoque_cd.csv",
    "capacidade_lojas": "archives/capacidade_lojas.csv",
    "demanda": "archives/demanda.csv",
    "custos": "archives/custo_por_caminhao.csv"
}

# Usa os arquivos de upload se existirem, senão os arquivos padrão
df_estoque = pd.read_csv(estoque_cd) if estoque_cd else pd.read_csv(DEFAULT_PATHS["estoque_cd"])
df_capacidade_raw = pd.read_csv(capacidade_lojas) if capacidade_lojas else pd.read_csv(DEFAULT_PATHS["capacidade_lojas"])
df_demanda = pd.read_csv(demanda) if demanda else pd.read_csv(DEFAULT_PATHS["demanda"])
df_custos = pd.read_csv(custos) if custos else pd.read_csv(DEFAULT_PATHS["custos"])

# Normaliza nomes das colunas
normalizar_colunas(df_estoque, df_capacidade_raw, df_demanda, df_custos)

# Reestrutura a capacidade das lojas
lojas = df_capacidade_raw['Loja']
capacidades = df_capacidade_raw['Capacidade']
df_capacidade = pd.DataFrame([capacidades.values] * df_demanda.shape[0], columns=lojas)

if st.button("🚛 Executar Algoritmo Genético"):
    resultado, custo_total = algoritmo_genetico(df_estoque, df_capacidade, df_demanda.iloc[:, 1:], df_custos)

    st.subheader("📋 Resultado da Distribuição")
    st.dataframe(resultado)

    st.metric("💰 Custo Total", f"R$ {custo_total:,.2f}")