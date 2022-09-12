import random
import time
import json

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


class Escolha:
    """
    Classe que define as escolhas de qual avião ataca qual base
    """
    bases = {x: list() for x in range(1, 13)}
    custo_dict = {x: 0 for x in range(1, 13)}
    custo = 0

    def __init__(self, copia=None, vazio=False):
        """Inicia um objeto.
        :param copia: Um objeto Escolha para copiar
        :param vazio: Se True, retorna um objeto sem preenchimento
        """
        self.bases = {x: list() for x in range(1, 13)}
        self.custo_dict = {x: 0 for x in range(1, 13)}
        self.custo = 0

        if vazio:
            return

        if copia is not None:
            for b in copia.bases:
                self.bases[b] = copia.bases[b].copy()
                self.custo_dict[b] = copia.custo_dict[b]
            self.custo = copia.custo

        else:
            self._gerar()

    def __str__(self):
        return ''.join([str(x) for x in self.bases.values()]) + str(self.custo)

    def _gerar(self):
        possiveis = {x: 5 for x in range(1, 6)}

        for i in range(1, 13):  # preenchendo cada base pelo menos com um aviao
            p = random.choice(list(possiveis.keys()))
            self.bases[i].append(p)
            possiveis[p] -= 1
            if possiveis[p] == 0:
                possiveis.pop(p)

        while possiveis:
            p = random.choice(list(possiveis.keys()))
            b = random.randint(1, 12)
            while p in self.bases[b]:
                b = random.randint(1, 12)

            self.bases[b].append(p)
            possiveis[p] -= 1
            if possiveis[p] == 0:
                possiveis.pop(p)

        self.calcula_custo()
        return

    def calcula_custo(self, bases_mudadas=None):
        bases_a_verificar = bases_mudadas if bases_mudadas is not None else self.bases.keys()
        for b in bases_a_verificar:
            avioes = self.bases[b]
            dano_ataque = sum([1 + v/10 for v in avioes])
            dificuldade = dificuldade_bases[b]
            self.custo_dict[b] = dificuldade / dano_ataque
        self.custo = sum(self.custo_dict.values())
        return

    def fazer_mutacao(self, prob_grave=0.1):
        """
        Faz a mutação dessa Escolha.
        Todas as mutações são sempre válidas.
        Mutação leve (1 - prob_grave %): coloca um avião de uma base em outra base
        Mutação grave (prob_grave %): troca bases de lugar
        :return: none
        """
        if random.uniform(0, 1) <= 1 - prob_grave:
            # tirando um aviao de uma base e colocando na outra
            bases_para_tirar = [x for x in self.bases if len(self.bases[x]) > 1]
            b = random.choice(bases_para_tirar)
            random.shuffle(self.bases[b])
            v = self.bases[b].pop()

            bases_para_colocar = [x for x in self.bases if v not in self.bases[x]]
            bb = random.choice(bases_para_colocar)
            self.bases[bb].append(v)

            self.calcula_custo(bases_mudadas=[b, bb])

        else:
            bases_pra_trocar = [0, 0]
            while bases_pra_trocar[0] == bases_pra_trocar[1]:
                bases_pra_trocar = random.choices(list(self.bases.keys()), k=2)

            b, bb = bases_pra_trocar
            # troca as bases
            temp = self.bases[b]
            self.bases[b] = self.bases[bb]
            self.bases[bb] = temp
            # troca os custos
            temp = self.custo_dict[b]
            self.custo_dict[b] = self.custo_dict[bb]
            self.custo_dict[bb] = temp

            self.calcula_custo(bases_mudadas=[b, bb])

        return


def crossover(pai, mae):
    """
    Crossover ataque por ataque.
    Se ambos atacarem a base com aquele aviao, o filho também atacara
    Se somente um deles atacar, o filho pode atacar ou não (50%)
    Se nenhum deles atacar, o filho não atacará

    Se no final o filho for inválido, o crossover será repetido, até 3 vezes.
    Depois disso, o filho será uma mutação do pai.
    """
    tentativas = 0
    while tentativas < 3:
        filho = Escolha(vazio=True)
        for b in range(1, 13):
            base1 = pai.bases[b]
            base2 = mae.bases[b]
            for v in range(1, 6):
                tem_base1 = 1 if v in base1 else 0
                tem_base2 = 1 if v in base2 else 0
                rnd = random.uniform(0, 1)
                prob = (tem_base2 + tem_base1) / 2
                if rnd <= prob:
                    filho.bases[b].append(v)
        # verificando se o filho ficou vivo
        contagem = [0, 0, 0, 0, 0]
        continuar = True
        for b in filho.bases.values():
            if len(b) == 0:
                continuar = False
                break
            for v in b:
                contagem[v-1] += 1

        if not continuar or contagem.count(5) != 5:
            tentativas += 1
            continue

        filho.calcula_custo()
        return filho

    # se nao conseguiu, copia o pai e faz uma mutacao
    filho = Escolha(copia=pai)
    filho.fazer_mutacao()
    return filho


def pega_melhor(lista):
    """Retorna a melhor escolha"""
    melhor_custo = 10000
    melhor_e = None
    for e in lista:
        if e.custo < melhor_custo:
            melhor_e = e
            melhor_custo = e.custo
    return melhor_e


def roleta(lista, quantidade):
    """
    Roleta de seleção de Escolhas para o crossover.
    :param lista: lista de escolhas
    :param quantidade: quantos elementos para selecionar
    :return: a escolha para crossover
    """

    menor_custo = pega_melhor(lista).custo

    # como queremos dar prioridade ao menor custo
    # podemos obter o peso fazendo maior_custo - valor

    lista_pesos_invertida = [menor_custo * menor_custo / e.custo for e in lista]

    return random.choices(lista, weights=lista_pesos_invertida, k=quantidade)


def pega_melhores(lista, n):
    """Pega os n escolhas com melhor custo da lista"""
    return sorted(lista, key=lambda a: a.custo)[:n]


def algoritmo_genetico(n):
    """
    Roda o algoritmo genetico para n evoluções
    :param n: numero de evoluoes a serem rodadas
    :return: melhor custo, melhor escolha
    """

    # modo = 'crossover'  # tem crossover e mutacao
    modo = 'mutacao'  # so mutacao

    max_populacao = 100
    max_elitismo = 0.2 * max_populacao
    max_criacionismo = 0.1 * max_populacao

    populacao = [Escolha() for _ in range(max_populacao)]
    lista_populacoes = [[e.custo for e in populacao]]   # para plot

    for geracao in range(n):
        elitismo = int(max_elitismo * (1 - 0.50 * geracao / n))  # 100% -> 50%
        # elitismo = int(max_elitismo)

        # criacionismo = int(max_criacionismo * geracao / n)  # 0 -> 100%
        criacionismo = int(max_criacionismo)

        probabilidade_mutacao = 0.00 + 0.04 * geracao / n
        probabilidade_mutacao_grave = 0.10 + 0.10 * geracao / n

        nova_populacao = []
        nova_populacao.extend(pega_melhores(populacao, elitismo))
        nova_populacao.extend(Escolha() for _ in range(criacionismo))

        if modo == 'crossover':
            lista_roleta = roleta(populacao, 2 * (max_populacao - elitismo - criacionismo))
            for i in range(max_populacao - elitismo - criacionismo):
                pai = lista_roleta[2*i]
                mae = lista_roleta[2*1 + 1]
                filho = crossover(pai, mae)
                if random.uniform(0, 1) <= probabilidade_mutacao:
                    filho.fazer_mutacao(probabilidade_mutacao_grave)
                nova_populacao.append(filho)

        else:   # modo mutacao
            lista_roleta = roleta(populacao, max_populacao - elitismo - criacionismo)
            for pai in lista_roleta:
                filho = Escolha(copia=pai)
                filho.fazer_mutacao(probabilidade_mutacao_grave)
                nova_populacao.append(filho)

        populacao = nova_populacao
        lista_populacoes.append([e.custo for e in populacao])  # para plot
        melhor_escolha = pega_melhor(populacao)
        melhor_custo = melhor_escolha.custo
        print("G: %d|E: %d|C: %d|Cost: %.3f" % (geracao, elitismo, criacionismo, melhor_custo))

    melhor_escolha = pega_melhor(populacao)
    print("Melhor escolha (%.3f): %s" % (melhor_escolha.custo, melhor_escolha))

    return lista_populacoes


if __name__ == "__main__":
    a = int(input("Digite o máximo de gerações: "))
    tempo = time.time()
    algoritmo_genetico(a)
    tempo = time.time() - tempo
    print("Tempo de execução: %.3fs (tempo por geracao: %.3fs)" % (tempo, tempo / a))
