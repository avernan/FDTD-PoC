import numpy

class PassiveMaterial(object):
    def __init__(self, grid, n, bleft, tright):
        self.n = n
        self.bleft = bleft
        self.tright = tright
        grid.add_passive_material(self)
        grid.register_build_callback(self.build)

    def build(self, grid):
        regionx = slice(self.bleft[0], self.tright[0]+1)
        regiony = slice(self.bleft[1], self.tright[1]+1)
        grid._epsr[regionx,regiony] = (self.n**2 * numpy.ones((
            regionx.stop - regionx.start,
            regiony.stop - regiony.start
        )))

    def overlap(self, other):
        if self.bleft[0] > other.tright[0] or other.bleft[0] > self.tright[0]:
            return False

        if self.bleft[1] > other.tright[1] or other.bleft[1] > self.tright[1]:
            return False

        return True
