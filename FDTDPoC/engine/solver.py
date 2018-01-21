############################################################
# Main classes for the FDTDPoC solver classes                 #
#                                                          #
############################################################
#           Copyright (c) 2018 Stefano Guazzotti           #
############################################################

import numpy


class Grid(object):
    """
    Main class to store a simulated system.
    """
    comps = 'xyz'
    C = 1 / numpy.math.sqrt(2)

    def __init__(self, sizex=101, sizey=101):
        """
        Initialize all essential components for a simulation on a (sizex x sizey) grid. This is the
        size for the z component of the field. The x (y) component has sizex - 1 (sizey - 1) points
        in the x (y) direction.
        :param sizex: number of mesh points along x
        :param sizey: number of mesh points along y
        """
        self._time = 0
        self._shape = (sizex, sizey)
        self._shape_x = (sizex, sizey - 1)
        self._shape_y = (sizex - 1, sizey)

        # z component of the field. For TE this is an electric field
        self._Fz = Field(self._shape, field="E", comp=2)
        # x,y components of the field. These are magnetic fields
        self._Fx = Field(self._shape_x, field="H", comp=0)
        self._Fy = Field(self._shape_y, field="H", comp=1)

    def __repr__(self):
        return "{}(sizex={}, sizey={})".format("Grid", self._shape[0], self._shape[1])

    def get_size(self):
        """
        Get grid size as a tuple
        :return: (int, int)
        """
        return self._shape

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

    def step(self, i, src=(1, 1, 0)):
        """
        Perform one FDTDPoC step, i.e., one electric field update and one magnetic field update on the
        whole grid
        :param i: index of the step
        :param src: a tuple indicating position and field for the source
        :return: NoneType
        """
        self._time = i
        self._Fx.step(i, self._Fz)
        self._Fy.step(i, self._Fz)
        self._Fz.step(i, self._Fx, self._Fy)

        self._Fz._data[src[0],src[1]] += src[2]
        return


class Field(object):
    """
    Class that represents a single field component over the whole grid or a subset of it
    """
    def __init__(self, shape, field, comp):
        """
        Create an object representing a field component over the grid or a subset of the grid
        :param shape: tuple representing the number of points along x and y
        :param field: electric or magnetic field
        :param comp: x, y, or z component
        """
        self._shape = shape
        self._field = field
        self._comp = comp
        self._data = numpy.zeros(self._shape, dtype="double")

    def step(self, i, *other):
        """
        Do a single step for one of the field components over the whole grid
        :param i: step index
        :param other: set of neighbouring fields
        :return: NoneType
        """
        if self._comp == 0:
            self._data = self._data - Grid.C * (other[0]._data[:,1:] - other[0]._data[:,:-1])
        elif self._comp == 1:
            self._data = self._data + Grid.C * (other[0]._data[1:,:] - other[0]._data[:-1,:])
        elif self._comp == 2:
            self._data[1:-1, 1:-1] = self._data[1:-1, 1:-1] + (
                - Grid.C * (other[0]._data[1:-1, 1:] - other[0]._data[1:-1, :-1])
                + Grid.C * (other[1]._data[1:, 1:-1] - other[1]._data[:-1, 1:-1])
            )
        return
