import numpy

class PassiveMaterial(object):
    def __init__(self, n, bleft, tright):
        self.n = n
        self.region = (slice(bleft[0], tright[0]+1), slice(bleft[1], tright[1]+1))

    def build(self):
        return  self.n**2 * numpy.ones((self.region[0].stop - self.region[0].start,
                                     self.region[1].stop - self.region[1].start))
