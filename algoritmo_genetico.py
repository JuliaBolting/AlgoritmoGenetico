from common import np, random, pd
from utils import TAMANHO_POPULACAO, CAPACIDADE_CAMINHAO, CAIXA_UNIDADES

def inicializar_populacao(n_produtos, n_lojas):
    return [np.random.randint(0, 50, size=(n_produtos, n_lojas)) * CAIXA_UNIDADES for _ in range(TAMANHO_POPULACAO)]

def calcular_aptidao(individuo, estoque_cd, capacidade_lojas, demanda, custo_caminhao):
    custo_total = 0
    penalidade = 0
    completo = np.full(individuo.shape, "sim", dtype=object)
    enviado = np.full(individuo.shape, "sim", dtype=object)

    individuo_final = np.zeros_like(individuo)

    for loja in range(individuo.shape[1]):
        carga_total = 0
        for prod in range(individuo.shape[0]):
            demanda_loja = demanda.iloc[prod, loja]
            capacidade_prod = capacidade_lojas.iloc[prod, loja]

            caixas = int(np.floor(demanda_loja / 20))
            sobra = demanda_loja % 20
            unidades_enviar = caixas * 20

            if sobra > 0 and unidades_enviar + 20 <= capacidade_prod:
                unidades_enviar += 20

            if unidades_enviar > capacidade_prod:
                unidades_enviar = capacidade_prod
                enviado[prod, loja] = "não"
                completo[prod, loja] = "não"
                penalidade += 50
            elif unidades_enviar < demanda_loja:
                completo[prod, loja] = "não"
                penalidade += 30 * (demanda_loja - unidades_enviar)

            individuo_final[prod, loja] = unidades_enviar
            carga_total += unidades_enviar

        viagens = np.ceil(carga_total / CAPACIDADE_CAMINHAO)
        custo_total += viagens * custo_caminhao[loja]

    total_envio_cd = np.sum(individuo_final, axis=1)
    excesso = np.maximum(total_envio_cd - estoque_cd, 0)
    penalidade += np.sum(excesso) * 100

    return custo_total + penalidade, individuo_final, enviado, completo

def selecao(populacao, aptidoes):
    selecionados = random.choices(list(zip(populacao, aptidoes)), k=10)
    return min(selecionados, key=lambda x: x[1])[0]

def crossover(pai1, pai2):
    return (pai1 + pai2) // 2

def mutacao(individuo, taxa_mutacao):
    if random.random() < taxa_mutacao:
        i = random.randint(0, individuo.shape[0]-1)
        j = random.randint(0, individuo.shape[1]-1)
        individuo[i, j] += random.choice([-20, 20])
        individuo[i, j] = max(0, individuo[i, j])
    return individuo

def calcular_aptidao_parallel(args):
    individuo, estoque_cd, capacidade_lojas, demanda, custo_caminhao = args
    return calcular_aptidao(individuo, estoque_cd, capacidade_lojas, demanda, custo_caminhao)


def algoritmo_genetico(df_estoque, df_capacidade, df_demanda, df_custos, tamanho_populacao=50, num_geracoes=100, taxa_mutacao=0.1):
    n_produtos = df_estoque.shape[0]
    n_lojas = df_capacidade.shape[1]

    estoque_cd = df_estoque['EstoqueDisponivel'].to_numpy()
    capacidade_lojas = df_capacidade
    demanda = df_demanda
    custo_caminhao = df_custos['CustoPorCaminhao'].to_numpy()

    populacao = [np.random.randint(0, 50, size=(n_produtos, n_lojas)) * 20 for _ in range(tamanho_populacao)]

    for _ in range(num_geracoes):
        avaliacoes = [calcular_aptidao(ind, estoque_cd, capacidade_lojas, demanda, custo_caminhao) for ind in populacao]
        aptidoes = [av[0] for av in avaliacoes]
        nova_populacao = []
        for _ in range(tamanho_populacao):
            pai1 = selecao(populacao, aptidoes)
            pai2 = selecao(populacao, aptidoes)
            filho = crossover(pai1, pai2)
            filho = mutacao(filho, taxa_mutacao)
            nova_populacao.append(filho)
        populacao = nova_populacao

    melhor_index = np.argmin(aptidoes)
    melhor_custo, melhor_solucao, enviado, completo = avaliacoes[melhor_index]

    resultado = pd.DataFrame(melhor_solucao, columns=df_demanda.columns)
    resultado.insert(0, "Produto", df_estoque['Produto'])

    for loja in df_demanda.columns:
        idx = df_demanda.columns.get_loc(loja)
        resultado[f"Enviado_{loja}"] = enviado[:, idx]
        resultado[f"Completo_{loja}"] = completo[:, idx]

    return resultado, melhor_custo