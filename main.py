import matplotlib.backends.backend_tkagg as mpltk
import matplotlib.figure
import numpy
import tkinter as tk
# import matplotlib.ticker

class Interface(tk.Tk):
    CON = 2.54
    def __init__(self):
        super().__init__()
        self.title("FDTD - PoC")
        fdtd = FDTD(matplotlib.figure.Figure(figsize=(13/self.CON,10/self.CON), dpi=100),
                    master=self)
        fdtd.show()
        fdtd.get_tk_widget().pack()

class FDTD(mpltk.FigureCanvasTkAgg):
    def __init__(self, figure, master=None):
        super().__init__(figure, master)
        lims = {'x':(-0.5, 9.5), 'y':(-0.5, 9.5)}
        ax_im = figure.add_axes([0.05,0.05,0.90,0.90], frameon=False, aspect='equal', anchor='W')
        ax_im.set_xlim(lims['x'])
        ax_im.set_ylim(lims['y'])
        ax_im.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

        ax_cbar = figure.add_axes([0.78,0.05,0.05,0.9])
        ax_cbar.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

        im = ax_im.imshow(numpy.zeros((100,100)))
        cbar = figure.colorbar(im, cax=ax_cbar)
        cbar.outline.set_visible(False)
        cbar.ax.tick_params(right=False, labelsize=16)
        ticks = cbar.get_ticks()
        cbar.set_ticks([ticks[0],ticks[-1]])
        cbar.set_label("E field", labelpad=-15, family='DejaVu Sans', fontsize=16)

if __name__ == '__main__':
    root = Interface()
    root.mainloop()
