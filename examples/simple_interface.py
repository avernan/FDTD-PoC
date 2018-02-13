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

def to_msec(x):
    return x.seconds * 1000 + x.microseconds/1000

class Animation(Frame):
    txt = (
        "Frame {frame:4d}", "{FPS:.1f} FPS",
        "Generation time: {gen:.2f} ms", "Rendering time: {rend:.2f} ms"
    )
    vals = {"frame":0, "FPS":0, "gen":0, "rend":0}
    def __init__(self, grid, nframes=1000):
        super().__init__()
        self.running = False
        self.elaps_gen = [0] * 50
        self.elaps_rend = [0] * 50
        self.nframes = nframes
        self.grid = grid
        self.time = [dt.now(), dt.now()]
        self.tpoints = numpy.arange(0,self.nframes,1)
        self.tdata = numpy.zeros((5,self.nframes), dtype=float) * numpy.nan

        center = numpy.array((int(grid.shape[0]/2), int(grid.shape[1]/2)), dtype=int)
        pm = numpy.array((1,-1), dtype=int)
        self.positions = (center, center + center/2, center + pm*center/2, center - center/2, center - pm*center/2)
        self.positions = tuple((tuple(numpy.int_(i)) for i in self.positions))

        self.initGUI()

    def initGUI(self):
        CON = 2.54
        self.fig = Figure(figsize=(9.5/CON, 7/CON), dpi=100)
        ax = self.fig.add_subplot(111)
        ax.set_xlim(-0.5,self.grid.shape[0]-0.5)
        ax.set_ylim(-0.5,self.grid.shape[1]-0.5)
        ax.set_aspect('equal')
        data = self.grid.get_field(2)._data
        self.im = ax.imshow(numpy.abs(numpy.transpose(data)), cmap=plt.get_cmap('inferno'),
                                 norm=SafeLogNorm(vmin=1e-5, vmax=2, clip=True))
        self.fig.colorbar(self.im, ax=ax)

        self.fig2 = Figure(figsize=(8/CON, 7/CON), dpi=100)
        ax2 = self.fig2.add_subplot(111)
        ax2.set_xlim(0, self.nframes)
        ax2.set_ylim(-0.001, 0.001)
        self.plot = ax2.plot(
            self.tpoints, self.tdata[0],
            self.tpoints, self.tdata[1],
            self.tpoints, self.tdata[2],
            self.tpoints, self.tdata[3],
            self.tpoints, self.tdata[4]
        )

        for j in range(len(self.plot)):
            ax.add_artist(plt.Rectangle(numpy.array(self.positions[j]) - numpy.array((15,15)),
                                        30, 30, color=self.plot[j].get_color(), alpha=0.4))


        self.master.title("FDTD - PoC")

        text_frame = Frame(self, relief=tk.RAISED, borderwidth=2)
        text_frame.columnconfigure(0, pad=5)
        text_frame.columnconfigure(1, pad=5)
        text_frame.rowconfigure(0, pad=5)
        text_frame.rowconfigure(1, pad=5)
        text_frame.rowconfigure(2, pad=5)

        font = Font(family="Helvetica", size=14, weight="bold")
        self.text_var = []
        self.labels = []
        for j in range(len(Animation.txt)):
            self.text_var.append(tk.StringVar())
            self.labels.append(Label(text_frame, textvariable=self.text_var[j], font=font))
            self.labels[j].grid(row=int(j/2), column=j%2, ipadx=15,ipady=1)
            self.text_var[j].set(Animation.txt[j].format(**Animation.vals))

        text_frame.pack()

        plots = Frame(self)
        self.fig_canvas = FigureCanvasTkAgg(self.fig, master=plots)
        self.fig_canvas.show()
        self.fig_canvas.get_tk_widget().pack(side=tk.LEFT)

        self.fig_canvas2 = FigureCanvasTkAgg(self.fig2, master=plots)
        self.fig_canvas2.show()
        self.fig_canvas2.get_tk_widget().pack(side=tk.LEFT)
        plots.pack()

        buttons = Frame(self)
        self.start = Button(buttons, text="Start FDTD", command=self.run)
        self.start.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.v_pause = tk.StringVar()
        self.v_pause.set("---")
        self.pause_b = Button(buttons, textvariable=self.v_pause, command=self.pause, state="disabled")
        self.pause_b.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        stop = Button(buttons, text="Stop FDTD", command=self.quit)
        stop.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        buttons.pack(side=tk.BOTTOM, fill=tk.BOTH)

        self.pack()

    def step(self,i):
        self.i = i
        self.time[0] = dt.now()
        self.elaps_rend.pop(0)
        self.elaps_rend.append(to_msec(self.time[0] - self.time[1]))
        self.grid.step(i)
        self.time[1] = dt.now()
        self.elaps_gen.pop(0)
        self.elaps_gen.append(to_msec(self.time[1] - self.time[0]))
        data = g.get_field(2)._data
        self.im.set_data(numpy.abs(numpy.transpose(data)))

        for j in range(5):
            self.tdata[j,i] = data[self.positions[j]]
            self.plot[j].set_ydata(self.tdata[j])

        try:
            lim = numpy.abs(self.tdata[:,:i]).max()
        except ValueError:
            lim = 0.001

        if lim >= 0.001:
            self.plot[0].axes.set_ylim((-lim,lim))

        self.fig_canvas2.draw()

        Animation.vals["frame"] = i
        Animation.vals["gen"] = sum(self.elaps_gen)/len(self.elaps_gen)
        Animation.vals["rend"] = sum(self.elaps_rend)/len(self.elaps_rend)
        Animation.vals["FPS"] = 1000 / (Animation.vals["gen"] + Animation.vals["rend"])
        Animation.vals["fM"] = data.max()
        Animation.vals["fm"] = data.min()

        for var, txt in zip(self.text_var, Animation.txt):
            var.set(txt.format(**Animation.vals))

    def run(self):
        if not self.running:
            self.anim = animation.FuncAnimation(
                self.fig, self.step, frames=self.nframes,
                repeat=False, interval=int(1000/30), blit=False
            )
            self.fig_canvas.draw()
            self.running = True
            self.start.config(state="disabled")
            self.pause_b.config(state="normal")
            self.v_pause.set("Pause")

    def quit(self):
        self.anim.event_source.stop()
        super().quit()

    def pause(self):
        if self.running:
            self.anim.event_source.stop()
            self.v_pause.set("Resume")
            self.running = False
        else:
            self.anim.event_source.start()
            self.v_pause.set("Pause")
            self.running = True

if __name__ == '__main__':
    # Define grid size
    shape = numpy.array((800, 800))
    g = FDTD.Grid(*shape)

    # Add sources
    # In this case a set of 5 randomised dipolar sources
    nsources = 5
    for i in range(nsources):
        parms = numpy.random.random(6)
        sources.SourceDipole(g, (int(parms[0]*shape[0]), int(parms[1]*shape[1])),
                             sources.PulseGaussian(10 * (1 - 0.5*parms[2]),
                                                   10e-15 * (1 - 0.5*parms[3]),
                                                   2e-15 * (1 - 0.5*parms[4]),
                                                   1.8e15 * (1 - 0.5*parms[5])))

    # Set boundary conditions
    # Here absorbing boundaries to simulate an open system
    g.set_boundaries(xm=bounds.ABC, xp=bounds.ABC, ym=bounds.ABC, yp=bounds.ABC)

    # Build and validate the FDTD setup
    g.build()

    # Run simulation and animation for nstep steps
    nsteps = 2000

    root = tk.Tk()
    anim = Animation(g, nsteps)
    root.mainloop()
