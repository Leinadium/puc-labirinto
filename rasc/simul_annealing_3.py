import random
import os
import json
import math

PATH_GINASIOS = os.path.join(os.path.dirname(__file__), '..', 'dados', 'ginasios.json')
PATH_POKEMONS = os.path.join(os.path.dirname(__file__), '..', 'dados', 'pokemons.json')

ginasios = json.load(open(PATH_GINASIOS, 'r'), object_hook=lambda a: {int(x): a[x] for x in a})
pokemons = json.load(open(PATH_POKEMONS, 'r'), object_hook=lambda a: {int(x): a[x] for x in a})

def gera_escolha():
    escolha = {x: list() for x in range(1, 1 + 5)}  # pok -> g

    possiveis = {1: 4, 2: 5, 3: 5, 4: 5, 5: 5}
    for g in range(1, 1 + 12):
        pok = random.choice(list(possiveis))
        escolha[pok].append(g)
        possiveis[pok] -= 1
        if possiveis[pok] == 0:
            possiveis.pop(pok)
    while possiveis:
        g = random.randint(1, 12)
        pok = random.choice(list(possiveis))
        escolha[pok].append(g)
        possiveis[pok] -= 1
        if possiveis[pok] == 0:
            possiveis.pop(pok)
    return escolha

def calcula_custo(escolha):
    gin = {x: 0 for x in range(1, 1 + 12)}
    for pok in escolha:
        for g in escolha[pok]:
            gin[g] += pokemons[pok]
    
    return sum([ginasios[g] / gin[g] for g in gin])

def gera_vizinho(escolha):
    vizinho = {x: escolha[x].copy() for x in escolha}

    while True:
        p1, p2 = random.choices(list(vizinho), k=2)
        while p1 == p2:
            p1, p2 = random.choices(list(vizinho), k=2)
        
        g1, g2 = vizinho[p1], vizinho[p2]
        possiveis1 = [g for g in g1 if g not in g2]
        possiveis2 = [g for g in g2 if g not in g1]
        if not possiveis2 or not possiveis1:
            continue
        r1 = random.choice(possiveis1)
        r2 = random.choice(possiveis2)
        
        g1.remove(r1)
        g2.remove(r2)
        g1.append(r2)
        g2.append(r1)
        return vizinho


def gera_vizinho2(escolhas_atuais):
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


def simulated_annealing(maxi):
    temperatura = 30
    atual = gera_escolha()
    custo_atual = calcula_custo(atual)
    melhor, custo_melhor = atual, custo_atual

    for i in range(maxi):
        if random.uniform(0, 1) <= 0.5:
            vizinho = gera_vizinho(atual)
        else:
            vizinho = gera_vizinho2(atual)
        custo_vizinho = calcula_custo(vizinho)

        diff = custo_vizinho - custo_atual
        t = math.exp(-abs(diff) / temperatura)
        rnd = random.uniform(0, 1)

        if diff < 0 or rnd < t:
            atual = vizinho
            custo_atual = custo_vizinho
            print("%d: %0.3f" % (i, custo_atual))

            if custo_atual < custo_melhor:
                melhor, custo_melhor = atual, custo_atual
         
        temperatura *= 0.99

    print(melhor, custo_melhor)
    return melhor, custo_melhor


if __name__ == "__main__":
    simulated_annealing(10000)
