"""
Módulo contendo a classe Escolha para simulated annealing
"""

import random
import json
import os

# variaveis default, podem ser sobreescritas
PATH_GINASIOS = os.path.join(os.path.dirname(__file__), '..', 'dados', 'ginasios.json')
PATH_POKEMONS = os.path.join(os.path.dirname(__file__), '..', 'dados', 'pokemons.json')

# cria o dicionario de ginasios e pokemons
ginasios = json.load(open(PATH_GINASIOS, 'r'), object_hook=lambda a: {int(x): a[x] for x in a})
pokemons = json.load(open(PATH_POKEMONS, 'r'), object_hook=lambda a: {int(x): a[x] for x in a})

QUANTIDADE_GINASIOS = len(ginasios.values())
QUANTIDADE_POKEMONS = len(pokemons.values())


class Escolha:
    """classe Escolha
    
    objeto.custo -> contem o custo atual da escolha
    objeto.randvizinho() -> gera um vizinho aleatório

    """


    def __str__(self):
        return '%0.3f: %s' % (self.custo, str(self.cromossomo.values()))

    def __init__(self, vazio=False):
        """Cria um objeto da classe escolha

        Se vazio for True, não sera preenchido.
        """
        self.custo = 0
        self.cromossomo = {g: list() for g in range(1, 1 + QUANTIDADE_GINASIOS)}
        self.dict_custos = {g: 0 for g in range(1, 1 + QUANTIDADE_GINASIOS)}
        # ginasio -> pokemon
        if not vazio:
            self._preencher()
            self._calcular_custo()
        return

    
    def _preencher(self):
        possiveis = {1: 4, 2: 5, 3: 5, 4: 5, 5: 5}
        for g in range(1, 1 + QUANTIDADE_GINASIOS):
            pok = random.choice(list(possiveis))
            self.cromossomo[g].append(pok)
            possiveis[pok] -= 1
            if possiveis[pok] == 1:
                possiveis.pop(pok)
        
        while possiveis:
            pok = random.choice(list(possiveis))
            ps = [g for g in self.cromossomo if pok not in self.cromossomo[g]]
            g = random.choice(list(ps))
            self.cromossomo[g].append(pok)
            possiveis[pok] -= 1
            if possiveis[pok] == 1:
                possiveis.pop(pok)
        return
    
    def _calcular_custo(self, gs=None):
        gs = gs if gs is not None else self.cromossomo
        for g in gs:
            base = sum([pokemons[p] for p in self.cromossomo[g]])
            self.dict_custos[g] = ginasios[g] / base
        self.custo = sum([x for x in self.dict_custos.values()])
        return
    
    def randvizinho(self):
        """Retorna um vizinho aleatorio da escolha atual
        """
        # fazendo a copia
        vizinho = Escolha(vazio=True)
        vizinho.custo = self.custo
        vizinho.dict_custos = self.dict_custos.copy()
        vizinho.cromossomo = {x: self.cromossomo[x].copy() for x in self.cromossomo}  # deepcopy

        while True:
            g1, g2 = random.choices(list(vizinho.cromossomo), k=2)
            a = random.choice(vizinho.cromossomo[g1])
            b = random.choice(vizinho.cromossomo[g2])
            if a not in vizinho.cromossomo[g2] and b not in vizinho.cromossomo[g1]:
                vizinho.cromossomo[g1].remove(a)
                vizinho.cromossomo[g2].remove(b)
                vizinho.cromossomo[g1].append(b)
                vizinho.cromossomo[g2].append(a)
                break
        
        vizinho._calcular_custo(gs=[g1, g2])
        return vizinho
