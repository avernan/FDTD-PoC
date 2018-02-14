import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Constants
Z0 = 377.0

# Global parameters (only change after the code is correct)
LENGTH = 1000
AMPLITUDE = 1
SOURCE_POSITION = 500
FREQ = 1/20
TAU = 200

# TODO
# All you need to write should be contained in the following two functions
# "init" and "update".

def init():
    """
    Initialize everything that is needed for the FDTD simulation, namely "allocate"
    some space for the E and H fields (which are scalars in the 1D formulation)
    """
    E = # TODO
    H = # TODO

    return (E, H)

def update(t, E, H, txt, line):
    """
    Implement the main FDTD algorithm. This should move H and E fields forward one step, apply
    boundary conditions (PML) as needed and apply the dipolar source
    """
    # TODO Update H

    # TODO Update E

    # TODO Boundary conditions

    # TODO Source(s)

    # Update the plot in the animation
    line.set_ydata(E)
    txt.set_text("frame {:4d}".format(t))
    return [txt, line]

def source(time, **kwargs):
    if time < 0:
        source.E0 = kwargs['E0']
        source.freq = kwargs['freq']
        source.tau = kwargs['tau']
        source.t0 = 10*kwargs['tau']
    else:
        val = source.E0 * np.sin(source.freq * time) * np.math.exp(- (time - source.t0)**2 / source.tau**2)
        return val

if __name__ == "__main__":
    E, H = init()

    source(-1, E0=AMPLITUDE, freq=FREQ, tau=TAU)

    fig = plt.figure()
    ax = plt.axes(xlim=(0, LENGTH-1), ylim=(-AMPLITUDE, AMPLITUDE))
    E_line, = ax.plot(E)
    txt = ax.text(0.1*LENGTH,0.9*AMPLITUDE, "frame {:4d}".format(0))

    anim = animation.FuncAnimation(
        fig,
        func=update,
        frames=10000,
        interval=10,
        fargs=(E, H, txt, E_line),
        repeat=False,
        blit=True
    )
    plt.show()
