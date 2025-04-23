from common import st
from algoritmo_genetico import algoritmo_genetico
from carregar_dados import carregar_dados

st.set_page_config(page_title="Distribuição Logística", layout="wide")
st.title("📦 Otimização de Distribuição de Produtos")

with st.sidebar:
    st.header("📂 Upload dos Arquivos")
    estoque_cd = st.file_uploader("Estoque CD", type="csv")
    capacidade_lojas = st.file_uploader("Capacidade das Lojas", type="csv")
    demanda = st.file_uploader("Demanda Semanal", type="csv")
    custos = st.file_uploader("Custo por Caminhão", type="csv")

if estoque_cd and capacidade_lojas and demanda and custos:
    df_estoque, df_capacidade, df_demanda, df_custos = carregar_dados(
        estoque_cd, capacidade_lojas, demanda, custos
    )

    if st.button("🚛 Executar Algoritmo Genético"):
        resultado, custo_total = algoritmo_genetico(df_estoque, df_capacidade, df_demanda, df_custos)

        st.subheader("📋 Resultado da Distribuição")
        st.dataframe(resultado)
        st.metric("💰 Custo Total", f"R$ {custo_total:,.2f}")
