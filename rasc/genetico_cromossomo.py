import random

dificuldade_ginasios = {
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
    cromossomo = [False] * 60
    fitness = 0
    custo = 0

    def __str__(self):
        return ''.join(list(['1' if x else '0' for x in self.cromossomo]))

    def __init__(self, arg=None):
        """
        Inicia uma Escolha
        caso arg seja 'gerar', sera iniciado do zero
        caso arg seja um objeto Escolha, sera copiado
        """
        if arg == 'gerar':
            possiveis = {0: 4, 1: 5, 2: 5, 3: 5, 4: 5}

            # preenchimento basico
            for i in range(12):
                pok = random.choice(list(possiveis.keys()))
                self.cromossomo[i * 5 + pok] = True
                possiveis[pok] -= 1
                if possiveis[pok] == 0:
                    possiveis.pop(pok)

            # preenchimento do restante
            for i in range(random.randint(0, 12)):
                pos = random.randrange(0, 12)
                pok = random.choice(list(possiveis.keys()))
                self.cromossomo[pos * 5 + pok] = True
                possiveis[pok] -= 1
                if possiveis[pok] == 0:
                    possiveis.pop(pok)

        elif type(arg) == Escolha:
            self.cromossomo = arg.cromossomo.copy()
            self.fitness = arg.fitness

        elif arg == 'vazio':
            return

        if self.fitness == 0:
            self.atualizar_fitness()

        return

    def atualizar_fitness(self):
        """
        Calcula fitness em base das seguinte equacao:
            custo + (100 * pokemon_morto) + (100 * ginazio_vazio)
        Salva fitness em self.fitness, não retorna valor
        :return: none
        """

        dict_ginasio = {x: 0 for x in range(12)}
        lista_pokemon = [0, 0, 0, 0, 0]
        fit = 0

        # preenchendo valores
        for i, gen in enumerate(self.cromossomo):
            gin, pok = i // 5, i % 5
            if gen:
                dict_ginasio[gin] += 1 + (pok + 1)/10
                lista_pokemon[pok] += 1

        # verificando validade ginasios e calculando custo
        for gin in dict_ginasio:
            if dict_ginasio[gin] == 0:
                fit -= 1000
            else:
                x = dificuldade_ginasios[gin+1] / dict_ginasio[gin]
                # fit += x
                self.custo += x

        # verificando validade pokemons mortos
        vida_perdida = 0
        for p in lista_pokemon:
            if p > 5:
                fit -= 200 * (p - 5)
            vida_perdida += p
        if vida_perdida > 24:
            fit -= 100 * (vida_perdida - 24)

        self.fitness = fit + 1000 - self.custo
        return

    def mutacao(self):
        """
        Cria uma mutacao em um dos cromossomos
        :return: none
        """
        i = random.randrange(0, 60)
        self.cromossomo[i] = not self.cromossomo[i]
        self.atualizar_fitness()
        return


def crossover(pai, mae):
    """
    Gera um filho resultado de um crossover do pai com a mae
    :param pai: objeto Escolha
    :param mae: objeto Escolha
    :return:
    """
    filho = Escolha(arg='vazio')
    filho.cromossomo = [pai.cromossomo[i] if random.uniform(0, 1) >= 0.5
                        else mae.cromossomo[i] for i in range(60)]
    filho.atualizar_fitness()
    return filho


def roleta(lista, q):
    return random.choices(lista, [e.custo for e in lista], k=q)


def evolucao(n):
    tamanho_populacao = 100
    limite_elitismo = n * 0.2
    limite_criacionismo = n * 0.2
    populacao = [Escolha('gerar') for _ in range(tamanho_populacao)]
    populacao.sort(key=lambda a: a.fitness, reverse=True)

    for geracao in range(n):
        elitismo = int(limite_elitismo)
        criacionismo = int(limite_criacionismo)

        nova_populacao = populacao[0:elitismo]
        nova_populacao.extend([Escolha('gerar') for _ in range(criacionismo)])

        for _ in range(tamanho_populacao - elitismo - criacionismo):
            pai, mae = roleta(populacao, q=2)
            filho = crossover(pai, mae)

            if random.uniform(0, 1) < 0.15:
                filho.mutacao()
            nova_populacao.append(filho)

        nova_populacao.sort(key=lambda a: a.fitness, reverse=True)
        melhor_individuo = nova_populacao[0]

        print('Generation [%d]: %.3f %s' % (geracao, melhor_individuo.fitness, melhor_individuo))

    print(melhor_individuo)
    print(melhor_individuo.custo)
    print(melhor_individuo.fitness)
    return


if __name__ == '__main__':
    evolucao(200)
