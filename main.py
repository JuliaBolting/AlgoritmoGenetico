from algoritmo_genetico import algoritmo_genetico
from carregar_dados import carregar_dados
from common import st, px

st.set_page_config(page_title="Distribuição Logística", layout="wide")
st.title("📦 Otimização de Distribuição de Produtos")

with st.sidebar:
    st.header("📂 Upload dos Arquivos (opcional)")
    estoque_cd = st.file_uploader("Estoque CD", type="csv")
    capacidade_lojas = st.file_uploader("Capacidade das Lojas", type="csv")
    demanda = st.file_uploader("Demanda Semanal", type="csv")
    custos = st.file_uploader("Custo por Caminhão", type="csv")

    st.header("⚙️ Parâmetros do Algoritmo Genético")
    tamanho_populacao = st.slider("Tamanho da População", 10, 200, 50, step=10)
    st.caption("**TAMANHO_POPULACAO**: número de possíveis soluções avaliadas a cada geração (quanto maior, mais variações testadas).")
    num_geracoes = st.slider("Número de Gerações", 10, 500, 100, step=10)
    st.caption("**NUM_GERACOES**: número de ciclos de evolução (mais gerações podem melhorar o resultado, mas aumentam o tempo de processamento).")
    taxa_mutacao = st.slider("Taxa de Mutação (%)", 0, 100, 10, step=1) / 100
    st.caption("**TAXA_MUTACAO**: chance de mudar aleatoriamente uma solução (ajuda a evitar que o algoritmo fique preso em soluções ruins).")

DEFAULT_PATHS = {
    "estoque_cd": "archives/estoque_cd.csv",
    "capacidade_lojas": "archives/capacidade_lojas.csv",
    "demanda": "archives/demanda.csv",
    "custos": "archives/custo_por_caminhao.csv"
}

df_estoque, df_capacidade, df_demanda, df_custos = carregar_dados(
    estoque_cd if estoque_cd else DEFAULT_PATHS["estoque_cd"],
    capacidade_lojas if capacidade_lojas else DEFAULT_PATHS["capacidade_lojas"],
    demanda if demanda else DEFAULT_PATHS["demanda"],
    custos if custos else DEFAULT_PATHS["custos"]
)

if st.button("🚛 Executar Algoritmo Genético"):
    resultado, custo_total = algoritmo_genetico(
        df_estoque, df_capacidade, df_demanda, df_custos,
        tamanho_populacao=tamanho_populacao,
        num_geracoes=num_geracoes,
        taxa_mutacao=taxa_mutacao
    )

    st.subheader("📋 Resultado da Distribuição")
    st.dataframe(resultado)
    st.caption("""
Esta tabela mostra como os produtos do Centro de Distribuição (CD) foram distribuídos para as lojas. 
Cada linha representa um produto e cada coluna indica a quantidade enviada para cada loja.
O objetivo é atender a demanda das lojas respeitando as capacidades de estoque, minimizando custos logísticos.
""")

    st.metric("💰 Custo Total", f"R$ {custo_total:,.2f}")
    st.write("")
    
    st.subheader("📊 Total de Produtos Enviados por Loja")
    total_envios_por_loja = resultado.iloc[:, 1:].sum()
    fig = px.bar(total_envios_por_loja, labels={'index': 'Loja', 'value': 'Total de Unidades'}, title="Total de Unidades por Loja")
    st.plotly_chart(fig)
    st.caption("""
Este gráfico ilustra visualmente a quantidade de produtos distribuída para cada loja.
Ele ajuda a identificar rapidamente se alguma loja está recebendo mais ou menos produtos em comparação às outras.
""")

    st.write("")
    csv = resultado.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar Resultado como CSV",
        data=csv,
        file_name='resultado_distribuicao.csv',
        mime='text/csv'
    )