import numpy

class Boundary(object):
    def __init__(self, grid, side):
        grid.register_step_callback('post', 'e', self)

    def __call__(self, t):
        raise NotImplementedError

class PEC(Boundary):
    """
    Perfect Electric Conductor (PEC) boundary.
    Perfectly reflecting boundary obtained by forcing the terminating E node to zero
    """
    def __call__(self, *args):
        pass

class ABC(Boundary):
    """
    Differential equation based absorbing boundary conditions (ABC)
    cf. http://www.eecs.wsu.edu/~schneidj/ufdtd/chap6.pdf eq. 6.32-33
    """
    def __init__(self, grid, side):

        Boundary.__init__(self, grid, side)
        t1 = grid.C
        t2 = 1. / t1 + 2. + t1
        self._coef0 = - (1. / t1 - 2. + t1) / t2
        self._coef1 = - 2. * (t1 - 1. / t1) / t2
        self._coef2 = 4. * (t1 + 1. / t1) / t2

        if 'x' in side:
            size = grid.shape[1]
        elif 'y' in side:
            size = grid.shape[0]
        else:
            raise Exception("Unrecognised side {}".format(side))

        self._auxfield = [numpy.zeros((3, size))] * 2

        if side == 'xm':
            self._realfield = grid._Fz._data[0:3,:]
        elif side == 'xp':
            self._realfield = grid._Fz._data[-1:-4:-1,:]
        elif side == 'ym':
            self._realfield = numpy.transpose(grid._Fz._data[:,0:3])
        elif side == 'yp':
            self._realfield = numpy.transpose(grid._Fz._data[:,-1:-4:-1])

    def __call__(self, *args):
        update = (
            self._coef0 * (self._realfield[2,:] + self._auxfield[1][0,:]) +
            self._coef1 * (self._auxfield[0][0,:] + self._auxfield[0][2,:] - self._realfield[1,:] - self._auxfield[1][1,:]) +
            self._coef2 * self._auxfield[0][1,:] -
            self._auxfield[1][2,:]
        )
        self._auxfield.pop()
        self._auxfield.insert(0, numpy.array([update, self._realfield[1,:].copy(), self._realfield[2,:].copy()]))

        self._realfield[0,:] = update
