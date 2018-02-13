# Simple driver implementation, whose main purpose is testing.

from datetime import datetime as dt
import engine.solver as FDTD
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy
import engine.boundaries as bounds
import engine.sources as sources

def to_msec(x):
    return x.seconds * 1000 + x.microseconds/1000

def run(grid, frames=1000):

    fig = plt.figure()
    plt.subplots_adjust(top=0.8)
    ax = plt.axes(xlim=(-0.5,grid.shape[0]-0.5), ylim=(-0.5,grid.shape[1]-0.5))
    ax.set_aspect('equal')

    data = grid.get_field(2)._data
    im = ax.imshow(numpy.transpose(data), cmap=plt.get_cmap('coolwarm'), vmin=-1.05, vmax=1.05)
    plt.colorbar(im, ax=ax)

    time = [dt.now(), dt.now()]
    elaps_gen = [0] * 50; elaps_rend = [0] * 50
    txt = "frame {:4d}\nTimes: {:.2f} ms (gen.), {:.2f} ms (rend.)\nFPS: {:.1f}"
    text0 = ax.text(int(shape[0]/2),int(shape[1]*1.20),
                    txt.format(0, sum(elaps_gen)/len(elaps_gen), sum(elaps_rend)/len(elaps_rend), 0),
                    horizontalalignment="center", verticalalignment="top", color="r", fontsize=16)

    def init():
        data = grid.get_field(2)._data
        im.set_data(numpy.transpose(data))

    def update(i):
        time[0] = dt.now()
        elaps_rend.pop(0)
        elaps_rend.append(to_msec(time[0] - time[1]))
        grid.step(i)
        time[1] = dt.now()
        elaps_gen.pop(0)
        elaps_gen.append(to_msec(time[1] - time[0]))
        data = grid.get_field(2)._data
        im.set_data(numpy.transpose(data))
        text0.set_text(txt.format(
            i, sum(elaps_gen)/len(elaps_gen), sum(elaps_rend)/len(elaps_rend),
            1000 / (sum(elaps_rend)/len(elaps_rend) + sum(elaps_gen)/len(elaps_gen))
        ))

    anim = animation.FuncAnimation(
        fig,
        update,
        init_func=init,
        frames=frames,
        repeat=False,
        interval=int(1000/30),
        blit=False
    )

    plt.show()

if __name__ == '__main__':
    # Define grid size
    shape = numpy.array((800, 800))
    g = FDTD.Grid(*shape)

    # Add sources
    # In this case a TFSF box with 50 cells spacing on each side
    buffer = numpy.array((50, 50))

    sources.SourceTFSF(g, buffer, shape-buffer, sources.PulseGaussian(1, 500, 200, 1/20))
    sources.SourceDipole(g, (600,400), sources.PulseGaussian(10, 300, 100, 1/20))

    # Set boundary conditions
    # Here absorbing boundaries to simulate an open system
    g.set_boundaries(xm=bounds.ABC, ym=bounds.ABC, xp=bounds.PEC, yp=bounds.PEC)

    # Build and validate the FDTD setup
    g.build()

    # Run simulation and animation for nstep steps
    nsteps = 4000
    run(g, nsteps)
