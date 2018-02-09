import numpy

class PassiveMaterial(object):
    def __init__(self, n, bleft=None, tright=None):
        self.n = n
        self.region = (slice(bleft[0], tright[0]), slice(bleft[1], tright[1]))

    def build(self):
        return  self.n * numpy.ones((self.region[0][1] - self.region[0][0],
                                     self.region[1][1] - self.region[1][0]))