############################################################
# Main classes for the FDTD solver classes                 #
#                                                          #
############################################################
#           Copyright (c) 2018 Stefano Guazzotti           #
############################################################

import numpy
from engine.boundaries import PEC

class Grid(object):
    """
    Main class to store a simulated system.
    """
    comps = 'xyz'
    sides = {'x': 1, 'y': 0}
    c = 299792458
    C = 1 / numpy.math.sqrt(2)
    Z0 = 377.0
    dx = 10e-9
    dt = -1

    def __init__(self, sizex=101, sizey=101, **kwargs):
        """
        Initialize all essential components for a simulation on a (sizex x sizey) grid. This is the
        size for the z component of the field. The x (y) component has sizex - 1 (sizey - 1) points
        in the x (y) direction.
        :param sizex: number of mesh points along x
        :param sizey: number of mesh points along y
        """
        self.shape = (sizex, sizey)

        self.sources = []

        self.bounds = {}

        for k,v in kwargs.items():
            if k in ['xm', 'yp', 'xp', 'ym']:
                self.bounds[k] = v

        self.build_callbacks = []

        self.pre_e = {}
        self.post_e = {}
        self.pre_h = {}
        self.post_h = {}

    def __repr__(self):
        return "{}(sizex={}, sizey={})".format("Grid", self.shape[0], self.shape[1])

    def register_build_callback(self, func):
        self.build_callbacks.append(func)

    def register_step_callback(self, time, field, func, priority=0):
        assert time.lower() in ["pre", "post"]
        assert field.lower() in "he" and len(field) == 1

        cbs = getattr(self, '_'.join([time, field]))
        if priority in cbs.keys():
            cbs[priority].append(func)
        else:
            cbs[priority] = [func]

    def get_field(self, comp):
        """
        Returns field along direction comp.
        :param comp: component of the field. Numbered from 0 or using 'xyz'
        :return: FDTDPoC.engine.solver.Field object
        """
        try:
            return getattr(self, "_F" + self.comps[comp])
        except TypeError:
            return getattr(self, "_F" + comp)

    def set_boundaries(self, **kwargs):
        for k, v in kwargs.items():
            self.bounds[k] = v

    def build(self):
        if len(self.bounds) != 4:
            raise Exception("Grid should have one boundary defined for every side")

        shape_x = (self.shape[0], self.shape[1] - 1)
        shape_y = (self.shape[0] - 1, self.shape[1])

        # z component of the field. For TE this is an electric field
        self._Fz = Field(self.shape, field="E", comp=2, bounds=self.bounds)
        # x,y components of the field. These are magnetic fields
        self._Fx = Field(shape_x, field="H", comp=0)
        self._Fy = Field(shape_y, field="H", comp=1)

        for side, bound in self.bounds.items():
            bound(self, side)

        for func in self.build_callbacks:
            func(self)

        self.time = 0
        self._built = True
        self.step = self.__step

    def __step(self, t):
        """
        Perform one FDTD step, i.e., one electric field update and one magnetic field update on
        the whole grid
        :param t: index of the step
        :param src: a tuple indicating position and field for the source
        :return: NoneType
        """
        self.time = t

        for priority in sorted(self.pre_h.keys(), reverse=True):
            for callback in self.pre_h[priority]:
                callback(t)

        self._Fx.step(t, self._Fz)
        self._Fy.step(t, self._Fz)

        for priority in sorted(self.post_h.keys(), reverse=True):
            for callback in self.post_h[priority]:
                callback(t)

        for priority in sorted(self.pre_e.keys(), reverse=True):
            for callback in self.pre_e[priority]:
                callback(t)

        self._Fz.step(t, self._Fx, self._Fy)

        for priority in sorted(self.post_e.keys(), reverse=True):
            for callback in self.post_e[priority]:
                callback(t)

        return


class Field(object):
    """
    Class that represents a single field component over the whole grid or a subset of it
    # TODO next clean up :)
    """
    def __init__(self, shape, field, comp, bounds=None):
        """
        Create an object representing a field component over the grid or a subset of the grid
        :param shape: tuple representing the number of points along x and y
        :param field: electric or magnetic field
        :param comp: x, y, or z component
        :param bounds: dictionary of boundaries on the four edges
        """
        self._shape = shape
        self._field = field
        self._comp = comp
        self._bounds = bounds
        self._data = numpy.zeros(self._shape, dtype="double")

    def step(self, i, *other):
        """
        Do a single step for one of the field components over the whole grid
        :param i: step index
        :param other: set of neighbouring fields
        :return: NoneType
        """
        if self._comp == 0:
            self._data -= Grid.C / Grid.Z0 * (other[0]._data[:,1:] - other[0]._data[:,:-1])
        elif self._comp == 1:
            self._data += Grid.C / Grid.Z0 * (other[0]._data[1:,:] - other[0]._data[:-1,:])
        elif self._comp == 2:
            self._data[1:-1, 1:-1] += (
                    - Grid.C * Grid.Z0 * (other[0]._data[1:-1, 1:] - other[0]._data[1:-1, :-1])
                    + Grid.C * Grid.Z0 * (other[1]._data[1:, 1:-1] - other[1]._data[:-1, 1:-1])
            )
        return
