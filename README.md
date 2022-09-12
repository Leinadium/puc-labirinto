# Trabalho 1 - INF1771

Desenvolvido por:

* Daniel Guimarães - 1910462
  
* Bruno Coutinho - 1910392

* Luiz Fellipe - 1711256

O vídeo da apresentação pode ser visualizado [neste link](https://youtu.be/qEskxllGtWM)

## Requirimentos

* Python >= 3.7
* Pygame >= 2.0

## Instalação

```shell
git clone https://github.com/Professor-Augusto-Baffa/trabalho-1---busca-e-otimizacao-truncate-cascade.git

cd trabalho-1---busca-e-otimizacao-truncate-cascade

# Para windows
python -m venv venv
venv/scripts/activate
pip install pygame
python main.py

# Para Linux/Mac
python3 -m venv venv
source venv/Scripts/activate
pip3 install pygame
python3 main.py
```

## Execução

### Modo de edição

Ao executar o arquivo main.py, uma tela pygame será exibida inicialmente. Ela é o campo a ser percorrido.

Essa tela inicial é o modo de edição. Clicando com o mouse, você pode editar o bloco para o tipo escolhido.

O tipo escolhido pode ser trocado digitando as teclas do mouse correspondente. As informações
estão no lado esquerdo.

Para sair e salvar, aperte *SPACE*

---

### Algoritmo Evolutivo

Logo após o modo de edição, o algoritmo evolutivo será iniciado. Este algoritmo tenta encontrar a melhor combinação de ataques
de pokemons por ginásio. Quanto menor o tempo necessário para atacar todos os ginásios, melhor.

As barras azul escuro são cada indivíduo de uma população de "Escolhas". Uma "Escolha" é uma combinação de pokemons e ginásios. Cada "Escolha"
tem um custo total associado. Ele é representado pela altura da barra azul. Quanto mais alto, pior

As barras azul claro são os melhores indivíduos da população (com menor custo, ou seja, menor altura). O grupo azul claro no canto direito é a "Elite", que é preservada de geração em geração. Ela começa sendo uma grande fatia da população, mas vai diminuindo conforme as gerações avançam.

O círculo vermelho indica qual foi a pior altura (ou pior custo) até agora. O círculo verde indica a menor altura (ou melhor custo).

No canto superior, está as informações da geração atual. "Tamanho" é o tamanho da população, que se mantém constante, "Elite" é a elite explicada acima, e "Criação" é uma fatia da população que é criada do zero a cada geração, para evitar que as gerações fiquem estagnadas.

Na linha abaixo, é indicada a melhor "Escolha" atual. f(x) é o *fitness* da escolha, um valor que aumenta conforme o custo cai, o c(x) é o *custo* da escolha, e a lista é a combinação de quais pokemons atacam qual ginásio. Cada colchete indica um estágio, e cada número indica o pokemon.

O melhor valor normalmente é encontrado em menos de 300 gerações, porém o algoritmo irá continuar rodando até 5000 gerações. Caso queira pular, aperte *SPACE* para avançar.

A dificuldade de cada ginásio, assim como a força de cada pokemon pode ser alterada nos arquivos ```/dados/ginasios.json``` e ```/dados/pokemons.json```

---

### Algoritmo A*

Após encontrada a combinação de pokemons e ginásios, o algoritmo de pathfinding é iniciado. Neste caso, o algoritmo começa na casa inicial, e tenta encontrar o melhor caminho até a casa final. Ao encontrar um ginásio, ele atribuirá o custo de acordo com os ginásios passados. Por exemplo, se ele encontrar um ginásio, e identificar que para aquele caminho ele já havia passado por *x* ginásios, ele irá atribuir o valor do ginásio *x+1*.

Ao chegar no final, o caminho ideal será exibido. O custo do caminho e a quantidade de ginásios passados podem ser acompanhadas ao vivo no lado esquerdo. A combinação de pokemons e ginásios encontradas na etapa anterior pode ser visualizada no lado direito.

Se ao chegar no final, o caminho não passar por todos os ginásios, será oferecido um recálculo, pois o melhor tempo ainda não foi encontrado (afinal, a combinação de pokemons e ginásios pode ser melhorada ignorando os ginásios não atacados). Para aceitar, aperte *SPACE*. Se ele utilizar todos os ginásios, o programa está finalizado.

---

## Código

O código do programa está quase todo no ```main.py```. Ele contém três classes, sendo as classes *Círculo* e *Campo* de auxílio para a parte gráfica. A classe *Simulação* é a classe que cuida da parte gráfica. Como o algoritmo A\* é muito dependente da parte gráfica, ele foi
desenvolvido como método da classe *Simulação*, ```Simulacao.a_estrela()```.

Já o algoritmo genético, ele foi desenvolvido a parte no arquivo ```/evolucao/algoritmo.py```. Dentro desse arquivo há duas funções, ```algoritmo_genetico_crossover()``` e ```algoritmo_genetico_mutacao()```. A diferença entre as duas é a maneira como foi implementada o algoritmo genético. Na primeira, o algoritmo admite escolhas *inválidas*, que quebram as regras definidas, como um pokemon atacar mais de uma vez. Ela admite essas escolhas inválidos pois isso permite um crossover muito rápido. Já a segunda, não existem escolhas inválidas. Todas as escolhas são sempre válidas. Porém, como isso torna um crossover sempre válido complexo, **não há crossover**, o filho é um mutação do pai. Para ter mais diversidade, há três tipos de mutação (explicadas no código).

Apesar das diferenças, o código do algoritmo é bem identico. A principal mudança está nas classes, ```EscolhaComInvalidez``` e ```EscolhaMutação```, cujo funcionamento foi explicado acima. O código delas está em ```/evolucao/escolha.py```.

Depois de duas semanas de testes, foi escolhido usar o método sem crossover, somente mutação. O código do algoritmo foi copiado, modificado de acordo com as necessidades da parte gráfica, e implementado como método da classe *Simulação*, ```Simulação.algoritmo_evolutivo()```.

---

## Outros detalhes

* Há uma pasta "rasc" contendo várias rascunhos de algoritmos, incluindo tentativas de algoritmos de *simulated annealing*, mas foram abandonados.

* A combinação ideal encontrada de pokemons e ginásios para as configurações padrão foi de **379.543**. Não foi encontrado nenhum valor menor, mesmo utilizando outros métodos, ou deixando computador para 100k gerações (aproximadamente 30min).

* As imagens foram inspiradas na internet, e desenhadas usando *inkscape* e *mspaint*.

* Há outras visualizações dos algoritmos na pasta rascunho, mas não há documentação para utiliza-las. É preciso instalar o módulo *matplotlib*.

* O motivo de haver uma separação entre algoritmo e objeto Escolha no algoritmo evolutivo era para haver um desenvolvimento em paralelo do algoritmo, assim como poder haver várias tentativas de representação da escolha sem precisar mudar o algoritmo. Tanto que há muito pouca diferença entre as funções dos algoritmos para a escolha com crossover e mutação, somente o número de pais que deve ser pego pela roleta (o modo usando crossover precisa de 2 pais para cada filho, já modo usando mutação somente 1 pai).

* Há um arquivo .bat que era executado para rodar testes com o algoritmo génetico. Ele está disponível em teste_genetico.bat

