import random
import math
# from matplotlib import pyplot as plt
import time

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


def gera_valores():
    possiveis = {a: 5 for a in range(1, 6)}
    possiveis[1] -= 1
    ret = [list() for i in range(12)]

    for i in range(12):
        p = random.choice(list(possiveis.keys()))
        ret[i].append(p)
        possiveis[p] -= 1
        if possiveis[p] == 0:
            possiveis.pop(p)

    while possiveis:
        while True:
            v = random.randint(0, 11)
            if len(ret[v]) < 5:
                p = random.choice(list(possiveis.keys()))
                if p not in ret[v]:
                    break

        ret[v].append(p)
        possiveis[p] -= 1
        if possiveis[p] == 0:
            possiveis.pop(p)

    return ret


def calcula_custo(escolhas):
    custo = 0
    for i, avioes in enumerate(escolhas, 1):
        base_formula = 0
        for aviao in avioes:
            base_formula += 1 + int(aviao)/10
        custo += dificuldade_bases[i]/base_formula
    return custo


def gera_vizinho(escolhas_atuais):
    escolhas = [xx.copy() for xx in escolhas_atuais]

    base = random.randint(0, 11)
    while len(escolhas[base]) == 1:
        base = random.randint(0, 11)

    v = escolhas[base].pop(random.randint(0, len(escolhas[base]) - 1))
    while True:
        nova_base = random.randint(0, 11)
        if nova_base != base and v not in escolhas[nova_base]:
            escolhas[nova_base].append(v)
            break

    return escolhas


def simulated_annealing(temperatura, esfriamento):
    escolha = gera_valores()
    custo = calcula_custo(escolha)

    melhor, melhor_custo = escolha, custo
    tentativas = 0
    while tentativas <= 1000:
        # print("T: %0.5f | C: %0.2f" % (temperatura, custo))
        nova_escolha = gera_vizinho(escolha)
        novo_custo = calcula_custo(nova_escolha)

        diferenca = novo_custo - custo
        prob = math.exp(-abs(diferenca)/temperatura)
        rnd = random.uniform(0, 1)

        if diferenca < 0 or rnd < prob:
            escolha = nova_escolha
            custo = novo_custo
            if custo < melhor_custo:
                melhor = escolha
                melhor_custo = custo

        temperatura *= esfriamento

        tentativas += 1

    # print("Executado %d vezes" % tentativas)
    # print("Escolha: ", escolha)
    # print("Custo: ", custo)
    return melhor, melhor_custo


if __name__ == "__main__":
    # print(simulated_annealing(300, 0.9999))

    
    lista = []
    lista_respostas = []
    numero = int(input("Numero de vezes: "))
    tempo = time.time()
    for i in range(numero):
        e, x = simulated_annealing(30, 0.999)
        print("Executando %d: %0.2f" % (i, x))
        lista.append(x)
        lista_respostas.append(e)

    print("Tempo estimado por execucao: %.5fs" % ((time.time() - tempo)/numero))
    print("Melhor custo: ", min(lista))
    print("Melhor escolha: ", lista_respostas[lista.index(min(lista))])
    '''
    plt.title("Tentativas")
    # plt.xlabel("numero da tentativa")
    # plt.ylabel("custo")
    # plt.plot(range(numero), lista, '.b')

    plt.xlabel("custo")
    plt.ylabel("numero tentativa")

    # plt.plot(lista, range(numero), '.b')
    plt.plot(lista, range(numero), '.b')
    plt.show()
    '''