# Simple driver implementation, whose main purpose is testing.

import engine.solver as FDTD
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy
from matplotlib.colors import LogNorm

import engine.sources as sources

g = FDTD.Grid(301,301)
for i in range(5):
    pos = numpy.random.random(2)*300
    parms = 2*(numpy.random.random(4) - 0.5)
    eff = 0.5
    g.add_source(
        sources.SourceDipole(
            (int(pos[0]), int(pos[1])),
            sources.PulseGaussian(
                1 * (1 + eff*parms[0]),
                300 * (1 + eff*parms[1]),
                100 * (1 + eff*parms[2]),
                1/40 * (1 + eff*parms[3])
            )
        )
    )

fig = plt.figure()
ax = plt.axes(xlim=(-100,300.5), ylim=(-0.5,300.5))
ax.set_aspect('equal')

data = g.get_field(2)._data
data = numpy.array(list(map(lambda x: 0*x+1e-10, data))) # TODO: clean this mess up
im = ax.imshow(numpy.abs(data), cmap=plt.get_cmap('jet'), norm=LogNorm(vmin=1e-4, vmax=2, clip=True))
g.get_field(2)._data = data
cbar = plt.colorbar(im, ax=ax)

text0 = ax.text(5,90, "f={:4d}".format(0))
text0.set_color('r')
text0.set_fontsize(20)

def init():
    data = g.get_field(2)._data
    im.set_data(numpy.abs(data))
    return [im]

def update(i):
    g.step(i)
    data = g.get_field(2)._data
    im.set_data(numpy.abs(data))
    text0.set_text("f={:4d}".format(i))
    return [im, text0]

anim = animation.FuncAnimation(
    fig,
    update,
    init_func=init,
    frames=800,
    repeat=False,
    interval=int(1000/30),
    blit=False
)

plt.show()

