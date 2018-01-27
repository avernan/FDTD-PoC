import numpy
from engine.solver import Grid

class Boundary(object):
    def __init__(self):
        pass

    def build_boundary(self, **kwargs):
        return self

    def __call__(self, *args):
        raise NotImplementedError

class PEC(Boundary):
    """
    Perfect Electric Conductor (PEC) boundary.
    Perfectly reflecting boundary obtained by forcing the terminating E node to zero
    """
    def __call__(self, *args):
        return 0

class ABC(Boundary):
    """
    Differential equation based absorbing boundary conditions (ABC)
    cf. http://www.eecs.wsu.edu/~schneidj/ufdtd/chap6.pdf eq. 6.32-33
    """
    def __init__(self):
        Boundary.__init__(self)
        t1 = Grid.C
        t2 = 1. / t1 + 2. + t1
        self._coef0 = - (1. / t1 - 2. + t1) / t2
        self._coef1 = - 2. * (t1 - 1. / t1) / t2
        self._coef2 = 4. * (t1 + 1. / t1) / t2

    def build_boundary(self, **kwargs):
        self._auxfield = [numpy.zeros((3,kwargs["size"]))] * 2
        return self

    # TODO: extend for y+- and x+ boundaries
    def __call__(self, *args):
        assert len(args) == 1
        field = args[0]
        update = (
            self._coef0 * (field[2,:] + self._auxfield[1][0,:]) +
            self._coef1 * (self._auxfield[0][0,:] + self._auxfield[0][2,:] - field[1,:] - self._auxfield[1][1,:]) +
            self._coef2 * self._auxfield[0][1,:] -
            self._auxfield[1][2,:]
        )
        self._auxfield.pop()
        self._auxfield.insert(0, numpy.array([update, field[1,:], field[2,:]]))
        return update
