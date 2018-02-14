from engine.solver import Grid
import engine.boundaries as boundaries
import matplotlib.backends.backend_tkagg as mpltk
import matplotlib.figure
import matplotlib.patches
import matplotlib.text
import numpy
import tkinter as tk
from tkinter.ttk import Labelframe, Label, Frame, Entry, OptionMenu, Button, Checkbutton

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

        Button(self, text="DEBUG!", command=self.debug).grid(column=0, row=3)

    def side_panel(self):
        rightpanel = Frame(self, borderwidth=1, relief=tk.RAISED)
        rightpanel.grid(column=1,row=0,rowspan=2,sticky=tk.N)
        bounds = Labelframe(rightpanel, borderwidth=3, padding=5, text="Boundary conditions")
        bounds.pack(fill=tk.X)

        frame = Frame(bounds)
        frame.pack()

        self.north = tk.StringVar(value="PEC")
        self.north.trace('w', lambda *args: self.set_boundary(yp=self.north.get()))
        self.east = tk.StringVar(value="PEC")
        self.east.trace('w', lambda *args: self.set_boundary(xp=self.east.get()))
        self.south = tk.StringVar(value="PEC")
        self.south.trace('w', lambda *args: self.set_boundary(ym=self.south.get()))
        self.west = tk.StringVar(value="PEC")
        self.west.trace('w', lambda *args: self.set_boundary(xm=self.west.get()))
        Label(frame, text="N", padding=5).grid(row=0, column=1, columnspan=2)
        Label(frame, text="W", padding=5).grid(row=2, column=0)
        Label(frame, text="E", padding=5).grid(row=2, column=3)
        Label(frame, text="S", padding=5).grid(row=4, column=1, columnspan=2)
        OptionMenu(frame, self.north, "PEC", *self.boundary_list.keys()).grid(row=1,column=1,columnspan=2)
        OptionMenu(frame, self.west, "PEC", *self.boundary_list.keys()).grid(row=2,column=1,columnspan=1)
        OptionMenu(frame, self.east, "PEC", *self.boundary_list.keys()).grid(row=2,column=2,columnspan=1)
        OptionMenu(frame, self.south, "PEC", *self.boundary_list.keys()).grid(row=3,column=1,columnspan=2)

        TFSF = Labelframe(rightpanel, borderwidth=3, padding=5, text="TFSF source")
        TFSF.pack()

        self.TFSF_on = tk.IntVar()
        self.TFSF_on.trace("w", lambda *args: self.TFSF_toggle(self.TFSF_on.get()))
        cb = Checkbutton(TFSF, variable=self.TFSF_on, text="Enable TFSF")
        cb.pack(side=tk.TOP, fill=tk.X)

        self.TFSF_options = Frame(TFSF)
        self.TFSF_options.pack(side=tk.TOP, fill=tk.X)

        okayInteger = self.register(self.is_integer)
        self.bleftx = tk.StringVar(value=20)
        self.blefty = tk.StringVar(value=20)
        self.trightx = tk.StringVar(value=20)
        self.trighty = tk.StringVar(value=20)
        Label(self.TFSF_options, text="Lower left corner").grid(row=0, column=0, padx=5, pady=3, columnspan=2)
        Entry(self.TFSF_options, textvariable=self.bleftx, width=6, justify=tk.RIGHT,
              validate='key', validatecommand=(okayInteger, '%P')).grid(column=0, row=1, pady=3, columnspan=2)
        Entry(self.TFSF_options, textvariable=self.blefty, width=6, justify=tk.RIGHT,
              validate='key', validatecommand=(okayInteger, '%P')).grid(column=0, row=2, pady=3, columnspan=2)
        Label(self.TFSF_options, text="Upper right corner").grid(row=0, column=2, padx=5, pady=3, columnspan=2)
        Entry(self.TFSF_options, textvariable=self.trightx, width=6, justify=tk.RIGHT,
              validate='key', validatecommand=(okayInteger, '%P')).grid(column=2, row=1, pady=3, columnspan=2)
        Entry(self.TFSF_options, textvariable=self.trighty, width=6, justify=tk.RIGHT,
              validate='key', validatecommand=(okayInteger, '%P')).grid(column=2, row=2, pady=3, columnspan=2)

        self.TFSF_E0 = tk.StringVar(value=1)
        self.TFSF_omega = tk.StringVar(value="{:.2e}".format(1.2e15))
        self.TFSF_tau = tk.StringVar(value=10e-15)
        self.TFSF_mu = tk.StringVar(value=30e-15)
        Label(self.TFSF_options, text="E₀").grid(row=3, column=0)
        Label(self.TFSF_options, text="ω").grid(row=4, column=0)
        Label(self.TFSF_options, text="τ").grid(row=3, column=2)
        Label(self.TFSF_options, text="μ").grid(row=4, column=2)
        Entry(self.TFSF_options, textvariable=self.TFSF_E0, width=8, justify=tk.RIGHT).grid(column=1, row=3, pady=3, padx=4)
        Entry(self.TFSF_options, textvariable=self.TFSF_omega, width=8, justify=tk.RIGHT).grid(column=1, row=4, pady=3, padx=4)
        Entry(self.TFSF_options, textvariable=self.TFSF_tau, width=8, justify=tk.RIGHT).grid(column=3, row=3, pady=3, padx=4)
        Entry(self.TFSF_options, textvariable=self.TFSF_mu, width=8, justify=tk.RIGHT).grid(column=3, row=4, pady=3, padx=4)

        self.TFSF_on.set(0)

        rightpanel = Frame(self, borderwidth=1, relief=tk.RAISED)
        rightpanel.grid(column=2,row=0,rowspan=2,sticky=tk.N, padx=10)
        dipoles = Labelframe(rightpanel, borderwidth=3, padding=5, text="Point sources")
        dipoles.pack(side=tk.TOP, fill=tk.X)

        self.dipole = [
            tk.StringVar(value=0),
            tk.StringVar(value=0),
            tk.StringVar(value=0),
            tk.StringVar(value=0),
            tk.StringVar(value=0),
            tk.StringVar(value=0)
        ]

        self.sources = tk.StringVar(value='New...')
        self.dipolar_sources = {}

        lb = tk.Listbox(dipoles, listvariable=self.sources, width=20)
        lb.grid(row=0, column=0, columnspan=4)
        lb.bind("<<ListboxSelect>>", lambda *args: self.dipole_select(lb))
        Label(dipoles, text="X₀").grid(row=1, column=0)
        Label(dipoles, text="Y₀").grid(row=1, column=2)
        Label(dipoles, text="E₀").grid(row=2, column=0)
        Label(dipoles, text="ω").grid(row=3, column=0)
        Label(dipoles, text="τ").grid(row=2, column=2)
        Label(dipoles, text="μ").grid(row=3, column=2)
        self.dipole_fields = []
        tmp = Entry(dipoles, textvariable=self.dipole[0], width=8, justify=tk.RIGHT, state="disabled",
              validate='key', validatecommand=(okayInteger, '%P'))
        tmp.grid(column=1, row=1, pady=3, padx=4)
        self.dipole_fields.append(tmp)
        tmp = Entry(dipoles, textvariable=self.dipole[1], width=8, justify=tk.RIGHT, state="disabled",
              validate='key', validatecommand=(okayInteger, '%P'))
        tmp.grid(column=3, row=1, pady=3, padx=4)
        self.dipole_fields.append(tmp)
        tmp = Entry(dipoles, textvariable=self.dipole[2], width=8, state="disabled",
              justify=tk.RIGHT)
        tmp.grid(column=1, row=2, pady=3, padx=4)
        self.dipole_fields.append(tmp)
        tmp = Entry(dipoles, textvariable=self.dipole[3], width=8, state="disabled",
              justify=tk.RIGHT)
        tmp.grid(column=1, row=3, pady=3, padx=4)
        self.dipole_fields.append(tmp)
        tmp = Entry(dipoles, textvariable=self.dipole[4], width=8, state="disabled",
              justify=tk.RIGHT)
        tmp.grid(column=3, row=2, pady=3, padx=4)
        self.dipole_fields.append(tmp)
        tmp = Entry(dipoles, textvariable=self.dipole[5], width=8, state="disabled",
              justify=tk.RIGHT)
        tmp.grid(column=3, row=3, pady=3, padx=4)
        self.dipole_fields.append(tmp)
        self.cds = Button(dipoles, text="Create source", state="disabled", command=lambda: self.save_source(lb))
        self.cds.grid(column=0, row=4, columnspan=2)
        self.rds = Button(dipoles, text="Remove source", state="disabled", command=lambda: self.remove_source(lb))
        self.rds.grid(column=2, row=4, columnspan=2)

        materials = Labelframe(self, text="Refractive index materials")
        materials.grid(column=1,row=2,rowspan=2, columnspan=2,sticky=tk.N, padx=10)
        Label(materials, text="Refractive index materials").pack()

    def top_frame(self):
        okayInteger = self.register(self.is_integer)
        okayFloat = self.register(self.is_float)

        grid_options = Labelframe(self, borderwidth=3, padding=5, text="Grid options")
        grid_options.grid(row=0, column=0)

        grid_options.columnconfigure(0, pad=5)
        grid_options.columnconfigure(1, pad=5)
        grid_options.columnconfigure(4, pad=5)

        self.Nx = tk.StringVar(value=self.grid.shape[0])
        self.Ny = tk.StringVar(value=self.grid.shape[1])
        self.dx = tk.StringVar(value="{}".format(self.grid.dx * 1e9))
        self.Nxf = tk.StringVar(value="({:.2f} μm)".format(self.grid.shape[0] * self.grid.dx * 1e6))
        self.Nyf = tk.StringVar(value="({:.2f} μm)".format(self.grid.shape[1] * self.grid.dx * 1e6))
        self.dt = tk.StringVar(value="{:.4f}".format(self.grid.dt * 1e15))

        self.Nx.trace("w", lambda *args: self.set_Nx(self.Nx.get()))
        self.Ny.trace("w", lambda *args: self.set_Ny(self.Ny.get()))
        self.dx.trace("w", lambda *args: self.set_dx(self.dx.get()))

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
        for k, v in kwargs.items():
            self.grid.set_boundaries(**{k:self.boundary_list[v]})
            # print(k, v, self.boundary_list[v])
            self.fdtd.update_boundary(k, v)

    def set_Nx(self, value):
        self.grid.Nx = value
        self.Nxf.set("({:.2f} μm)".format(self.grid.Nx * self.grid.dx * 1e6))
        self.fdtd.update_size(self.grid.shape)

    def set_Ny(self, value):
        self.grid.Ny = value
        self.Nyf.set("({:.2f} μm)".format(self.grid.Ny * self.grid.dx * 1e6))
        self.fdtd.update_size(self.grid.shape)

    def set_dx(self, value):
        value = float(value) * 1e-9
        self.grid.dx = value
        self.dt.set("{:.4f}".format(self.grid.dt * 1e15))

    def main_animation(self):
        self.fdtd = FDTD(matplotlib.figure.Figure(figsize=(13/self.CON,10/self.CON), dpi=100),
                    master=self)
        self.fdtd.show()
        self.fdtd.get_tk_widget().grid(row=1, column=0, rowspan=2)

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

    def TFSF_toggle(self, flag):
        if bool(flag):
            for child in self.TFSF_options.winfo_children():
                if child.winfo_class() != "TLabel":
                    child.configure(state="normal")
        else:
            for child in self.TFSF_options.winfo_children():
                if child.winfo_class() != "TLabel":
                    child.configure(state="disabled")

    def dipole_select(self, listbox):
        if listbox.get(listbox.curselection()) == "New...":
            for f in self.dipole_fields:
                f.configure(state="normal")
            self.cds.configure(text="Create source", state="normal")
            self.rds.configure(state="disabled")
            for txt in self.dipole:
                txt.set("0")
        else:
            act = listbox.get(listbox.curselection()).split(",")
            self.cds.configure(text="Modify source")
            self.rds.configure(state="normal")
            self.dipole[0].set(act[0])
            self.dipole[1].set(act[1])
            parameters = self.dipolar_sources[(act[0], act[1])]
            for i in range(len(parameters)):
                self.dipole[2+i].set(parameters[i])

    def save_source(self, listbox):
        if listbox.get(listbox.curselection()) == "New...":
            self.dipolar_sources[(self.dipole[0].get(), self.dipole[1].get())] = [v.get() for v in self.dipole[2:]]
            listbox.insert(tk.END, "{},{}".format(self.dipole[0].get(), self.dipole[1].get()))
            for v in self.dipole:
                v.set(0)
        else:
            act = listbox.get(listbox.curselection()).split(",")
            del self.dipolar_sources[(act[0], act[1])]
            self.dipolar_sources[(self.dipole[0].get(), self.dipole[1].get())] = [v.get() for v in self.dipole[2:]]
            listbox.insert(tk.END, "{},{}".format(self.dipole[0].get(), self.dipole[1].get()))
            listbox.delete(tk.ANCHOR)
            for v in self.dipole:
                v.set(0)

    def remove_source(self, listbox):
        if listbox.get(listbox.curselection()) != "New...":
            act = listbox.get(listbox.curselection()).split(",")
            del self.dipolar_sources[(act[0], act[1])]
            listbox.delete(tk.ANCHOR)
            for v in self.dipole:
                v.set(0)
            for f in self.dipole_fields:
                f.configure(state="disabled")
            self.rds.configure(state="disabled")
            self.cds.configure(state="disabled")

    def debug(self):
        print("Grid has size {}x{}. Mesh size is {}. Time step is {}".format(*self.grid.shape, self.grid.dx, self.grid.dt))
        print("The following boundaries are defined W:{xm} N:{yp} E:{xp} S:{ym}".format(self.grid.sources, **self.grid.bounds))


class FDTD(mpltk.FigureCanvasTkAgg):
    def __init__(self, figure, master=None):
        super().__init__(figure, master)
        self.master = master
        lims = {'x':(0, 100), 'y':(0, 100)}
        self.axes = figure.add_axes([0.05, 0.05, 0.90, 0.90], frameon=False, aspect='equal', anchor='W')
        self.axes.set_xlim(lims['x'])
        self.axes.set_ylim(lims['y'])
        self.axes.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

        ax_cbar = figure.add_axes([0.78,0.05,0.05,0.9])
        ax_cbar.tick_params(bottom=False, left=False, labelbottom=False, labelleft=False)

        im = self.axes.imshow(numpy.zeros((100, 100)))
        cbar = figure.colorbar(im, cax=ax_cbar)
        cbar.outline.set_visible(False)
        cbar.ax.tick_params(right=False, labelsize=16)
        ticks = cbar.get_ticks()
        cbar.set_ticks([ticks[0],ticks[-1]])
        cbar.set_label("E field", labelpad=-15, family='DejaVu Sans', fontsize=16)

        ruler = 1e-4 / (self.master.grid.shape[0] * self.master.grid.dx)
        self.ruler = matplotlib.patches.Rectangle((8,8), ruler, 1, color="#FFFFFF")
        self.axes.add_patch(self.ruler)
        self.axes.add_artist(matplotlib.text.Text(7.5, 3.5, text="1 μm", color="#FFFFFF", ha="left"))

        self.bounds = {}
        self.bounds["xm"] = matplotlib.patches.Polygon(numpy.array([(0,0),(0,100),(5,95),(5,5)]), color="#7DC4DB", alpha=0.6)
        self.bounds["yp"] = matplotlib.patches.Polygon(numpy.array([(0,100),(100,100),(95,95),(5,95)]), color="#7DC4DB", alpha=0.6)
        self.bounds["xp"] = matplotlib.patches.Polygon(numpy.array([(100,100),(100,0),(95,5),(95,95)]), color="#7DC4DB", alpha=0.6)
        self.bounds["ym"] = matplotlib.patches.Polygon(numpy.array([(0,0),(100,0),(95,5),(5,5)]), color="#7DC4DB", alpha=0.6)

        for rect in self.bounds.values():
            self.axes.add_patch(rect)

    def update_boundary(self, side, type):
        print(side, type)
        if type == "PEC":
            self.bounds[side].set_color("#7DC4DB")
            print(type)
        if type == "ABC":
            self.bounds[side].set_color("#E3AB5D")
            print(type)
        self.draw()

    def update_size(self, shape):
        ruler = 1e-4 / (shape[0] * self.master.grid.dx)
        self.ruler.set_width(ruler)
        self.draw()

if __name__ == '__main__':
    root = Interface()
    s = tk.ttk.Style()
    s.theme_use('classic')
    s.configure('TFrame', background='#FFF')
    s.configure('TLabelframe', background='#FFF')
    s.configure('TLabelframe.Label', background='#FFF')
    s.configure('TLabel', background='#FFF')
    s.configure('TCheckbutton', background='#FFF')
    s.configure('TButton', background='#FFF')
    root.mainloop()
