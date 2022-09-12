import math
import random
import time
from matplotlib import pyplot as plt

dificuldade_bases = {
    1: 55,
    2: 60,
    3: 65,
    4: 70,
    5: 75,
    6: 80,
    7: 85,
    8: 90,
    9: 95,
    10: 100,
    11: 110,
    12: 120
}

"""
escolha:
{
    aviao: [bases],
    custo: custo
}
"""


def gera_valores():
    escolhas = {x: list() for x in range(1, 6)}

    for b in range(1, 13):
        escolhas[random.randint(1, 5)].append(b)

    for x in escolhas:
        escolhidos = escolhas[x]
        while len(escolhidos) < 5:
            base = random.randint(1, 12)
            while base in escolhidos:
                base = random.randint(1, 12)
            escolhidos.append(base)

        escolhas[x] = escolhidos

    escolhas['custo'] = calcula_custo(escolhas)

    return escolhas


def calcula_custo(escolhas):
    bases = {x: 0 for x in range(1, 13)}
    for aviao in escolhas:
        if aviao == 'custo':
            continue
        if len(escolhas[aviao]) > 5:
            return 1000

        for base in escolhas[aviao]:
            bases[base] += 1 + aviao/10

    custo = 0
    for base in bases:
        if bases[base] == 0:
            return 1000
        else:
            custo += dificuldade_bases[base]/bases[base]

    return custo


def mutacao(escolhas):
    v = random.randint(1, 5)
    while len(escolhas[v]) == 1:
        v = random.randint(1, 5)
    bases = escolhas[v]
    random.shuffle(bases)
    antiga_base = bases.pop()  # retirei uma base aleatoria
    nova_base = random.randint(1, 12)
    while nova_base in bases or nova_base == antiga_base:
        nova_base = random.randint(1, 12)
    bases.append(nova_base)

    escolhas['custo'] = calcula_custo(escolhas)
    return


def recombinacao(escolhas1, escolhas2):
    tentativas = 0
    while tentativas < 3:
        nova_escolha = {x: None for x in range(1, 6)}

        avioes_de_1 = random.sample(range(1, 6), k=3)
        for v in range(1, 6):
            if v in avioes_de_1:
                nova_escolha[v] = escolhas1[v].copy()
            else:
                nova_escolha[v] = escolhas2[v].copy()

        if verifica_validade(nova_escolha):
            break
        tentativas += 1

    if tentativas == 3:
        nova_escolha = {x: escolhas1[x].copy() for x in range(1, 6)}
        mutacao(nova_escolha)

    nova_escolha['custo'] = calcula_custo(nova_escolha)
    return nova_escolha


def roleta(lista_escolhas):
    dict_com_custo = {x['custo']: x for x in lista_escolhas}
    lista_custos = list(dict_com_custo.keys())
    maior_custo = max(lista_custos)

    lista_custos_invertida = [maior_custo - x for x in lista_custos]

    custo = random.choices(lista_custos, weights=lista_custos_invertida, k=1)[0]
    return dict_com_custo[custo]


def distribuicao_custos(lista_escolhas):
    return [e['custo'] for e in lista_escolhas]


def pega_melhores(populacao, q):
    populacao.sort(key=lambda x: x['custo'])
    return populacao[:q]


def verifica_validade(escolha):
    contagem = {}
    for v in escolha:
        if len(escolha[v]) == 0:
            return False
        for b in escolha[v]:
            contagem[b] = 0

    if len(contagem.keys()) != 12:
        return False
    return True


def algoritmo_genetico(maxima_evolucoes):
    # iniciando a populacao
    max_populacao = 200
    max_elitismo = 20
    max_criacionismo = 10
    populacao = [gera_valores() for _ in range(max_populacao)]
    evolucao_atual = 0
    lista_melhores = []
    lista_medias = []

    while evolucao_atual < maxima_evolucoes:
        elitismo = max_elitismo # - int(max_elitismo * evolucao_atual / maxima_evolucoes)
        criacionismo = int(max_criacionismo * evolucao_atual / maxima_evolucoes)

        nova_populacao = []
        nova_populacao.extend(pega_melhores(populacao, elitismo))  # ELITISMO
        nova_populacao.extend([gera_valores() for _ in range(criacionismo)])  # CRIACIONISMO

        for _ in range(max_populacao - elitismo - criacionismo):
            pai = roleta(populacao)
            mae = roleta(populacao)
            filho = recombinacao(pai, mae)

            probabilidade_mutacao = random.uniform(0, 1)
            # mutacao: 5% - 10% (linearmente)
            if probabilidade_mutacao < 0.05 + 0.10 * evolucao_atual / maxima_evolucoes:
                mutacao(filho)

            nova_populacao.append(filho)

        populacao = nova_populacao
        evolucao_atual += 1
        dist = distribuicao_custos(populacao)
        melhor_custo = min(dist)
        media_custo = sum(dist) / max_populacao
        lista_melhores.append(melhor_custo)
        lista_medias.append(media_custo)
        print("Evolucao %d: %.3f" % (evolucao_atual, melhor_custo))

    lista_custos = distribuicao_custos(populacao)
    melhor_custo = 100000000
    melhor_custo_i = -1
    for i, c in enumerate(lista_custos):
        if c < melhor_custo:
            melhor_custo = c
            melhor_custo_i = i

    melhor_individuo = populacao[melhor_custo_i]
    print("Melhor custo: %.3f" % melhor_custo)
    print("Melhor individuo: ", melhor_individuo)

    return lista_melhores, lista_medias


if __name__ == "__main__":
    a = int(input("Digite a quantidade de evolucoes: "))
    tempo = time.time()
    # algoritmo_genetico(a)

    eixo_y, eixoy_2 = algoritmo_genetico(a)
    eixo_x = range(0, a)
    tempo = time.time() - tempo
    print("Tempo: %.3f (tempo por geracao: %.3f)" % (tempo, tempo / a))

    plt.title("Evolucao do custo")

    plt.xlabel("evolucao")
    plt.ylabel("custo")

    # plt.plot(lista, range(numero), '.b')
    plt.plot(eixo_x, eixo_y, '.b', eixo_x, eixoy_2, '.g')
    plt.show()
