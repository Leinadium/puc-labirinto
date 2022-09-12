from escolha import Escolha
from math import exp
from random import uniform

def simulated_annealing(passos):
    temperatura = 1000

    melhor = Escolha()
    atual = melhor

    for i in range(passos):
        candidato = atual.randvizinho()

        if candidato.custo < atual.custo:
            melhor = candidato
            # print("%d: %0.3f" % (i, melhor.custo))
        
        diff = candidato.custo - atual.custo
        t = temperatura / float(i + 1)
        chance_metropolis = exp(-diff / t)
        if diff < 0 or uniform(0, 1) < chance_metropolis:
            atual = candidato
    
    print(melhor)
    return melhor


simulated_annealing(1000)
