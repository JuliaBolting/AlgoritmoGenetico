from algoritmo_genetico import algoritmo_genetico
from carregar_dados import carregar_dados
from common import st, px, pd, io, mp

mp.set_start_method("spawn", force=True)

st.set_page_config(page_title="Distribuição Logística", layout="wide")
st.title("\U0001F4E6 Otimização de Distribuição de Produtos")

with st.sidebar:
    st.header("\U0001F4C2 Upload dos Arquivos (opcional)")
    estoque_cd = st.file_uploader("Estoque CD", type="csv")
    capacidade_lojas = st.file_uploader("Capacidade das Lojas", type="csv")
    demanda = st.file_uploader("Demanda Semanal", type="csv")
    custos = st.file_uploader("Custo por Caminhão", type="csv")

    st.header("⚙️ Parâmetros do Algoritmo Genético")
    tamanho_populacao = st.slider("Tamanho da População", 10, 200, 100, step=10)
    st.caption("**Tamanho da População**: número de possíveis soluções avaliadas a cada geração (quanto maior, mais variações testadas).")
    num_geracoes = st.slider("Número de Gerações", 10, 500, 200, step=10)
    st.caption("**Número de Gerações**: número de ciclos de evolução (mais gerações podem melhorar o resultado, mas aumentam o tempo de processamento).")
    taxa_mutacao = st.slider("Taxa de Mutação (%)", 0, 100, 50, step=1) / 100
    st.caption("**Taxa de Mutação**: chance de mudar aleatoriamente uma solução (ajuda a evitar que o algoritmo fique preso em soluções ruins).")

    print("Parâmetros Selecionados:")
    print(f"Tamanho da população: {tamanho_populacao}")
    print(f"Número de gerações: {num_geracoes}")
    print(f"Taxa de mutação: {taxa_mutacao}")

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

if st.button("\U0001F69B Executar Algoritmo Genético"):
    with st.spinner("Executando algoritmo genético..."):
        resultado, custo_total = algoritmo_genetico(
            df_estoque, df_capacidade, df_demanda, df_custos,
            tamanho_populacao=tamanho_populacao,
            num_geracoes=num_geracoes,
            taxa_mutacao=taxa_mutacao
        )

    st.success("Otimização concluída!")
    st.markdown(f"### \U0001F4B0 Custo total: R$ {custo_total:,.2f}")

    colunas_envio = [col for col in resultado.columns if not col.startswith("Enviado_") and not col.startswith("Completo_") and col != "Produto"]
    colunas_status = [col for col in resultado.columns if col.startswith("Enviado_") or col.startswith("Completo_")]

    st.markdown("### 📦 Distribuição de Produtos")
    st.dataframe(resultado[["Produto"] + colunas_envio], use_container_width=True)

    st.markdown("### 🟢 Status de Entrega (Enviado e Completo)")
    st.dataframe(resultado[["Produto"] + colunas_status], use_container_width=True)
    st.markdown("""
    - **Colunas `Enviado_<Loja>`**: Indica se algum produto **foi enviado** para essa loja (`sim` ou `não`).
    - **Colunas `Completo_<Loja>`**: Indica se a **demanda total foi atendida** (`sim` ou `não`).
    - Os produtos são enviados **apenas em caixas de 20 unidades**.
    """)

    st.markdown("### 🚛 Custos Logísticos por Loja")
    dados_custo_loja = []
    for loja in colunas_envio:
        total_unidades = resultado[loja].sum()
        caixas = total_unidades // 20
        produtos_viagem = 20
        viagens = caixas
        custo_viagem = float(df_custos.loc[df_custos["Loja"] == loja, "CustoPorCaminhao"].values[0])
        custo_total_loja = viagens * custo_viagem

        dados_custo_loja.append({
            "Loja": loja,
            "Total de Unidades": total_unidades,
            "Caixas (20 unid)": caixas,
            "Produtos/Viagem": produtos_viagem,
            "Nº de Viagens": viagens,
            "Custo por Viagem (R$)": custo_viagem,
            "Custo Total (R$)": custo_total_loja
        })

    df_detalhes_custo = pd.DataFrame(dados_custo_loja)
    st.dataframe(df_detalhes_custo, use_container_width=True)

    st.markdown("### \U0001F4B8 Custo Total por Loja")
    fig = px.bar(df_detalhes_custo, x="Loja", y="Custo Total (R$)", text_auto=".2s")
    st.plotly_chart(fig)

    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        resultado.to_excel(writer, index=False, sheet_name="Distribuicao")
        df_detalhes_custo.to_excel(writer, index=False, sheet_name="Custos")

    st.download_button(
        label="📥 Baixar Resultado como Excel",
        data=excel_buffer.getvalue(),
        file_name="resultado_distribuicao.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )