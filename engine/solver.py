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
    sides = {'x': 1, 'y': 0}
    C = 1 / numpy.math.sqrt(2)
    Z0 = 377.0

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
        self._sources = []
        self._bounds = {}
        self._materials = []
        self._passive_materials = []

        self._epsr = numpy.ones(self._shape)

        # z component of the field. For TE this is an electric field
        self._Fz = Field(self._shape, field="E", comp=2, bounds=self._bounds)
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

    def add_source(self, source):
        """
        Add a source to the simulation
        :param source: object of type source
        :return: NoneType
        """
        self._sources.append(source)
        return

    def add_passive_material(self, material):
        """
        Add a passive material to a region of the simulation
        """
        for mat in self._materials + self._passive_materials:
            if mat.overlap(material):
                raise Exception("Error: detected overlap of materials when adding {}".format(material))
        self._passive_materials.append(material)
        self._epsr[material.region] = material.build()

    def add_material(self, material, bleft, tright):
        for mat in self._materials + self._passive_materials:
            if mat.overlap(material):
                raise Exception("Error: detected overlap of materials when adding {}".format(material))
        if material in self._materials:
            material.add_region(bleft, tright, self)
        else:
            self._materials.append(material)
            material.add_region(bleft, tright, self)

    def set_boundaries(self, **kwargs):
        # TODO: cleaner implementation required:
        #   * this should only transpose and/or reverse arrays as different boundary types may require different number
        #   of layers
        #   * the dictionary implementation is confusing and difficult to handle/expand
        for k, v in kwargs.items():
            self._bounds[k] = v.build_boundary(
                **{
                    'xm': {'size': self._shape[1], 'field': self._Fz._data[0:3,:]},
                    'xp': {'size': self._shape[1], 'field': self._Fz._data[-1:-4:-1,:]},
                    'ym': {'size': self._shape[0], 'field': numpy.transpose(self._Fz._data[:,0:3])},
                    'yp': {'size': self._shape[0], 'field': numpy.transpose(self._Fz._data[:,-1:-4:-1])}
                }[k]
            )

    def build(self):
        if len(self._bounds) != 4:
            raise Exception("Grid should have one boundary defined for every side")
        self._built = True
        self.step = self.__step
        for mat in self._materials:
            mat.build(self)

    def __step(self, t):
        """
        Perform one FDTD step, i.e., one electric field update and one magnetic field update on
        the whole grid
        :param t: index of the step
        :param src: a tuple indicating position and field for the source
        :return: NoneType
        """
        self._time = t
        self._Fx.step(t, self._Fz)
        self._Fy.step(t, self._Fz)
        # Plane wave sources automatically update the relevant fields
        for src in self._sources:
            src.update(t)
        for mat in self._materials:
            mat.update_current()
        self._Fz.step(t, self._Fx, self._Fy, self._epsr)
        for mat in self._materials:
            mat.update_field()

        # Point source have to be manually applied
        for src in self._sources:
            self._Fz._data[src.get_position()] += src(t)

        return


class Field(object):
    """
    Class that represents a single field component over the whole grid or a subset of it
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
                    - Grid.C * Grid.Z0 * (other[0]._data[1:-1, 1:] - other[0]._data[1:-1, :-1]) / other[2][1:-1,1:-1]
                    + Grid.C * Grid.Z0 * (other[1]._data[1:, 1:-1] - other[1]._data[:-1, 1:-1]) / other[2][1:-1,1:-1]
            )
            self._data[0,:] = self._bounds['xm']()
            self._data[-1,:] = self._bounds['xp']()
            self._data[:,0] = self._bounds['ym']()
            self._data[:,-1] = self._bounds['yp']()
        return
