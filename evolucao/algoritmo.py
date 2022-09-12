"""
Módulo do algoritmo de evolução genética.

O algoritmo depende de uma classe que contenha as seguintes propriedades:
Classe(vazio=True)              iniciar um objeto vazio
Classe()                        iniciar um objeto aletoriamente

Classe.crossover(obj1, obj2)    fazer o crossover
Classe.roleta(popul, qtd)       faz a roleta
Classe.n_melhores(popul, n)     retorna os n melhores
Classe.gera_elite(popul, n)
Classe.gera_criacao(n)          retorna n novos individuos

objeto.mutacao()                fazer a mutacao do objeto
objeto.fitness                  propriedade contendo o fitness
objeto.custo                    propriedade contendo o custo
"""

import random
import time
from escolha import EscolhaComInvalidez as EI
from escolha import EscolhaMutacao as EM

"""
O algoritmo genetico com crossover funciona da seguinte maneira:

Primeiro, é gerada uma populacao aleatoriamente. Cada individuo eh gerado usando Escolha()
Depois, para cada geração, é feito as seguintes operações:
    Determina quantos indivíduos serão preservados, a elite.
    Determina quantos indivíduos novos serão gerados, a criação
    Determina qual a chance de um indivíduo sofrer mutação

    Cada uma das quantidades acima varia linearmente, ou seja, conforme as gerações vão passando,
    a quantidade vai variando linearmente
    (pode ser mudado)
 
    Depois disso, é selecionado os indivíduos para reprodução através da roleta.
    A roleta não é nada mais que uma seleção aleatória da população, sendo que indíviduos melhores tem mais chance
    de serem escolhidos.
    A função de roleta já seleciona uma quantidade de indivíduos suficiente para fazer todas as reproduções
    
    Depois disso, é feita a reprodução. São selecionados um pai e uma mãe da roleta, e faz-se o crossover
    Após o crossover, é feita a mutação de acordo com a chance de mutação.
    
    Depois disso, o novo indivíduo é acrescentado na nova população
    Depois de ser gerada toda a nova população, ela sobreescreve a população antiga, e é exibido o melhor indivíduo
"""
def algoritmo_genetico_crossover(max_evolucoes):
    """
    Roda o algoritmo genetico para uma populacao aleatoria.
    :param max_evolucoes: maximo de evolucoes da populacao
    :return: a populacao final
    """

    tamanho = 100
    max_elite = tamanho * 0.2  # 20% da populacao
    max_criacao = tamanho * 0.15   # 15% da populacao
    max_mutacao = 0.1  # 10% de chance de se mutar
    populacao = [EI() for _ in range(tamanho)]

    for geracao in range(max_evolucoes):
        porcentagem_geracao_ocorrida = geracao / max_evolucoes
        q_elite = int(max_elite * (1 - 0.5 * porcentagem_geracao_ocorrida))  # 100% -> 50%
        q_criacao = int(max_criacao * porcentagem_geracao_ocorrida)   # 0% -> 100%
        chance_mutacao = max_mutacao * (0.5 + 0.5 * porcentagem_geracao_ocorrida)   # 50% -> 100%

        nova_populacao = list()
        nova_populacao.extend(EI.gera_elite(populacao, q_elite))
        nova_populacao.extend(EI.gera_criacao(q_criacao))

        q_falta_gerar = tamanho - q_criacao - q_elite
        pais_e_maes = EI.roleta(populacao, 2 * q_falta_gerar)   # [pai, mae, pai, mae, pai, mae...]
        for i in range(q_falta_gerar):
            pai, mae = pais_e_maes[2 * i:2 * (i + 1)]
            filho = EI.crossover(pai, mae)

            if random.uniform(0, 1) <= chance_mutacao:
                filho.mutacao()
            nova_populacao.append(filho)

        populacao = nova_populacao
        # exibindo o melhor individuo até agora
        x = EI.n_melhores(populacao, 1)
        print("Ger %d (E: %0.2f, C: %0.2f, M: %0.2f): %0.3f (c: %0.3f)" % (
            geracao, q_elite, q_criacao, chance_mutacao, x.fitness, x.custo
        ))

    print("Finalizado")
    print("Melhor: ", EI.n_melhores(populacao, 1))
    return populacao


"""
O algoritmo genético de mutação não é muito diferente do algoritmo de crossover. As suas diferenças:

- Não há crossover. Em vez disso, o filho é uma mutação do pai.
- Como o crossover já é uma mutação, há uma chance depois de cada crossover de haver uma mutação diferente ("grave" ou "mudar")
- É mais devagar, pois a EscolhaMutação força com que todas as escolhas são sempre válidas, 
mesmo sofrendo alguma mutação.
"""
def algoritmo_genetico_mutacao(max_evolucoes):
    tamanho = 200
    max_elite = tamanho * 0.05  # 10% da populacao
    max_criacao = tamanho * 0.40  # 20% da populacao
    max_mutacao_grave = 0.20  # 20% de chance de se mutar grave
    populacao = [EM() for _ in range(tamanho)]

    for geracao in range(max_evolucoes):
        porcentagem_geracao_ocorrida = geracao / max_evolucoes
        q_elite = int(max_elite * (1 - 0.5 * porcentagem_geracao_ocorrida))  # 100% -> 50%
        q_criacao = int(max_criacao * porcentagem_geracao_ocorrida)  # 0% -> 100%
        chance_mutacao_grave = max_mutacao_grave * (0.5 + 0.5 * porcentagem_geracao_ocorrida)  # 50% -> 100%

        nova_populacao = list()
        nova_populacao.extend(EM.gera_elite(populacao, q_elite))
        nova_populacao.extend(EM.gera_criacao(q_criacao))

        q_falta_gerar = tamanho - q_criacao - q_elite
        
        pais = EM.roleta(populacao, q_falta_gerar)
        for pai in pais:
            filho = EM.crossover(pai)
            '''
            # ABANDONADO! MUITO COMPLEXO E DEMORADO
            pais = EM.roleta(populacao, 2 * q_falta_gerar)
            for i in range(q_falta_gerar):
                pai, mae = pais[2 * i:2 * (i + 1)]
                filho = EM.true_crossover(pai, mae)
            '''
            if random.uniform(0, 1) <= chance_mutacao_grave:
                filho.mutacao()
            nova_populacao.append(filho)
        populacao = nova_populacao
        # exibindo o melhor individuo até agora
        x = EM.n_melhores(populacao, 1)
        print("Ger %d (E: %0.2f, C: %0.2f): %s" % (
            geracao, q_elite, q_criacao, x
        ))

    print("Finalizado")
    print("Melhor: ", EM.n_melhores(populacao, 1))
    return populacao


if __name__ == "__main__":
    p = int(input("Digite max_evolucoes: "))
    t = time.time()
    # algoritmo_genetico_crossover(p)
    algoritmo_genetico_mutacao(p)
    print("Tempo de execucao: %.3fs" % (time.time() - t))
    """
    lista = []
    for i in range(100):
        pops = algoritmo_genetico_mutacao(5000)
        x = EM.n_melhores(pops, 1).custo
        lista.append(x)
    
    print(lista)
    print(min(lista))
    """
