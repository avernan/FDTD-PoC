# Simple driver implementation, whose main purpose is testing.
import tkinter as tk
from tkinter.font import Font
from tkinter.ttk import Button, Frame, Label
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from datetime import datetime as dt
import engine as FDTD
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy
import engine.boundaries as bounds
import engine.sources as sources
from utilities import SafeLogNorm

matplotlib.use('TkAgg')
plt.ion()

root = tk.Tk()

shape = (301, 301)
eff = 0.5

g = FDTD.Grid(*shape)

for i in range(5):
    pos = numpy.array(shape) * numpy.random.random(2)
    parms = numpy.random.random(4)
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

g.set_boundaries(xm=bounds.PEC(), xp=bounds.PEC(), ym=bounds.PEC(), yp=bounds.PEC())
g.build()

CON = 2.54
fig = Figure(figsize=(10/CON,10/CON), dpi=94)
ax = fig.add_subplot(111, xlim=(-0.5, shape[0]-0.5), ylim=(-0.5,shape[1]-0.5), aspect='equal')


data = g.get_field(2)._data
# TODO: smaller value of `vmin` is required to hide ABC reflection on log scale
im = ax.imshow(numpy.abs(numpy.transpose(data)), cmap=plt.get_cmap('inferno'), norm=SafeLogNorm(vmin=1e-6, vmax=2, clip=True))

time = [dt.now(), dt.now()]
elaps_gen = [0] * 50
elaps_rend = [0] * 50
# txt = "frame {:4d}\nTimes: {:.2f} ms (gen.), {:.2f} ms (rend.)\nFPS: {:.1f}"
# text0 = ax.text(int(shape[0]/2),int(shape[1]*1.20), txt.format(0, sum(elaps_gen)/len(elaps_gen), sum(elaps_rend)/len(elaps_rend), 0))
# text0.set_horizontalalignment("center")
# text0.set_verticalalignment("top")
# text0.set_color('r')
# text0.set_fontsize(16)

main_frame = Frame(root)

txt = (
    "Frame {:4d}\tFPS {:.1f}\n"
    "Times: {:.2f} ms (gen.)\t {:.2f} ms (rend.)"
)
f = Font(family="Helvetica", size=16, weight="bold")
v_t = tk.StringVar()
text = Label(main_frame, textvariable=v_t, width=6, foreground="#F00")
text.pack(side=tk.TOP, fill=tk.X)

v_t.set(txt.format(0, 0, sum(elaps_gen)/len(elaps_gen), sum(elaps_rend)/len(elaps_rend)))

def test():
    print("Hello")
    root.quit()


fig_canvas = FigureCanvasTkAgg(fig, master=main_frame)
fig_canvas.show()
fig_canvas.get_tk_widget().pack(side=tk.TOP)

buttons_frame = Frame(main_frame)
buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)
b = Button(buttons_frame, text="Exit", command=test)
b.pack(side=tk.RIGHT)

main_frame.pack()

# TODO: should avoid transposing data every time. Too easy to forget
def init():
    data = g.get_field(2)._data
    im.set_data(numpy.abs(numpy.transpose(data)))
    return [im]

def update(i):
    def to_msec(x):
        return x.seconds * 1000 + x.microseconds/1000
    time[0] = dt.now()
    elaps_rend.pop(0)
    elaps_rend.append(to_msec(time[0] - time[1]))
    g.step(i)
    time[1] = dt.now()
    elaps_gen.pop(0)
    elaps_gen.append(to_msec(time[1] - time[0]))
    data = g.get_field(2)._data
    im.set_data(numpy.abs(numpy.transpose(data)))
    v_t.set(txt.format(
        i,
        1000 / (sum(elaps_rend)/len(elaps_rend) + sum(elaps_gen)/len(elaps_gen)),
        sum(elaps_gen)/len(elaps_gen),
        sum(elaps_rend)/len(elaps_rend)
    ))
    # text0.set_text(txt.format(
    #     i,
    #     sum(elaps_gen)/len(elaps_gen),
    #     sum(elaps_rend)/len(elaps_rend),
    #     1000 / (sum(elaps_rend)/len(elaps_rend) + sum(elaps_gen)/len(elaps_gen))
    # ))
    # return [im, text0]
    return [im]

anim = animation.FuncAnimation(
    fig,
    update,
    init_func=init,
    frames=100,
    repeat=False,
    interval=int(1000/30),
    blit=False
)

plt.show()
