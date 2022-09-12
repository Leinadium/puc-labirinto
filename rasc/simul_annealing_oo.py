import random
import math
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


def pegar_aviao(d):
    v = random.choice(list(d.keys()))
    d[v] -= 1
    if d[v] == 0:
        d.pop(v)
    return v


class Ataque:
    avioes = list()
    q = 0

    def __len__(self):
        return self.q

    def copy(self):
        a = Ataque()
        a.avioes = self.avioes.copy()
        return a

    def __iter__(self):
        return iter(self.avioes)

    def possui_aviao(self, v):
        return v in self.avioes

    def tirar_aviao(self):
        if self.q == 0:
            return
        random.shuffle(self.avioes)
        self.q -= 1
        return self.avioes.pop()

    def adicionar_aviao(self, v):
        self.q += 1
        self.avioes.append(v)
        return


class Escolha:
    ataques = [Ataque() for i in range(12)]

    def gerar_escolha(self):
        d = {x: 5 for x in range(1, 6)}
        for i in range(12):
            aviao = pegar_aviao(d)
            self.ataques[i].adicionar_aviao(aviao)

        while d:
            aviao = pegar_aviao(d)
            i = random.randint(0, 11)
            while self.ataques[i].possui_aviao(aviao):
                i = random.randint(0, 11)
            self.ataques[i].adicionar_aviao(aviao)
        return

    def gerar_copia(self):
        e = Escolha()
        e.ataques = [x.copy() for x in self.ataques]
        return e

    def gerar_vizinho(self):
        e = self.gerar_copia()
        a = random.randint(0, 11)
        v = e.ataques[a].tirar_aviao()
        possiveis = [i for i in range(0, 11) if i != a and not e.ataques[i].possui_aviao(v)]
        random.shuffle(possiveis)
        e.ataques[possiveis.pop()].adicionar_aviao(v)
        return e

    def custo(self):
        custo = 0
        for i, ataque in enumerate(self.ataques, 1):
            dificuldade = dificuldade_bases[i]
            pontos_base = 0
            for v in ataque:
                pontos_base += 1 + int(v)/10
            custo += dificuldade/pontos_base
        return custo


def simulated_annealing(temperatura, esfriamento):
    escolha = Escolha()
    escolha.gerar_escolha()

    custo = escolha.custo()
    tentativas = 0
    while temperatura >= 0.3:
        print("T: %0.5f | C: %0.2f" % (temperatura, custo))
        nova_escolha = escolha.gerar_vizinho()
        novo_custo = nova_escolha.custo()

        diferenca = novo_custo - custo
        prob = math.exp(-abs(diferenca)/temperatura)
        rnd = random.uniform(0, 1)

        if diferenca < 0 or rnd < prob:
            escolha = nova_escolha
            custo = novo_custo
        temperatura *= esfriamento
        tentativas += 1

    # print("Executado %d vezes" % tentativas)
    # print("Escolha: ", escolha)
    # print("Custo: ", custo)
    return custo


if __name__ == '__main__':
    t = time.time()
    print(simulated_annealing(1000, 0.9))
    print(time.time() - t)
