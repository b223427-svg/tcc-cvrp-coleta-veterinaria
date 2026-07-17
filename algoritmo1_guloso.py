# =============================================================
# ALGORITMO 1 — GULOSO PURO
# TCC - Beatriz Ducatti de Almeida - UNICAMP/FT 2025
#
# Estratégia: a partir do depósito, sempre vai ao ponto de
# coleta mais próximo ainda não visitado que caiba na mochila.
# Quando a mochila enche (Q=10), fecha a rota e abre uma nova.
# =============================================================

import os
import math
import time

# -------------------------------------------------------
# CONFIGURAÇÕES
# -------------------------------------------------------
CAPACIDADE = 10          # Q: máximo de exames por rota
PASTA_INSTANCIAS = r"C:\Users\Usuario\Desktop\tcc_benchmark\instancias"
PASTA_RESULTADOS = r"C:\Users\Usuario\Desktop\tcc_benchmark\algoritmos\resultados_guloso"

# -------------------------------------------------------
# LEITURA DO ARQUIVO .VRP
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
# ALGORITMO GULOSO PURO
# -------------------------------------------------------
def algoritmo_guloso(dimensao, max_veiculos, matriz, depot, capacidade):
    """
    Constrói rotas de forma gulosa:
    - Sempre vai ao ponto não visitado mais próximo que caiba na mochila.
    - Quando a mochila enche, fecha a rota e abre uma nova.
    """
    nao_visitados = set(range(1, dimensao + 1))  # pontos 1..N (0 é depósito)
    rotas = []
    custo_total = 0

    while nao_visitados:
        # abre nova rota
        rota = [depot]
        carga = 0
        atual = depot
        custo_rota = 0

        while True:
            # encontra o ponto mais próximo que cabe na mochila
            melhor = None
            menor_dist = math.inf

            for ponto in nao_visitados:
                if carga + 1 <= capacidade:
                    dist = matriz[atual][ponto]
                    if dist < menor_dist:
                        menor_dist = dist
                        melhor = ponto

            if melhor is None:
                break  # mochila cheia ou não há mais pontos

            # vai para o melhor ponto
            rota.append(melhor)
            custo_rota += menor_dist
            carga += 1
            atual = melhor
            nao_visitados.remove(melhor)

        # volta ao depósito
        custo_rota += matriz[atual][depot]
        rota.append(depot)

        rotas.append(rota)
        custo_total += custo_rota

    return rotas, custo_total

# -------------------------------------------------------
# FORMATAÇÃO DOS RESULTADOS
# -------------------------------------------------------
def formatar_resultado(nome_instancia, rotas, custo_total, tempo_seg):
    linhas = []
    linhas.append(f"Instância: {nome_instancia}")
    linhas.append(f"Algoritmo: Guloso Puro")
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
# EXECUÇÃO PRINCIPAL
# -------------------------------------------------------
def main():
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)

    # busca .vrp dentro das subpastas
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
        rotas, custo_total = algoritmo_guloso(dimensao, max_veiculos, matriz, depot, CAPACIDADE)
        tempo = time.time() - inicio

        resultado = formatar_resultado(nome, rotas, custo_total, tempo)
        resumo_total.append(resultado)

        caminho_saida = os.path.join(PASTA_RESULTADOS, nome + "_guloso.txt")
        with open(caminho_saida, 'w') as f:
            f.write(resultado)

        print(f"{nome:<30} {len(rotas):>6} {custo_total:>18.3f} {tempo:>9.4f}s")

    caminho_resumo = os.path.join(PASTA_RESULTADOS, "RESUMO_GULOSO.txt")
    with open(caminho_resumo, 'w') as f:
        f.write("\n".join(resumo_total))

    print("-" * 70)
    print(f"\nResultados salvos em: {PASTA_RESULTADOS}")

if __name__ == "__main__":
    main()