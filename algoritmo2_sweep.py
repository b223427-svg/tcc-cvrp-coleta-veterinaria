# =============================================================
# ALGORITMO 2 — SWEEP + GULOSO
#
# Estratégia em duas etapas:
# 1. SWEEP (clustering): ordena os pontos por ângulo polar em
#    relação ao depósito e agrupa respeitando Q=10.
# 2. GULOSO (roteamento): dentro de cada cluster, constrói a
#    rota sempre indo ao ponto mais próximo ainda não visitado.
# =============================================================

#Importação de bibliotecas
import os
import math
import time

# -------------------------------------------------------
# Configurações
# -------------------------------------------------------
CAPACIDADE = 10          # Q: máximo de exames por rota
PASTA_INSTANCIAS = r"C:\Users\Usuario\Desktop\tcc_benchmark\instancias"
PASTA_RESULTADOS = r"C:\Users\Usuario\Desktop\tcc_benchmark\algoritmos\resultados_sweep"

# -------------------------------------------------------
# Leitura do arquivo .VRP
# -------------------------------------------------------
def ler_vrp(caminho):
    with open(caminho, 'r') as f:
        linhas = f.readlines()

    dimensao = 0
    max_veiculos = 0
    matriz = []
    coordenadas = {}
    depot = 0
    modo = None
    valores = []

    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        if linha.startswith("DIMENSION"):
            dimensao = int(linha.split(":")[1].strip())
        elif linha.startswith("MAX_VEHICLES"):
            max_veiculos = int(linha.split(":")[1].strip())
        elif linha == "EDGE_WEIGHT_SECTION":
            modo = "matriz"
        elif linha == "DISPLAY_DATA_SECTION":
            modo = "coordenadas"
            if valores:
                n = dimensao + 1
                matriz = [[float(valores[i * n + j]) for j in range(n)] for i in range(n)]
        elif linha == "DEPOT_SECTION":
            modo = "depot"
        elif linha == "EOF":
            modo = None
        elif modo == "matriz":
            valores.extend(linha.split())
        elif modo == "coordenadas":
            partes = linha.split()
            if len(partes) >= 3:
                coordenadas[int(partes[0])] = (float(partes[1]), float(partes[2]))
        elif modo == "depot":
            if linha != "-1":
                depot = int(linha)

    return dimensao, max_veiculos, matriz, coordenadas, depot

# -------------------------------------------------------
# ETAPA 1: Sweep Clustering
# -------------------------------------------------------
def sweep_clustering(coordenadas, depot, dimensao, capacidade, matriz):
    """
    Clustering por vizinhança:
    1. Começa pelo ponto mais distante do depósito
    2. Expande o cluster pegando sempre o vizinho mais próximo
       do último ponto adicionado
    3. Quando o cluster enche (Q), abre um novo a partir do
       próximo ponto mais distante ainda não visitado
    """
    nao_visitados = set(range(1, dimensao + 1))
    clusters = []

    while nao_visitados:
        # abre novo cluster pelo ponto mais longe do depósito
        ponto_inicial = max(nao_visitados, key=lambda p: matriz[depot][p])
        cluster_atual = [ponto_inicial]
        nao_visitados.remove(ponto_inicial)
        atual = ponto_inicial

        # expande pelo vizinho mais próximo do último ponto
        while len(cluster_atual) < capacidade and nao_visitados:
            proximo = min(nao_visitados, key=lambda p: matriz[atual][p])
            cluster_atual.append(proximo)
            nao_visitados.remove(proximo)
            atual = proximo

        clusters.append(cluster_atual)

    return clusters

# -------------------------------------------------------
# ETAPA 2: Roteamento guloso dentro do cluster 
# -------------------------------------------------------
def rota_gulosa_cluster(cluster, depot, matriz):
    """
    Constrói a rota dentro de um cluster usando o vizinho mais próximo.
    Parte do depósito, vai sempre ao ponto mais próximo não visitado,
    e retorna ao depósito no final.
    """
    nao_visitados = set(cluster)
    rota = [depot]
    custo = 0
    atual = depot

    while nao_visitados:
        melhor = min(nao_visitados, key=lambda p: matriz[atual][p])
        custo += matriz[atual][melhor]
        rota.append(melhor)
        atual = melhor
        nao_visitados.remove(melhor)

    # volta ao depósito
    custo += matriz[atual][depot]
    rota.append(depot)

    return rota, custo

# -------------------------------------------------------
# Algoritmo SWEEP + GULOSO
# -------------------------------------------------------
def algoritmo_sweep(dimensao, max_veiculos, matriz, coordenadas, depot, capacidade):
    clusters = sweep_clustering(coordenadas, depot, dimensao, capacidade, matriz)  # ← adiciona matriz

    rotas = []
    custo_total = 0

    for cluster in clusters:
        rota, custo = rota_gulosa_cluster(cluster, depot, matriz)
        rotas.append(rota)
        custo_total += custo

    return rotas, custo_total

# -------------------------------------------------------
# Formatação de Resultados
# -------------------------------------------------------
def formatar_resultado(nome_instancia, rotas, custo_total, tempo_seg):
    linhas = []
    linhas.append(f"Instância: {nome_instancia}")
    linhas.append(f"Algoritmo: Sweep + Guloso")
    linhas.append(f"Número de rotas utilizadas: {len(rotas)}")
    linhas.append(f"Custo total (segundos): {custo_total:.3f}")
    linhas.append(f"Tempo de execução: {tempo_seg:.4f}s")
    linhas.append("")
    for i, rota in enumerate(rotas):
        rota_str = " -> ".join(str(p) for p in rota)
        linhas.append(f"  Rota {i+1}: {rota_str}")
    linhas.append("=" * 60)
    return "\n".join(linhas)

# -------------------------------------------------------
# Execução Principal
# -------------------------------------------------------
def main():
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)

    arquivos_vrp = []
    for subpasta in sorted(os.listdir(PASTA_INSTANCIAS)):
        caminho_subpasta = os.path.join(PASTA_INSTANCIAS, subpasta)
        if os.path.isdir(caminho_subpasta):
            for arquivo in os.listdir(caminho_subpasta):
                if arquivo.endswith(".vrp") and not arquivo.endswith(".vrp.png"):
                    arquivos_vrp.append(os.path.join(caminho_subpasta, arquivo))

    if not arquivos_vrp:
        print(f"Nenhum arquivo .vrp encontrado em: {PASTA_INSTANCIAS}")
        return

    print(f"{'Instância':<30} {'Rotas':>6} {'Custo Total (s)':>18} {'Tempo':>10}")
    print("-" * 70)

    resumo_total = []

    for caminho in sorted(arquivos_vrp):
        nome = os.path.basename(caminho).replace(".vrp", "")

        dimensao, max_veiculos, matriz, coordenadas, depot = ler_vrp(caminho)

        inicio = time.time()
        rotas, custo_total = algoritmo_sweep(
            dimensao, max_veiculos, matriz, coordenadas, depot, CAPACIDADE
        )
        tempo = time.time() - inicio

        resultado = formatar_resultado(nome, rotas, custo_total, tempo)
        resumo_total.append(resultado)

        caminho_saida = os.path.join(PASTA_RESULTADOS, nome + "_sweep.txt")
        with open(caminho_saida, 'w') as f:
            f.write(resultado)

        print(f"{nome:<30} {len(rotas):>6} {custo_total:>18.3f} {tempo:>9.4f}s")

    caminho_resumo = os.path.join(PASTA_RESULTADOS, "RESUMO_SWEEP.txt")
    with open(caminho_resumo, 'w') as f:
        f.write("\n".join(resumo_total))

    print("-" * 70)
    print(f"\nResultados salvos em: {PASTA_RESULTADOS}")

if __name__ == "__main__":
    main()