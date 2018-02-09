import numpy

class PassiveMaterial(object):
    def __init__(self, n, bleft, tright):
        self.n = n
        self.region = (slice(bleft[0], tright[0]), slice(bleft[1], tright[1]))

    def build(self):
        return  self.n * numpy.ones((self.region[0][1] - self.region[0][0] + 1,
                                     self.region[1][1] - self.region[1][0] + 1))
