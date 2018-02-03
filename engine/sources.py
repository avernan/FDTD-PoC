import numpy


class Source(object):
    def __call__(self, *args, **kwargs):
        return float(0)

    def get_position(self):
        return (0,0)

    def update(self, t):
        return


class SourceDipole(Source):
    """
    Dipole (additive) sources with arbitrary position and pulse shape
    """
    def __init__(self, pos, pulse):
        self._position = pos
        self._source = pulse

    def __call__(self, *args, **kwargs):
        assert len(args) == 1
        return self._source.update(args[0])

    def get_position(self):
        """Return dipole source position as a tuple"""
        return self._position


class SourceTFSF(Source):
    """
    Total Field/Scattered Field box for plane waves with arbitrary propagation
    direction and temporal shape (Pulse)
    """
    # TODO: extend to arbitrary phi
    def __init__(self, grid, bleft, tright, pulse):
        xs = [bleft[0], tright[0]]
        ys = [bleft[1], tright[1]]
        self._source = pulse
        self.C = grid.C
        self.Z0 = grid.Z0
        self.space = 2
        NP = xs[1] - xs[0] + 2*self.space + 1
        NP = xs[1] - xs[0] + self.spacel + self.spacer + 1
        self._bound_El = grid.get_field('z')._data[xs[0],ys[0]:ys[1]+1]
        self._bound_Hl = grid.get_field('y')._data[xs[0]-1,ys[0]:ys[1]+1]
        self._bound_Er = grid.get_field('z')._data[xs[1],ys[0]:ys[1]+1]
        self._bound_Hr = grid.get_field('y')._data[xs[1],ys[0]:ys[1]+1]

        self._bound_Et = grid.get_field('z')._data[xs[0]:xs[1]+1,ys[1]]
        self._bound_Ht = grid.get_field('x')._data[xs[0]:xs[1]+1,ys[1]]
        self._bound_Eb = grid.get_field('z')._data[xs[0]:xs[1]+1,ys[0]]
        self._bound_Hb = grid.get_field('x')._data[xs[0]:xs[1]+1,ys[0]-1]

        self._E = numpy.zeros(NP)
        self._H = numpy.zeros(NP - 1)
        return

    def update(self, t):
        #TODO: implement ABC on right end of 1D grid
        self._bound_Hl -= self.C / self.Z0 * self._E[self.space]
        self._bound_Hr += self.C / self.Z0 * self._E[-(self.space+1)]
        self._bound_Hb += self.C / self.Z0 * self._E[self.space:-self.space]
        self._bound_Ht -= self.C / self.Z0 * self._E[self.space:-self.space]

        self._H += self.C / self.Z0 * (self._E[1:] - self._E[:-1])
        self._E[1:-1] += self.C * self.Z0 * (self._H[1:] - self._H[:-1])

        self._E[0] = self._source.update(t)

        self._bound_El -= self.C * self.Z0 * self._H[self.space-1]
        self._bound_Er += self.C * self.Z0 * self._H[-self.space]
        return


class Pulse(object):
    """
    Abstract pulse class. Subclasses should override the update method
    """
    def update(self, t):
        """Return value of source at time t"""
        raise NotImplementedError


class PulseGaussian(Pulse):
    # noinspection PyPep8Naming
    def __init__(self, E0, mu, tau, omega):
        self.ampl = E0
        self.mu = mu
        self.tau = tau
        self.omega = omega

    def update(self, t):
        return self.ampl*(numpy.math.exp(-(t - self.mu)**2 / self.tau**2) *
                          numpy.math.cos(2*numpy.math.pi*self.omega*t))
