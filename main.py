from engine.solver import Grid
import engine.boundaries as boundaries
import matplotlib.backends.backend_tkagg as mpltk
import matplotlib.figure
import numpy
import tkinter as tk
from tkinter.ttk import Labelframe, Label, Frame, Entry, OptionMenu
# import matplotlib.ticker

class Interface(tk.Tk):
    CON = 2.54
    boundary_list = {'ABC': boundaries.ABC, 'PEC': boundaries.PEC}
    def __init__(self):
        super().__init__()
        self.title("FDTD - PoC")
        self.configure(background='#FFF')

        self.grid = Grid(500, 500, dx=10e-9)

        self.top_frame()
        self.main_animation()
        self.side_panel()

    def side_panel(self):
        rightpanel = Frame(self, width=200, height=200,borderwidth=1, relief=tk.RAISED)
        rightpanel.grid(column=1,row=0,rowspan=2,sticky=tk.N)
        bounds = Labelframe(rightpanel, borderwidth=3, padding=5, text="Boundary conditions")
        bounds.grid(row=0, column=0)

        self.north = tk.StringVar(value="PEC")
        self.east = tk.StringVar(value="PEC")
        self.south = tk.StringVar(value="PEC")
        self.west = tk.StringVar(value="PEC")
        Label(bounds, text="N", padding=5).grid(row=0, column=1, columnspan=2)
        Label(bounds, text="W", padding=5).grid(row=2, column=0)
        Label(bounds, text="E", padding=5).grid(row=2, column=3)
        Label(bounds, text="S", padding=5).grid(row=4, column=1, columnspan=2)
        OptionMenu(bounds, self.north, "PEC", *self.boundary_list.keys()).grid(row=1,column=1,columnspan=2)
        OptionMenu(bounds, self.west, "PEC", *self.boundary_list.keys()).grid(row=2,column=1,columnspan=1)
        OptionMenu(bounds, self.east, "PEC", *self.boundary_list.keys()).grid(row=2,column=2,columnspan=1)
        OptionMenu(bounds, self.south, "PEC", *self.boundary_list.keys()).grid(row=3,column=1,columnspan=2)

    def top_frame(self):
        okayInteger = self.register(self.is_integer)
        okayFloat = self.register(self.is_float)

        grid_options = Labelframe(self, borderwidth=3, padding=5, text="Grid options")
        grid_options.grid(row=0, column=0)

        grid_options.columnconfigure(0, pad=5)
        grid_options.columnconfigure(1, pad=5)
        grid_options.columnconfigure(4, pad=5)

        self.Nx = tk.StringVar(value=self.grid.shape[0])
        self.Nx.trace("w", lambda *args: self.set_grid_parameter(Nx=self.Nx.get()))
        self.Ny = tk.StringVar(value=self.grid.shape[1])
        self.Ny.trace("w", lambda *args: self.set_grid_parameter(Ny=self.Ny.get()))
        self.dx = tk.StringVar(value="{}".format(self.grid.dx * 1e9))
        self.dx.trace("w", lambda *args: self.set_grid_parameter(dx=self.dx.get()))
        self.Nxf = tk.StringVar(value="({:.2f} μm)".format(self.grid.shape[0] * self.grid.dx * 1e6))
        self.Nyf = tk.StringVar(value="({:.2f} μm)".format(self.grid.shape[1] * self.grid.dx * 1e6))
        self.dt = tk.StringVar(value="{:.4f}".format(self.grid.dt * 1e15))

        Label(grid_options, text="Cells along x").grid(column=0, row=0)
        Label(grid_options, text="Cells along y").grid(column=0, row=1)
        Label(grid_options, textvariable=self.Nxf, width=10).grid(column=2, row=0)
        Label(grid_options, textvariable=self.Nyf, width=10).grid(column=2, row=1)
        Label(grid_options, text="Mesh size dx (nm)").grid(column=3, row=0)
        Label(grid_options, text="Time step (fs)").grid(column=3, row=1, sticky=tk.E)

        Entry(grid_options, textvariable=self.Nx, width=6, justify=tk.RIGHT,
              validate='key', validatecommand=(okayInteger, '%P')).grid(column=1, row=0)
        Entry(grid_options, textvariable=self.Ny, width=6, justify=tk.RIGHT,
              validate='key', validatecommand=(okayInteger, '%P')).grid(column=1, row=1)
        Entry(grid_options, textvariable=self.dx, width=10, justify=tk.RIGHT,
              validate='key', validatecommand=(okayFloat, '%P')).grid(column=4, row=0)
        Entry(grid_options, textvariable=self.dt, width=10,
              state='disabled', justify=tk.RIGHT).grid(column=4, row=1)

    def set_boundary(self, **kwargs):
        self.grid.set_boundaries(**kwargs)
        # TODO: some kind of visual feedback on top of the plot

    def set_grid_parameter(self, **kwargs):
        for k, v in kwargs.items():
            if k == "dx":
                v = float(v) * 1e-9
            setattr(self.grid, k, v)

        print(self.grid.shape, self.grid.dx, self.grid.dt)
        self.Nxf.set("({:.2f} μm)".format(self.grid.shape[0] * self.grid.dx * 1e6))
        self.Nyf.set("({:.2f} μm)".format(self.grid.shape[1] * self.grid.dx * 1e6))
        self.dt.set("{:.4f}".format(self.grid.dt * 1e15))


    def main_animation(self):
        fdtd = FDTD(matplotlib.figure.Figure(figsize=(13/self.CON,10/self.CON), dpi=100),
                    master=self)
        fdtd.show()
        fdtd.get_tk_widget().grid(row=1, column=0)

    def is_integer(self, val):
        try:
            int(val)
        except ValueError:
            return False
        else:
            return True

    def is_float(self, val):
        try:
            float(val)
        except ValueError:
            return False
        else:
            return True


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
    s = tk.ttk.Style()
    s.theme_use('classic')
    s.configure('TFrame', background='#FFF')
    s.configure('TLabelframe', background='#FFF')
    s.configure('TLabelframe.Label', background='#FFF')
    s.configure('TLabel', background='#FFF')
    root.mainloop()
