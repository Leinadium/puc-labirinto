"""
Módulo contendo a classe Escolha
Utilizado no algoritmo de evolução genética
"""
import json
import random
import os

# variaveis default, podem ser sobreescritas
PATH_GINASIOS = os.path.join(os.path.dirname(__file__), '..', 'dados', 'ginasios.json')
PATH_POKEMONS = os.path.join(os.path.dirname(__file__), '..', 'dados', 'pokemons.json')
PUNICAO = 150  # multiplicador para valor invalido de cromossomo
MAX_BATALHAS_POKEMON = 5   # maximo de batalhas que um pokemon aguenta

# cria o dicionario de ginasios e pokemons
ginasios = json.load(open(PATH_GINASIOS, 'r'), object_hook=lambda a: {int(x): a[x] for x in a})
pokemons = json.load(open(PATH_POKEMONS, 'r'), object_hook=lambda a: {int(x): a[x] for x in a})


class EscolhaComInvalidez:
    QUANTIDADE_POKEMONS = 5
    QUANTIDADE_GINASIOS = 12

    def __init__(self, vazio=False):
        """
        Cria um objeto escolha, e preenche com escolhas aleatorios
        :param vazio: se for True, os valores serão vazios.
        """
        self.custo = -1
        self.fitness = 0
        self.validade = False
        self.cromossomo = [False] * (self.QUANTIDADE_POKEMONS * self.QUANTIDADE_GINASIOS)

        if vazio:
            return

        self.cromossomo = random.choices(
            population=[True, False],
            k=self.QUANTIDADE_GINASIOS * self.QUANTIDADE_POKEMONS
        )

        self._calcula_custo()
        return

    def __str__(self):
        return '<Escolha> f(%.3f) c(%.3f) v(%s) [%s]' % (
            self.fitness, self.custo, 'SIM' if self.validade else 'NAO',
            ''.join(['1' if x else '0' for x in self.cromossomo]))

    def _calcula_custo(self):
        """
        Calcula os valores de fitness e de custo
        :return:
        """

        lista_bases = [0] * self.QUANTIDADE_GINASIOS
        lista_pokemons = [0] * self.QUANTIDADE_POKEMONS
        quantidade_de_batalhas = 0
        self.validade = True
        quantidade_de_punicoes = 0

        for i, c in enumerate(self.cromossomo):
            if c:
                quantidade_de_batalhas += 1
                lista_pokemons[i % self.QUANTIDADE_POKEMONS] += 1
                lista_bases[i // self.QUANTIDADE_POKEMONS] += pokemons[i % self.QUANTIDADE_POKEMONS + 1]

        # vendo punicao se o pokemon foi muito utilizado
        for pok in lista_pokemons:
            if pok > MAX_BATALHAS_POKEMON:
                self.validade = False
                quantidade_de_punicoes += 1

        # vendo se eu consumi todos os pokemons:
        if self.validade and quantidade_de_batalhas == MAX_BATALHAS_POKEMON * self.QUANTIDADE_POKEMONS:
            self.validade = False
            quantidade_de_punicoes += 1

        # verificando se todos os ginasios foram batalhados
        for i, bas in enumerate(lista_bases):
            if bas == 0:
                self.validade = False
                quantidade_de_punicoes += 1
            else:
                self.custo += ginasios[i + 1] / bas

        # calculando fitness final
        self.fitness = (1000 / (self.custo + PUNICAO * quantidade_de_punicoes)) if self.custo > 0 else 0
        return

    def mutacao(self):
        """
        Gera uma mutacao no cromossomo do individuo
        """
        i = random.randrange(0, len(self.cromossomo))
        self.cromossomo[i] = not self.cromossomo[i]
        self._calcula_custo()
        return

    @classmethod
    def crossover(cls, pai, mae):
        """
        Faz a operação de crossover com o pai e a mãe, e retorna um filho.
        É pego uma fatia do pai e uma fatia da mae.
        :param pai: objeto Escolha
        :param mae: objeto Escolha
        :return: objeto Escolha
        """

        filho = EscolhaComInvalidez(vazio=True)

        i_fatia = random.randint(1, cls.QUANTIDADE_GINASIOS - 1)
        filho.cromossomo = pai.cromossomo[0:i_fatia*cls.QUANTIDADE_POKEMONS]  # copia do pai até i_fatia
        filho.cromossomo.extend(mae.cromossomo[i_fatia*cls.QUANTIDADE_POKEMONS:])  # copia da mae de i_fatia ate o final

        filho._calcula_custo()
        return filho

    @staticmethod
    def roleta(populacao, quantidade):
        """
        Seleciona individuos da população usando o metodo da roleta.
        Os individuos podem se repetir.
        :param populacao: lista de individuos
        :param quantidade: quantidade de individuos para serem pegos
        """
        return random.choices(populacao, weights=[x.fitness**(3/2) for x in populacao], k=quantidade)

    @staticmethod
    def n_melhores(populacao, n):
        """
        Seleciona os n melhores individuos de uma populacao
        :param populacao: lista de individuos
        :param n: quantidade de individuos a serem selecionados
        :return: lista de individuos ou o indivíduo diretamente (n=1)
        """
        if n == 1:
            return max(populacao, key=lambda a: a.fitness)
        return sorted(populacao, key=lambda a: a.fitness, reverse=True)[:n]

    @staticmethod
    def gera_elite(populacao, n):
        """
        Gera individuos da elite.
        Neste caso, seram simplesmente os melhores individuos da populacao
        :param populacao: lista de individuos
        :param n: tamamnho da elite
        :return: lista de individuos
        """
        return EscolhaComInvalidez.n_melhores(populacao, n)

    @staticmethod
    def gera_criacao(n):
        """
        Gera individuos de acordo com o criacionismo.
        Ou seja, n individuos aleatorios
        :param n: tamamnho da criacao
        :return: lista de individuos
        """
        return [EscolhaComInvalidez() for _ in range(n)]


class EscolhaMutacao:
    
    chances_mutacao = {  # pesos de cada tipo de mutação que pode ocorrer
        'trocar': 0,  # ja ocorre no crossover
        'mudar': 10,  # equivale a 66%
        'grave': 5  # equivale a 33%
    }

    QUANTIDADE_GINASIOS = len(ginasios.values())
    QUANTIDADE_POKEMONS = len(pokemons.values())

    @classmethod
    def alterar_propriedades(cls, q_ginasios=-1, q_pokemons=-1):
        """Altera a quantidade de ginásios e pokemons para a Escolha

        Args:
            q_ginasios (int): quantidade de ginasios
            q_pokemons (int): quantidade de pokemons
        """
        if q_ginasios > 0:
            cls.QUANTIDADE_GINASIOS = q_ginasios
        if q_pokemons > 0:
            cls.QUANTIDADE_POKEMONS = q_pokemons
        return
        
    def __init__(self, vazio=False):
        """
        Cria um objeto escolha, e preenche com escolhas aleatorias válidas
        :param vazio: se True, os valores serao vazios
        """
        self.custo = -1
        self.fitness = 0

        # o cromossomo sera um dicionario [ginasio] -> pokemons
        self.cromossomo = {x: list() for x in range(1, self.QUANTIDADE_GINASIOS + 1)}

        # dicionario auxiliar de custo, para recalcular custos mais rapidamente
        self.dict_custo = dict()

        if vazio:
            return

        # preenchendo o cromossomo:
        # cada pokemons atacara 5 vezes, exceto o mais fraco, que sobreviverá
        # por que o melhor pokemon atacará
        possiveis = {pok: 5 for pok in range(1, 1 + self.QUANTIDADE_POKEMONS)}
        possiveis[1] -= 1  

        # preenchendo todos os ginasios:
        for g in self.cromossomo:
            pok = random.choice(list(possiveis.keys()))
            self.cromossomo[g].append(pok)
            possiveis[pok] -= 1
            if possiveis[pok] == 0:
                possiveis.pop(pok)

        # preenchendo usando os pokemons restantes
        while possiveis:
            pok = random.choice(list(possiveis.keys()))
            ginasios_possiveis = [g for g in self.cromossomo if pok not in self.cromossomo[g]]
            g = random.choice(ginasios_possiveis)
            self.cromossomo[g].append(pok)
            possiveis[pok] -= 1
            if possiveis[pok] == 0:
                possiveis.pop(pok)

        self.calcula_custo()
        return

    def __str__(self):
        s = ''
        for lista in self.cromossomo.values():
            s += '%s' % str(lista)

        return '<EscolhaM> f(%.3f) c(%.12f) [%s]' % (self.fitness, self.custo, s)

    def calcula_custo(self, ginasios_para_recalcular=None):
        """
        Calcula os valores de fitness e custo
        :param ginasios_para_recalcular: uma lista de ginasios para recalcular o custo, para
        economizar tempo. Se for None, o custo sera recalculado inteiramente
        :return:
        """
        if ginasios_para_recalcular is None:
            ginasios_para_recalcular = self.cromossomo.keys()  # verifica todos os ginasios

        for g in ginasios_para_recalcular:
            # calcula o custo para cada ginasios e salva no dicionario auxiliar
            self.dict_custo[g] = ginasios[g] / sum(pokemons[x] for x in self.cromossomo[g])

        # calculando o custo
        self.custo = sum(self.dict_custo.values())
        self.fitness = (400 / self.custo) if self.custo != 0 else 0
        return

    def mutacao(self, tipo=''):
        """
        Faz uma mutação no objeto
        Para a mutação sempre ser válida, é preciso que os pokemons continuem atacando,
        e que todos os ginásios estejam sendo atacados.

        Mutacao MUDAR:
        Um pokemon mudará o ginásio que atacará.

        Mutacao GRAVE: em vez de um pokemon mudar um ataque, todos os ataques direcionados a uma base serão
        trocados com uma outra base

        Mutacao TROCAR: troca o ataque de dois pokemons um com o outro.
        """
        if not tipo:
            tipos = list(self.chances_mutacao.keys())
            tipo = random.choices(population = tipos,
                                weights = [self.chances_mutacao[x] for x in tipos],
                                k=1)[0]

        if tipo == 'grave':
            gs = list(self.cromossomo.keys())
            random.shuffle(gs)
            g1, g2 = gs[:2]
            temp = self.cromossomo[g1]
            self.cromossomo[g1] = self.cromossomo[g2]
            self.cromossomo[g2] = temp

            self.calcula_custo([g1, g2])
            return
        
        if tipo == 'trocar':
            # escolhendo um ginasio que é possivel tirar um ataque
            # ginasios_possiveis = [g for g in self.cromossomo if len(self.cromossomo[g]) > 1]
            while True:
                g1, g2 = 1, 1
                while g1 == g2:
                    g1, g2 = random.choices(list(self.cromossomo), k=2)  # dois ginasios aleatorios diferentes
                
                l1, l2 = self.cromossomo[g1], self.cromossomo[g2]
                random.shuffle(l1)
                random.shuffle(l2)
                for a in l1:
                    if a not in l2:
                        for b in l2:
                            if b not in l1:
                                # faz a troca
                                l1.remove(a)
                                l1.append(b)
                                l2.remove(b)
                                l2.append(a)
                                self.calcula_custo([g1, g2])
                                return
            

        if tipo == 'mudar':   
            # escolhendo um ginasio que é possivel tirar um ataque
            ginasios_possiveis = [g for g in self.cromossomo if len(self.cromossomo[g]) > 1]
            g1 = random.choice(list(ginasios_possiveis))

            # embaralhando e tirando um pokemon aleatoriamente
            random.shuffle(self.cromossomo[g1])
            pok = self.cromossomo[g1].pop()

            # pegando um ginasios possivel (em que o ginasio nao contenha aquele pok)
            ginasios_possiveis = [g for g in self.cromossomo if pok not in self.cromossomo[g]]
            g2 = random.choice(list(ginasios_possiveis))

            # colocando o pok no ginasio
            self.cromossomo[g2].append(pok)

            # recalculando o custo somente para aquele ginasios
            self.calcula_custo([g1, g2])
            return

    @staticmethod
    def crossover(pai):
        """
        Este não é o crossover comum. Esta funcao realiza a duplicação do pai, com uma mutação.

        :param pai: objeto EscolhaMutacao
        :return: novo objeto EscolhaMutacao
        """
        # criando o filho copia do pai
        filho = EscolhaMutacao(vazio=True)
        filho.cromossomo = {g: poks.copy() for g, poks in pai.cromossomo.items()}
        filho.dict_custo = pai.dict_custo.copy()
        filho.calcula_custo()
        # gerando a mutacao do filho
        filho.mutacao(tipo='trocar')

        return filho
    
    @classmethod
    def true_crossover(cls, pai, mae):
        """
        ABANDONADO! MUITO COMPLEXO E DEMORADO.

        Faz um crossover com o pai e mãe, e retorna um filho.
        O crossover funciona da seguinte forma:

        * Inverte-se o pai e mãe (pok -> gin)
        * Se o mesmo pok do pai e da mãe atacam um ginásio, o pok do filho atacará também

        * Veja quais ginasios o pok ataca (tanto pelo pai quanto pela mãe)
        * Para cada ginasio que o filho ainda não ataca, escolhe um pokemon que ou o pai ou a mãe ataca.

        * Depois, para cada pokemon, escolhe um ginasio que o pai ou a mãe ataca, até que o filho ataque a mesma 
          quantidade que o pai atacava.

        * Inverte-se o filho para obter uma escolha válida
        """

        # invertendo o pai e a mãe
        pok_pai = {x: dict() for x in range(1, 1 + cls.QUANTIDADE_POKEMONS)}
        pok_mae = {x: dict() for x in range(1, 1 + cls.QUANTIDADE_POKEMONS)}
        pok_geral = {x: dict() for x in range(1, 1 + cls.QUANTIDADE_POKEMONS)}
        pok_filho = {x: list() for x in range(1, 1 + cls.QUANTIDADE_POKEMONS)}
        ginasios_atacados = {x: 1 for x in range(1, cls.QUANTIDADE_GINASIOS + 1)}
        for g in pai.cromossomo:
            for pok in pai.cromossomo[g]:
                pok_pai[pok][g] = 1
                pok_geral[pok][g] = 1

            for pok in mae.cromossomo[g]:
                pok_mae[pok][g] = 1
                if g in pok_geral[pok]:  # ambos os poks atacam o mesmo ginasio, coloca no filho
                    pok_filho[pok].append(g)
                    pok_geral[pok].pop(g)  # tira do geral, ja foi escolhido
                    if g in ginasios_atacados:
                        ginasios_atacados.pop(g)
                else:
                    pok_geral[pok][g] = 1
        
        for g in ginasios_atacados:  # andando para cada ginasio ainda nao atacado
            pok_escolhido = None
            for pok in pok_geral:
                # verificando se o pokemon nao atacou aquele gin, ou se o pokemon já nao esta exausto
                if g in pok_geral[pok] and len(pok_filho[pok]) < len(pok_pai[pok]):
                    # ordenando por pokemon menos esgotado, para sempre haver um pokemon que pode atacar
                    if pok_escolhido is None or len(pok_filho[pok]) < len(pok_filho[pok_escolhido]):
                        pok_escolhido = pok
            
            if pok_escolhido is None:
                print(pok_filho, pok_geral, pok_mae, pok_pai, ginasios_atacados)

            pok_filho[pok_escolhido].append(g)
            pok_geral[pok_escolhido].pop(g)
        
        # agora todas as regras estão garantidas
        # preenchendo os poks com ginasios do pai ou da mãe, até que que o pok 4 ou 5 ataques
        for pok in pok_geral:
            tamanho = len(pok_pai[pok]) - len(pok_filho[pok])
            while tamanho > 0:
                g_escolhido = random.choice(list(pok_geral[pok]))
                pok_filho[pok].append(g_escolhido)
                pok_geral[pok].pop(g_escolhido)
                tamanho -= 1
        # invertendo o filho
        for pok in pok_filho:
            if len(pok_filho[pok]) > 5:
                raise Exception("oh no")

        filho = EscolhaMutacao(vazio=True)
        for pok in pok_filho:
            for g in pok_filho[pok]:
                filho.cromossomo[g].append(pok)
        filho.calcula_custo()
        return filho

    @staticmethod
    def roleta(populacao, quantidade):
        """
        Seleciona individuos da população usando o metodo da roleta.
        Os individuos podem se repetir.
        :param populacao: lista de individuos
        :param quantidade: quantidade de individuos para serem pegos
        """
        return random.choices(populacao, weights=[x.fitness ** (3/2) for x in populacao], k=quantidade)

    @staticmethod
    def n_melhores(populacao, n):
        """
        Seleciona os n melhores individuos de uma populacao
        :param populacao: lista de individuos
        :param n: quantidade de individuos a serem selecionados
        :return: lista de individuos ou o indivíduo diretamente (n=1)
        """
        if n == 1:
            return max(populacao, key=lambda a: a.fitness)
        return sorted(populacao, key=lambda a: a.fitness, reverse=True)[:n]

    @staticmethod
    def gera_elite(populacao, n):
        """
        Gera individuos da elite.
        Neste caso, seram simplesmente os melhores individuos da populacao
        :param populacao: lista de individuos
        :param n: tamamnho da elite
        :return: lista de individuos
        """
        return EscolhaMutacao.n_melhores(populacao, n)

    @staticmethod
    def gera_criacao(n):
        """
        Gera individuos de acordo com o criacionismo.
        Ou seja, n individuos aleatorios
        :param n: tamamnho da criacao
        :return: lista de individuos
        """
        return [EscolhaMutacao() for _ in range(n)]
