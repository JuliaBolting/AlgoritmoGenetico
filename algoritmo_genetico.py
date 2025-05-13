from common import np, random, pd, cf, time, os
from utils import CAPACIDADE_CAMINHAO, CAIXA_UNIDADES

# =========================
# 1. ALGORITMO GENÉTICO
# =========================

def algoritmo_genetico(df_estoque, df_capacidade, df_demanda, df_custos, tamanho_populacao, num_geracoes, taxa_mutacao):
    n_produtos = df_estoque.shape[0]
    n_lojas = df_capacidade.shape[1]

    estoque_cd = df_estoque['EstoqueDisponivel'].to_numpy()
    capacidade_lojas = df_capacidade
    demanda = df_demanda
    custo_caminhao = df_custos['CustoPorCaminhao'].to_numpy()

    populacao = inicializar_populacao(tamanho_populacao, n_produtos, n_lojas)

    # Escolhe o melhor executor para o paralelismo
    _, melhor_executor = benchmark_executor(populacao[:10], estoque_cd, capacidade_lojas, demanda, custo_caminhao)

    for i in range(num_geracoes):
        print(f"[GERAÇÃO {i+1}] Início")
        inicio = time.time()
        avaliacoes = fitness_paralela(populacao, estoque_cd, capacidade_lojas, demanda, custo_caminhao, melhor_executor)
        fim = time.time()
        print(f"[GERAÇÃO {i+1}] Tempo: {fim - inicio:.2f}s")
        aptidoes = [av[0] for av in avaliacoes]
        nova_populacao = []
        for _ in range(tamanho_populacao):
            pai1 = selecao(populacao, aptidoes)
            pai2 = selecao(populacao, aptidoes)
            filho = crossover(pai1, pai2)
            filho = mutacao(filho, taxa_mutacao)
            nova_populacao.append(filho)
        populacao = nova_populacao
        print(f"[GERAÇÃO {i+1}] Fim\n")

    melhor_index = np.argmin(aptidoes)
    melhor_custo, melhor_solucao, enviado, completo = avaliacoes[melhor_index]

    resultado = pd.DataFrame(melhor_solucao, columns=df_demanda.columns)
    resultado.insert(0, "Produto", df_estoque['Produto'])

    for loja in df_demanda.columns:
        idx = df_demanda.columns.get_loc(loja)
        resultado[f"Enviado_{loja}"] = enviado[:, idx]
        resultado[f"Completo_{loja}"] = completo[:, idx]

    return resultado, melhor_custo

def gerar_individuo(n_produtos, n_lojas):
    return np.random.randint(0, 50, size=(n_produtos, n_lojas)) * CAIXA_UNIDADES

def inicializar_populacao(tamanho_populacao, n_produtos, n_lojas):
    return [gerar_individuo(n_produtos, n_lojas) for _ in range(tamanho_populacao)]

def selecao(populacao, aptidoes):
    selecionados = random.choices(list(zip(populacao, aptidoes)), k=10)
    return min(selecionados, key=lambda x: x[1])[0]

def crossover(pai1, pai2):
    return (pai1 + pai2) // 2

def mutacao(individuo, taxa_mutacao):
    if random.random() < taxa_mutacao:
        i = random.randint(0, individuo.shape[0] - 1)
        j = random.randint(0, individuo.shape[1] - 1)
        individuo[i, j] += random.choice([-CAIXA_UNIDADES, CAIXA_UNIDADES])
        individuo[i, j] = max(0, individuo[i, j])
    return individuo


def fitness_paralela(populacao, estoque_cd, capacidade_lojas, demanda, custo_caminhao, executor_cls):
    print("\n[INFO] Iniciando fitness_paralela...")
    cap_lojas_np = capacidade_lojas.to_numpy()
    demanda_np = demanda.to_numpy()
    args = [(ind, estoque_cd, cap_lojas_np, demanda_np, custo_caminhao) for ind in populacao]
    with executor_cls(max_workers=os.cpu_count()) as executor:
        print(f"[INFO] Executor usado: {executor_cls.__name__}")
        resultados = list(executor.map(calcular_aptidao_parallel, args))
    print("[INFO] Finalizou execução paralela!\n")
    return resultados

def calcular_aptidao_parallel(args):
    individuo, estoque_cd, capacidade_lojas, demanda, custo_caminhao = args
    return calcular_aptidao(individuo, estoque_cd, capacidade_lojas, demanda, custo_caminhao)

def calcular_aptidao(individuo, estoque_cd, capacidade_lojas, demanda, custo_caminhao):
    custo_total = 0
    penalidade = 0
    completo = np.full(individuo.shape, "sim", dtype=object)
    enviado = np.full(individuo.shape, "sim", dtype=object)
    individuo_final = np.zeros_like(individuo)

    for loja in range(individuo.shape[1]):
        carga_total = 0
        for prod in range(individuo.shape[0]):
            demanda_loja = demanda[prod, loja]
            capacidade_prod = capacidade_lojas[prod, loja]

            caixas = int(np.floor(demanda_loja / CAIXA_UNIDADES))
            sobra = demanda_loja % CAIXA_UNIDADES
            unidades_enviar = caixas * CAIXA_UNIDADES

            if sobra > 0 and unidades_enviar + CAIXA_UNIDADES <= capacidade_prod:
                unidades_enviar += CAIXA_UNIDADES

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


# =========================
# 4. BENCHMARKS E UTILITÁRIOS
# =========================

def fitness_com_tempo(populacao, estoque_cd, capacidade_lojas, demanda, custo_caminhao, executor_cls):
    inicio = time.time()
    resultado = fitness_paralela(populacao, estoque_cd, capacidade_lojas, demanda, custo_caminhao, executor_cls)
    fim = time.time()
    print(f"[INFO] Tempo com {executor_cls.__name__}: {fim - inicio:.2f}s")
    return resultado

def benchmark_executor(populacao, estoque_cd, capacidade_lojas, demanda, custo_caminhao):
    def executar(executor_cls):
        inicio = time.time()
        resultados = fitness_paralela(populacao, estoque_cd, capacidade_lojas, demanda, custo_caminhao, executor_cls)
        duracao = time.time() - inicio
        return resultados, duracao

    print("\n[INFO] Realizando benchmark entre ThreadPool e ProcessPool...")
    resultados_thread, tempo_thread = executar(cf.ThreadPoolExecutor)
    print(f"[INFO] ThreadPoolExecutor levou {tempo_thread:.2f}s")

    resultados_process, tempo_process = executar(cf.ProcessPoolExecutor)
    print(f"[INFO] ProcessPoolExecutor levou {tempo_process:.2f}s")

    if tempo_thread <= tempo_process:
        print("[INFO] Usando ThreadPoolExecutor\n")
        return resultados_thread, cf.ThreadPoolExecutor
    else:
        print("[INFO] Usando ProcessPoolExecutor\n")
        return resultados_process, cf.ProcessPoolExecutor