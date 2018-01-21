# Simple driver implementation, whose main purpose is testing.

import numpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.colors import LogNorm
import FDTDPoC.engine.solver as FDTD

g = FDTD.Grid(301,301)

fig = plt.figure()
ax = plt.axes(xlim=(-0.5,300.5), ylim=(-0.5,300.5))
ax.set_aspect('equal')

data = g.get_field(2)._data
im = ax.imshow(numpy.abs(data), cmap=plt.get_cmap('jet'), norm=LogNorm(vmin=1e-4, vmax=2, clip=True))
cbar = plt.colorbar(im, ax=ax)

text0 = ax.text(5,90, "f={:4d}".format(0))
text0.set_color('r')
text0.set_fontsize(20)

mu = 300
w = 1/40
s = 100

def source(i):
    return numpy.math.exp(-(i - mu)**2/s**2) * numpy.math.cos(2*numpy.math.pi*w*i)

def init():
    data = g.get_field(2)._data
    im.set_data(numpy.abs(data))
    return [im]

def update(i):
    g.step(i, (200,200,source(i)))
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
    blit=True
)

plt.show()

