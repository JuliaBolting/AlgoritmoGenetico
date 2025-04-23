from common import np, random, pd

TAMANHO_POPULACAO = 50
NUM_GERACOES = 100
TAXA_MUTACAO = 0.1
CAPACIDADE_CAMINHAO = 1000
CAIXA_UNIDADES = 20

def inicializar_populacao(n_produtos, n_lojas):
    return [np.random.randint(0, 50, size=(n_produtos, n_lojas)) * CAIXA_UNIDADES for _ in range(TAMANHO_POPULACAO)]

def calcular_aptidao(individuo, estoque_cd, capacidade_lojas, demanda, custo_caminhao):
    custo_total = 0
    penalidade = 0

    for loja in range(individuo.shape[1]):
        carga_total = np.sum(individuo[:, loja])
        viagens = np.ceil(carga_total / CAPACIDADE_CAMINHAO)
        custo_total += viagens * custo_caminhao[loja]

        for prod in range(individuo.shape[0]):
            enviado = individuo[prod, loja]
            demanda_loja = demanda.iloc[prod, loja]
            capacidade_max = capacidade_lojas.iloc[prod, loja]

            if enviado > capacidade_max:
                penalidade += (enviado - capacidade_max) * 10
            elif enviado < demanda_loja:
                penalidade += (demanda_loja - enviado) * 20

    total_enviado_cd = np.sum(individuo, axis=1)
    excesso_envio = np.maximum(total_enviado_cd - estoque_cd, 0)
    penalidade += np.sum(excesso_envio) * 30

    return custo_total + penalidade

def selecao(populacao, aptidoes):
    selecionados = random.choices(list(zip(populacao, aptidoes)), k=10)
    return min(selecionados, key=lambda x: x[1])[0]

def crossover(pai1, pai2):
    return (pai1 + pai2) // 2

def mutacao(individuo):
    if random.random() < TAXA_MUTACAO:
        i = random.randint(0, individuo.shape[0]-1)
        j = random.randint(0, individuo.shape[1]-1)
        individuo[i, j] += random.choice([-20, 20])
        individuo[i, j] = max(0, individuo[i, j])
    return individuo

def algoritmo_genetico(df_estoque, df_capacidade, df_demanda, df_custos):
    n_produtos = df_estoque.shape[0]
    n_lojas = df_capacidade.shape[1]

    estoque_cd = df_estoque['EstoqueDisponivel'].to_numpy()
    capacidade_lojas = df_capacidade
    demanda = df_demanda
    custo_caminhao = df_custos['CustoPorCaminhao'].to_numpy()

    populacao = inicializar_populacao(n_produtos, n_lojas)

    for _ in range(NUM_GERACOES):
        aptidoes = [calcular_aptidao(ind, estoque_cd, capacidade_lojas, demanda, custo_caminhao) for ind in populacao]
        nova_populacao = []
        for _ in range(TAMANHO_POPULACAO):
            pai1 = selecao(populacao, aptidoes)
            pai2 = selecao(populacao, aptidoes)
            filho = crossover(pai1, pai2)
            filho = mutacao(filho)
            nova_populacao.append(filho)
        populacao = nova_populacao

    aptidoes = [calcular_aptidao(ind, estoque_cd, capacidade_lojas, demanda, custo_caminhao) for ind in populacao]
    melhor_solucao = populacao[np.argmin(aptidoes)]
    melhor_custo = min(aptidoes)

    resultado = pd.DataFrame(melhor_solucao, columns=df_demanda.columns)
    resultado.insert(0, "Produto", df_estoque['Produto'])

    return resultado, melhor_custo