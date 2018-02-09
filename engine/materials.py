import numpy

class PassiveMaterial(object):
    def __init__(self, n, bleft, tright):
        self.n = n
        self.region = (slice(bleft[0], tright[0]+1), slice(bleft[1], tright[1]+1))

    def build(self):
        return self.n**2 * numpy.ones((self.region[0].stop - self.region[0].start,
                                     self.region[1].stop - self.region[1].start))

class DrudeMaterial(object):
    def __init__(self, omegap, gamma, epsinf):
        # TODO: the units really need fixing
        self.omegap = omegap
        self.gamma = gamma
        self.epsinf = epsinf
        self._regions = []

    def add_region(self, bleft, tright, grid):
        self._regions.append((
            slice(bleft[0], tright[0]+1), slice(bleft[1], tright[1]+1)
        ))
        grid.add_passive_material(PassiveMaterial(numpy.math.sqrt(self.epsinf), bleft, tright))

    def build(self, grid):
        if not self._regions:
            raise Exception("Material {} is not associated with any region".format(self))
        self._fields = [grid.get_field('z')._data[reg] for reg in self._regions]
        self._current = [numpy.zeros_like(f) for f in self._fields]
        self.A = (2 - self.gamma*grid.dt) / (2 + self.gamma*grid.dt)
        eps0 = 1 # TODO: change ;)
        self.B = 2 * eps0 * grid.dt / (2 + self.gamma*grid.dt) * self.omegap**2

    def update_current(self):
        # TODO: test that values are correctly passed as VALUES
        for curr, field in zip(self._current, self._fields):
            curr[:,:] = self.A * curr + self.B * field

    def update_field(self):
        for field, curr in zip(self._fields, self._current):
            field[:,:] -= curr

