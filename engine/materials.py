import numpy

class PassiveMaterial(object):
    def __init__(self, bleft, tright, n):
        self.w = tright[0] - bleft[0]
        self.h = tright[1] - bleft[1]
        self.n = n
    def __call__(self):
        return numpy.ones((self.w,self.h)) * self.n