from matplotlib import pyplot as plt
from matplotlib import animation
import matplotlib

import genetico_oo as gen


lista_populacoes = gen.algoritmo_genetico(500)
q_populacao = len(lista_populacoes[0])

fig = plt.figure()
ax = plt.axes(xlim=(0, q_populacao), ylim=(300, 600))
line, = ax.plot([], [], '.b')


def init():
    line.set_data([], [])
    return line,


def animate(i):
    x = range(q_populacao)
    y = lista_populacoes[i]
    line.set_data(x, y)
    return line,


matplotlib.rcParams['animation.ffmpeg_path'] = \
    r'C://Users//Daniel//PortableApps//AudacityPortable//App//FFMPeg//ffmpeg.exe'

print("Criando grafico...")
anim = animation.FuncAnimation(fig, animate, init_func=init, interval=100, blit=False)

anim.save('resultado.mp4', writer='ffmpeg')
print("Finalizado")