"""
Arquivo principal de execução
"""
import os
import time
import random
from math import sin, cos, pi
from queue import PriorityQueue

import pygame
import pygame.freetype

from evolucao.escolha import EscolhaMutacao as EM
from evolucao.escolha import ginasios, pokemons

COMPRIMENTO, ALTURA = 1280, 720
QUANTIDADE_BLOCOS = 42, 42
TAMANHO_BLOCO_X, TAMANHO_BLOCO_Y = 16, 16
BORDA = 304, 24

MAX_POPULACAO = 300

NOME_TIPO = {
    'M': 'Floresta Densa / [M]ontanhoso',
    'R': 'Floresta / [R]ochoso',
    '.': 'Campo / [P]lanície',
    'B': 'Ginásio / [B]ase',
    'I': '[I]nicio',
    'F': '[F]inal'
}

COR_TIPO = {
    'RED': (200, 0, 0),
    'GREEN': (0, 200, 0),
    'M': (105, 105, 105),
    'R': (161, 161, 161),
    'B': (222, 232, 28),
    'I': (232, 133, 28),
    'F': (23, 181, 2),
    '.': (255, 255, 255),
    'verificar': (0, 8, 252, 0.5),
    'verificado': (0, 236, 252, 0.5),
    'verificando': (255, 0, 0, 1),
    'caminho': (255, 255, 0, 0.8)
}
PATH_FONT = os.path.join(os.path.dirname(__file__), 'graficos', 'JetBrainsMono-Bold.ttf')
PATH_CAMPO = os.path.join(os.path.dirname(__file__), 'dados', 'campo.txt')
PATH_ESCOLHAS = os.path.join(os.path.dirname(__file__), 'dados', 'escolhas.json')
PATH_FIGURA = {
    'M': os.path.join(os.path.dirname(__file__), 'graficos', 'm.png'),
    'R': os.path.join(os.path.dirname(__file__), 'graficos', 'r.png'),
    '.': os.path.join(os.path.dirname(__file__), 'graficos', 'dot.png'),
    'I': os.path.join(os.path.dirname(__file__), 'graficos', 'i.png'),
    'F': os.path.join(os.path.dirname(__file__), 'graficos', 'f.png'),
    'B': os.path.join(os.path.dirname(__file__), 'graficos', 'b.png'),
}

PATH_POKEMONS = {
    5: os.path.join(os.path.dirname(__file__), 'graficos', 'pikachu.png'),
    4: os.path.join(os.path.dirname(__file__), 'graficos', 'bulbasaur.png'),
    3: os.path.join(os.path.dirname(__file__), 'graficos', 'rattata.png'),
    2: os.path.join(os.path.dirname(__file__), 'graficos', 'caterpie.png'),
    1: os.path.join(os.path.dirname(__file__), 'graficos', 'weedle.png')
}

class Circulo:
    """
    Classe para visualizacao do algoritmo genético em círculo.
    O circulo são várias barras, em cada cada um representa um indivíduo.
    Quanto maior a barra, maior o custo
    A barra azul clara é a melhor escolha atualmente
    O círculo verde representa a melhor altura, e a vermelha é a pior altura que já ocorreu.
    """

    def __init__(self, tamanho):
        """Inicializa um objeto Círculo configurando as variáveis iniciais

        Args:
            tamanho (float): raio máximo do circulo
        """
        self.tamanho = tamanho
        self.lista_raw = list()
        self.lista_pos = list()
        self.tamanho_lista = MAX_POPULACAO
        self.melhor = -1
        self.pior = -1
        self.media = -1
        self.melhor_raio = 0
    
    def atualizar(self, nova_lista):
        """
        Atualiza o circulo com uma lista de novos valores (gerados da evolução)
        """
        # inicia a nova lista e as listas auxiliares
        self.lista_raw = nova_lista
        self.lista_pos = [None] * self.tamanho_lista

        # acha o melhor, menor e media
        self.melhor = min(self.lista_raw)
        self.pior = max(max(self.lista_raw), self.pior)  # so atualiza se for pior ainda
        self.media = sum(self.lista_raw) / len(self.lista_raw)

        # calculando a posicao de cada ponto no circulo
        for i, valor in enumerate(self.lista_raw):
            # o valor vai de 0 até o maior.
            # transformando de r, theta (custo, angulo) para x, y
            r = self.tamanho * valor / self.pior
            theta = 2 * pi * (i / self.tamanho_lista)
            x, y = r * cos(theta), r * sin(theta)
            cor = tuple(COR_TIPO['verificar'][:3])   # cor generica
            if valor - self.melhor <= 0.001:
                cor = tuple(COR_TIPO['verificado'][:3])  # cor diferente para se destacar
                self.melhor_raio = r
            self.lista_pos[i] = x, y, cor
        return
    
    def iter_pos(self):
        """Iterador para cada posição x, y das barras.

        Returns:
            iter: posicoes (x, y) da ponta de cada raio
        """
        return iter(self.lista_pos)           

class Campo:
    """Classe para a visualização do campo
    O campo é constituido de vários blocos, cada um com um tipo
    """
    # custo de cada tipo de bloco
    CUSTO = {
        'M': 200,  # montanha / floresta densa
        'R': 5,    # floresta
        '.': 1,    # caminho plano 
        'I': 1,    # inicio
        'F': 1,    # fim
        'B': 1     # base/ginásio
    }

    def __init__(self):
        """Inicia um objeto Campo, coletando os dados do arquivo
        e iniciando as variáveis.
        """
        self.dicionario = dict()
        self.inicio = None
        self.fim = None

        # lendo o arquivo e convertendo para dicionario[tupla] = tipo
        with open(PATH_CAMPO, 'r') as f:
            for y, line in enumerate(f):
                line = line.strip()
                for x, tipo in enumerate(line):
                    if tipo == 'I':
                        self.inicio = x, y  # salvando o inicio
                    elif tipo == 'F':
                        self.fim = x, y  # salvando o fim

                    self.dicionario[(x, y)] = tipo

        return

    def salvar(self):
        """
        Salva o dicionario no arquivo em .txt
        :return: none
        """
        final = []
        for y in range(QUANTIDADE_BLOCOS[1]):
            ss = ''
            for x in range(QUANTIDADE_BLOCOS[0]):
                ss += str(self.dicionario[(x, y)])
            final.append(ss)

        with open(PATH_CAMPO, 'w+') as f:
            f.write('\n'.join(final))

        return

    def get_bloco(self, pos):
        """Retorna o tipo do bloco naquela posicao

        Args:
            pos (int, int): posicao do bloco

        Returns:
            string: tipo do bloco
        """
        return self.dicionario.get(pos)

    def set_bloco(self, pos, tipo):
        """Atualiza o tipo do bloco naquela posicao

        Args:
            pos (int, tin): posicao do bloco
            tipo (string): novo tipo do bloco
        """
        self.dicionario[pos] = tipo
        return

    def __iter__(self):
        """Iterador do objeto Campo. Itera por cada posicao e tipo

        Yields:
            Tuple(Tuple(int, int), string): posicao, tipo do bloco
        """
        for key in self.dicionario:
            yield key, self.dicionario[key]

    def get_vizinhos(self, pos):
        """Retorna todas as posições vizinhas válidas daquela posicao.
        Essa é umas das funções mais importantes para o A* e Dijkstra

        Args:
            pos (Tuple(int, int)): posicao do bloco

        Returns:
            List(Tuple(int, int)): lista de posições de blocos vizinhos
        """
        x, y = pos
        ret = [(x, y+1), (x, y-1), (x-1, y), (x+1, y)]
        for r in ret:
            if r not in self.dicionario:
                ret.remove(r)
        return ret

    @staticmethod
    def distancia(pos1, pos2, tipo='manhattan'):
        """
        Determina a distancia entre duas posicoes de acordo com o tipo com o tipo de algoritmo.
        Tipos implementados: "manhattan", "euclidean"
        """

        if tipo == 'manhattan':
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        if tipo == 'euclidean':
            return ((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)**(1/2)

        else:
            raise Exception("TipoNaoImplementado", "Verifique se o tipo da distancia foi implementado")

    @staticmethod
    def converte(modo, x, y):
        """
        Converte um tipo de coordenada para outro
        modo 'campo': recebe a coordenada do campo, e converte para coordenada correspondente da tela
        modo 'tela': recebe a coordenada da tela, e coloca para coordenada correspondente do campo
        """
        if modo == 'campo':
            return BORDA[0] + x * TAMANHO_BLOCO_X, BORDA[1] + y * TAMANHO_BLOCO_X

        elif modo == 'tela':
            return (x - BORDA[0]) // TAMANHO_BLOCO_X, (y - BORDA[1]) // TAMANHO_BLOCO_Y

        else:
            raise Exception("ModoInvalido")

class Simulacao:
    """Classe principal para a parte gráfica. 
    Possui todos os métodos para visualização.
    """
    def __init__(self):
        """Inicia as variáveis utilizadas na simulação
        """
        # inicia o pygame e seus parâmetros
        pygame.init()
        self.tamanho = COMPRIMENTO, ALTURA
        self.tela = pygame.display.set_mode(self.tamanho)
        self.font = pygame.freetype.Font(open(PATH_FONT, 'r'))

        self.tecla_pressionada = False
        self.tecla_pressionada_anterior = False
        self.pos_mouse = None
    
        # configurações do campo
        self.campo = Campo()
        # um campo paralelo para ter os blocos atualizados pelo algoritmo
        self.campo_atualizado = dict()  # dicionario[pos] -> cor
        self.ginasios_a_passar = len(ginasios)
        self.ginasios_passados = 0
        self.custo_total_atual = 0
        # armazenamento das figuras do campo
        self.figuras = dict()
        for fig, p in PATH_FIGURA.items():
            x = pygame.image.load(p)
            x.convert()  # otimiza um pouco
            self.figuras[fig] = x
        # armazenamento das figuras dos pokemons
        self.figuras_pokemons = dict()
        self.max_pokemons_por_ginasio = 2  # valor default
        
        # configuracao do circulo
        self.tam_max_circulo = min(COMPRIMENTO, ALTURA) / 3
        self.centro_circulo = COMPRIMENTO // 2, ALTURA // 2
        self.circulo = Circulo(self.tam_max_circulo)
        self.melhor_escolha = None
        self.lista_custos = list()
        self.quit_circulo = False

        # para edicao do tabuleiro
        self.quit_edicao = False
        self.tipo_preenchimento = 'M'

    def carregar_imagens_pokemons(self):
        """Carrega as imagens dos pokemons no dicionario
           Já converte para o tamanho apropriado de acordo com a maior quantidade de pokemons
           em um ginasio
        """
        if self.melhor_escolha:
            self.max_pokemons_por_ginasio = len(max(self.melhor_escolha.cromossomo.values(), key=len))
        else:
            self.max_pokemons_por_ginasio = 2

        # quantidade esta entre 2 e 5
        # fator de transform esta entre 2 e 1
        fator = int(2 - ((self.max_pokemons_por_ginasio - 2) / 3))

        for fig, p in PATH_POKEMONS.items():
            img = pygame.image.load(p)
            x, y = img.get_width(), img.get_height()
            img = pygame.transform.scale(img, (fator * x, fator * y))
            img.convert()
            self.figuras_pokemons[fig] = img
        return

    def desenha_escolha(self):
        """Desenha as informações do algoritmo genético.
        """
        # a tela nao sera preenchida de preta
        # pois a exibição será só de textos
        # logo, sera exibida por cima de algo já existente

        # exibindo cada ginásio e seu custo
        for i, (g, poks) in enumerate(self.melhor_escolha.cromossomo.items(), 1):  # [g] -> p
            x, y = BORDA[0] + ALTURA, i * int(ALTURA / (self.ginasios_a_passar + 1))
            self.font.render_to(self.tela, (x, y), 'Gym %2d: ' % g, size=25, fgcolor=(255, 255, 255))
            for j, pok in enumerate(poks):
                fig = self.figuras_pokemons[pok]
                rect = fig.get_rect()
                rect.x, rect.y = x + 120 + (rect.width + 10) * j, y - (rect.height // 2)
                self.tela.blit(fig, rect)


        # exibindo o total dos ginásios
        texto = "Soma dos ginasios: %0.3f min" % self.melhor_escolha.custo   
        self.font.render_to(self.tela, (10, 30), texto, size=15, fgcolor=(255, 255, 255))

        # exibindo o custo final
        texto = "Custo final: %0.3f min" % (self.custo_total_atual)
        self.font.render_to(self.tela, (10, 70), texto, size=15, fgcolor=(255, 255, 255))
        texto = "Ginasios passados: %2d/%2d" % (self.ginasios_passados, self.ginasios_a_passar)
        self.font.render_to(self.tela, (10, 90), texto, size=15, fgcolor=(255, 255, 255))

        return

    def desenha_edicao(self):
        while not self.quit_edicao:
            self._checa_evento()  # atualiza os dados
            if self.pos_mouse is not None:  # verifica se clicou no mouse
                self.edita_campo()  # edita o campo com a posicao do mouse
            self.desenha_campo(edicao=True)  # desenha o campo
            
            # desenhando o manual
            self.font.render_to(self.tela, (10, 10), 'Modo de edição', size=15, fgcolor=(255, 255, 255))
            self.font.render_to(self.tela, (10, 30), '[SPACE] para salvar e iniciar', size=15, fgcolor=(255, 255, 255))

            self.font.render_to(self.tela, (10, 100), 'Clique no quadrado', size=15, fgcolor=(255, 255, 255))
            self.font.render_to(self.tela, (10, 120), 'para mudar seu tipo', size=15, fgcolor=(255, 255, 255))

            self.font.render_to(self.tela, (10, 210), 'Tipo atual: ', size=13, fgcolor=(255, 255, 255))
            texto = '%s - %s' % (self.tipo_preenchimento, NOME_TIPO[self.tipo_preenchimento])
            self.font.render_to(self.tela, (10, 228), texto, size=13, fgcolor=(255, 255, 255))

            self.font.render_to(self.tela, (10, 310), 'Digite M, R, ., ', size=13, fgcolor=(255, 255, 255))
            self.font.render_to(self.tela, (10, 328), 'G, I ou F para trocar o tipo', size=13, fgcolor=(255, 255, 255))
            pygame.display.update()
        self.campo.salvar()
        return

    def desenha_campo(self, edicao=False):
        """Desenha o campo e o progresso do algoritmo A*/Dijkstra atualmente
        """
        # preenchendo de preto
        self.tela.fill((0, 0, 0))

        for pos, tipo in self.campo:
            x, y = Campo.converte('campo', pos[0], pos[1])

            # desenha a figura
            img = self.figuras[tipo]
            rect = img.get_rect()
            rect.x, rect.y = x, y
            self.tela.blit(img, rect)

            # verifica se o bloco eh atualizado (verificar, verificado ou caminho)
            if pos in self.campo_atualizado:
                cor = COR_TIPO.get(self.campo_atualizado.get(pos))

                surf = pygame.Surface((TAMANHO_BLOCO_X, TAMANHO_BLOCO_Y))
                surf.set_alpha(255 * cor[-1])
                surf.fill(cor)
                self.tela.blit(surf, rect)

        if edicao:
            return
            
        # desenha os dados do algoritmo genético no canto da tela
        self.desenha_escolha()
            # atualiza a tela
        pygame.display.update()
        return

    def desenha_circulo(self, gen, q_elite, q_criacao, melhor):
        """Desenha o progresso do algoritmo genético

        Args:
            gen (int): geração atual
            q_elite (int): quantidade de indivíduos na elite
            q_criacao (int): quantidade de indivíduos de criação
            melhor (Escolha): melhor indivíduo
        """
        # mostrando cada escolha individualmente
        self.tela.fill((0, 0, 0))

        # imprime os dados do progresso
        texto = "Ger %d (Total: %d, Elite: %d, Criacao: %d)" % (gen, MAX_POPULACAO, q_elite, q_criacao)
        self.font.render_to(self.tela, (10, 10), texto, size=15, fgcolor=(255, 255, 255))

        texto = "Média (custo): %.3f, Pior (custo): %.3f" % (self.circulo.media, self.circulo.pior)
        self.font.render_to(self.tela, (10, 50), texto, size=15, fgcolor=(255, 255, 255))

        # imprimindo o melhor indivíduo
        texto = str(melhor)
        self.font.render_to(self.tela, (10, 30), texto, size = 15, fgcolor = (255, 255, 255))
        
        # texto para pular
        texto = "Aperte [SPACE] para usar a combinação atual"
        self.font.render_to(self.tela, (10, 80), texto, size=15, fgcolor=(255, 255, 255))

        for x, y, cor in self.circulo.iter_pos():
            x += self.centro_circulo[0]
            y += self.centro_circulo[1] 
            pygame.draw.line(self.tela, cor, self.centro_circulo, (x, y), width=2)

        # mostrando os limites do círculo
        pygame.draw.circle(self.tela, COR_TIPO['RED'], self.centro_circulo,
                           self.tam_max_circulo, width=2)
        
        pygame.draw.circle(self.tela, COR_TIPO['GREEN'], self.centro_circulo,
                           self.circulo.melhor_raio, width=2)

        pygame.display.update()
        return

    def edita_campo(self):
        pos = self.pos_mouse
        x, y = Campo.converte('tela', pos[0], pos[1])
        if 0 <= x < QUANTIDADE_BLOCOS[0] and 0 <= y < QUANTIDADE_BLOCOS[1]:
            self.campo.set_bloco((x, y), self.tipo_preenchimento)
        return

    def atualiza_bloco(self, pos, tipo, limpar=False):
        """
        Atualiza a posição do bloco de acordo com o algoritmo
        tipo = 'verificar' ou 'verificado' ou 'caminho' ou 'verificando'.
        Se limpar for definido, o campo todo será reiniciado
        """
        if limpar:
            self.campo_atualizado.clear()
            return

        if tipo not in ['verificar', 'verificado', 'caminho', 'verificando']:
            raise Exception("TipoInvalido")

        self.campo_atualizado[pos] = tipo
        return

    def _checa_evento(self):
        """
        Retorna um dicionario com os eventos realizados
        :return dicionario[evento] -> dados_do_evento
        """
        self.tecla_pressionada_anterior = self.tecla_pressionada
        self.tecla_pressionada = False
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.pos_mouse = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP:
                self.pos_mouse = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.tecla_pressionada = True
                    if self.tecla_pressionada and not self.tecla_pressionada_anterior:
                        if not self.quit_edicao:
                            self.quit_edicao = True
                        elif not self.quit_circulo:
                            self.quit_circulo = True

                elif event.key == pygame.K_m:
                    self.tipo_preenchimento = 'M'
                elif event.key == pygame.K_r:
                    self.tipo_preenchimento = 'R'
                elif event.key == pygame.K_b:
                    self.tipo_preenchimento = 'B'
                elif event.key == pygame.K_i:
                    self.tipo_preenchimento = 'I'
                elif event.key == pygame.K_f:
                    self.tipo_preenchimento = 'F'
                elif event.key == pygame.K_PERIOD:
                    self.tipo_preenchimento = '.'
                elif event.key == pygame.K_g:
                    self.tipo_preenchimento = 'G'

            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)

    def wait(self, ms):
        """Espera por alguns milisegundos, porem sem travar o pygame

        Args:
            ms (float): milisegundos de espera
        """
        t = time.time()
        while time.time() - t < ms / 1000:
            self._checa_evento()
        return

    def a_estrela(self): 
        """
        Implementação do A*, atualiza a parte gráfica ao longo da execução.
        """


        # para cada posição p, gScore[p] é o custo do caminho da posicao inicial até p
        gScore = dict()
        # para cada posição p, count_ginasios_passados[p] é o número de ginásios passados até chegar em p
        count_ginasios_passados = dict()
        # para cada posição p, pos_anterior[p] é a posição precedente no mais caminho mais curto da origem
        pos_anterior = dict()
        # para cada posição p, se blocos_passados[p] então p nao sera mais visitado
        blocos_passados = dict()
        # fila ordenada pelo menor f(n). Cada elemento é da forma (f(n), (x_pos, y_pos))
        posicoes_em_aberto = PriorityQueue()

        for pos, _ in self.campo:
            gScore[pos] = 10000000
            pos_anterior[pos] = None
            count_ginasios_passados[pos] = 0
        gScore[self.campo.inicio] = 0
        fScore_inicio = 0 + self.campo.distancia(self.campo.inicio, self.campo.fim, 'manhattan')
        posicoes_em_aberto.put((fScore_inicio, self.campo.inicio))
        
        self.carregar_imagens_pokemons()                                    # parte grafica

        while not posicoes_em_aberto.empty():
            # pega a posicao com o menor fscore no momento
            pos_atual = posicoes_em_aberto.get()[1]
            blocos_passados[pos_atual] = True

            self.atualiza_bloco(pos_atual, 'verificando')                   # parte grafica
            self.desenha_campo()                                            # parte grafica
            self.wait(2)                                                    # parte grafica
            self.custo_total_atual = gScore[pos_atual]                      # parte grafica
            self.ginasios_passados = count_ginasios_passados[pos_atual]     # parte grafica

            if self.campo.get_bloco(pos_atual) == 'F':
                while pos_atual is not None:
                    self.atualiza_bloco(pos_atual, 'caminho')               # parte grafica
                    pos_atual = pos_anterior[pos_atual]
                    self.desenha_campo()                                    # parte grafica
                    self.wait(3)                                            # parte grafica
                return
            
            elif self.campo.get_bloco(pos_atual) == 'B':
                count_ginasios_passados[pos_atual] += 1
            
            for vizinho in self.campo.get_vizinhos(pos_atual):
                if vizinho in blocos_passados:
                    continue
                self.atualiza_bloco(vizinho, 'verificar')                   # parte grafica
                
                tipo = self.campo.get_bloco(vizinho)
                if tipo == 'B':
                    if count_ginasios_passados[pos_atual] >= len(self.lista_custos):
                        custo = 10000  # ginasio nulo, que nao da para passar
                    else:
                        custo = self.lista_custos[count_ginasios_passados[pos_atual] + 1 - 1]  # -1 pois a lista comeca em 0
                else:
                    custo = Campo.CUSTO[tipo]
                
                possivel_novo_gScore = gScore[pos_atual] + custo
                if possivel_novo_gScore < gScore[vizinho]:
                    pos_anterior[vizinho] = pos_atual
                    gScore[vizinho] = possivel_novo_gScore
                    fScore = gScore[vizinho] + self.campo.distancia(vizinho, self.campo.fim, 'manhattan')
                    posicoes_em_aberto.put((fScore, vizinho))
                    count_ginasios_passados[vizinho] = count_ginasios_passados[pos_atual]
            
            self.atualiza_bloco(pos_atual, 'verificado')                    # parte grafica

        return

    def dijkstra(self):
        self.carregar_imagens_pokemons()                                    # parte grafica

        Q = dict()
        dist = dict()
        gin = dict()
        prev = dict()

        for v, _ in self.campo:
            dist[v] = 10000000
            prev[v] = None
            gin[v] = 0
            Q[v] = 1
        dist[self.campo.inicio] = 0

        while Q:
            self.desenha_campo()                        # parte grafica
            self.wait(5)                                # parte grafica

            menor_dist = 10000000
            u = None
            for v in Q:
                if dist[v] <= menor_dist:
                    u = v
                    menor_dist = dist[v]

            Q.pop(u)
            self.atualiza_bloco(u, 'verificado')        # parte grafica
            self.custo_total_atual = dist[u]            # parte grafica
            self.ginasios_passados = gin[u]             # parte grafica

            if self.campo.get_bloco(u) == 'F':
                while u is not None:
                    self.atualiza_bloco(u, 'caminho')   # parte grafica
                    u = prev[u]
                self.desenha_campo()                    # parte grafica
                return
            
            elif self.campo.get_bloco(u) == 'B':
                gin[u] += 1

            for vizinho in self.campo.get_vizinhos(u):
                if vizinho not in Q:
                    continue
                self.atualiza_bloco(vizinho, 'verificar')       # parte grafica
                tipo = self.campo.get_bloco(vizinho)
                if tipo == 'B':
                    custo = self.lista_custos[gin[u] + 1 - 1]  # +1 pois é o proximo ginasio, -1 pois a lista comeca em 0
                    if custo is None:
                        custo = 10000  # ginasio nulo, que nao da para passar
                else:
                    custo = Campo.CUSTO[tipo]

                alt = dist[u] + custo
                if alt < dist[vizinho]:
                    dist[vizinho] = alt
                    prev[vizinho] = u
                    gin[vizinho] = gin[u]
        return

    def algorimo_evolutivo(self, max_evolucoes):
        """
        Algorimto genético.
        Uma melhor explicação pode ser encontrada em ./evolucao/algoritmo
        """
        tamanho = MAX_POPULACAO
        max_elite = tamanho * 0.10  # 10% da populacao
        max_criacao = tamanho * 0.20   # 20% da populacao
        max_mutacao = 0.20  # 20% de chance de se mutar
        populacao = [EM() for _ in range(tamanho)]

        for geracao in range(max_evolucoes):
            porcentagem = geracao / max_evolucoes
            q_elite = int(max_elite * (1 - 0.7 * porcentagem))  # 10% -> 3%
            q_criacao = int(max_criacao * porcentagem)  # 0% -> 20%
            chance_mutacao = max_mutacao * (0.5 + 0.5 * porcentagem)   # 10% -> 20%

            nova_populacao = list()
            nova_populacao.extend(EM.gera_elite(populacao, q_elite))
            nova_populacao.extend(EM.gera_criacao(q_criacao))

            q_falta_gerar = tamanho - q_criacao - q_elite
            pais = EM.roleta(populacao, q_falta_gerar)
            for pai in pais:
                filho = EM.crossover(pai)
                if random.uniform(0, 1) <= chance_mutacao:
                    filho.mutacao()
                nova_populacao.append(filho)
            
            populacao = nova_populacao
        
            # atualização da parte gráfica
            self.circulo.atualizar([x.custo for x in populacao])
            self.melhor_escolha = EM.n_melhores(populacao, 1)
            self.lista_custos = [ginasios[g] / sum(pokemons[p] for p in poks)
                                 for g, poks in self.melhor_escolha.cromossomo.items()]
            self.desenha_circulo(geracao, q_elite, q_criacao, self.melhor_escolha)
            self.wait(5)
            if self.quit_circulo:
                return   # saindo antes do final

        return

    def run(self):
        # edicao do campo
        self.desenha_edicao()

        self.algorimo_evolutivo(5000)
        
        # self.dijkstra()
        self.a_estrela()

        # caso nao tenha finalizado
        while self.ginasios_passados > 0 and self.ginasios_passados < self.ginasios_a_passar:
            # espera clicar espaco para reiniciar
            self.quit_edicao = False
            while not self.quit_edicao:
                self._checa_evento()  # atualiza os dados
            
            # altera os dados para o algoritmo dos ginasios
            self.ginasios_a_passar = self.ginasios_passados
            EM.alterar_propriedades(q_ginasios=self.ginasios_a_passar)
            
            # reseta os dados do circulo e do campo
            self.quit_circulo = False
            self.atualiza_bloco(0, 0, limpar=True)

            # roda novamente
            self.algorimo_evolutivo(5000)
            self.a_estrela()

        # loop final
        while True:
            self._checa_evento()
        return

if __name__ == "__main__":
    s = Simulacao()
    s.run()
