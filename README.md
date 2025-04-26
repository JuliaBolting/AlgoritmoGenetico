## Algoritmo Genético
Uma rede de supermercados possui um centro de distribuição (CD) onde são recebidos e ficam armazenados todos os produtos comprados por ela. Esta rede busca distribuir as mercadorias entre suas filiais visando evitar excesso de estoque em algumas unidades e falta em outras. A distribuição deve ser otimizada para minimizar custos logísticos e garantir que cada loja tenha produtos suficientes para atender à demanda prevista.
- A rede de supermercado possui 10 filiais diferentes.
- A rede de supermercados vende 50 produtos diferentes.
- A quantidade de unidades em estoque no CD de cada produto está disponível no arquivo estoque_cd.csv.
- A quantidade de unidades máxima que cada loja pode ter em estoque, considerando o seu espaço físico, está disponível em capacidade_lojas.csv.
- O custo em reais para realizar uma viagem de caminhão entre o CD e uma loja está definido em custo_por_caminhao.csv.
- A demanda semanal de unidades de cada produto, em cada uma das lojas, está especificada em demanda.csv.
- Em cada viagem, um caminhão pode levar 1000 unidades independente do tipo do produto transportado.
- Os produtos são alocados em caixas com 20 unidades cada e não podem ser abertas no CD, ou seja, a quantidade de unidades transportada deve ser sempre múltiplo de 20.

O Algoritmo Genético deve realizar a programação das viagens a serem realizadas na semana para distribuir os produtos entre as lojas, de forma a minimizar custos logísticos, evitar rupturas de estoque (falta de produtos nas lojas) e excesso de mercadorias (para não gerar desperdício ou necessidade de promoções para liquidação).

Para rodar o projeto, digite no terminal:
streamlit run app.py
