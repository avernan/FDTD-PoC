import numpy


class Source(object):
    def __init__(self, position, pulse):
        self.position = position
        self.pulse = pulse


class SourceDipole(Source):
    """
    Dipole (additive) sources with arbitrary position and pulse shape
    """
    def __init__(self, grid, position, pulse):
        super().__init__(position, pulse)
        grid.register_build_callback(self.build)
        grid.register_step_callback("post", "e", self)

    def __call__(self, t):
        self._field += self.pulse.update(t)

    def build(self, grid):
        xpos = slice(self.position[0], self.position[0]+1)
        ypos = slice(self.position[1], self.position[1]+1)
        self._field = grid.get_field("z")._data[xpos,ypos]


class SourceTFSF(Source):
    """
    Total Field/Scattered Field box for plane waves with arbitrary propagation
    direction and temporal shape (Pulse)
    """
    # TODO: extend to arbitrary phi
    def __init__(self, grid, bleft, tright, pulse,
                 spacel=2, spacer=3):
        super().__init__((bleft, tright), pulse)
        grid.register_build_callback(self.build)
        grid.register_step_callback("pre", "e", self)
        self.spacel = spacel
        self.spacer = spacer

        t1 = grid.C
        t2 = 1. / t1 + 2. + t1
        self._coef0 = - (1. / t1 - 2. + t1) / t2
        self._coef1 = - 2. * (t1 - 1. / t1) / t2
        self._coef2 = 4. * (t1 + 1. / t1) / t2
        return

    def __call__(self, t):
        self._bound_Hl -= self._C / self._Z0 * self._E[self.spacel]
        self._bound_Hr += self._C / self._Z0 * self._E[-(self.spacer + 1)]
        self._bound_Hb += self._C / self._Z0 * self._E[self.spacel:-self.spacer]
        self._bound_Ht -= self._C / self._Z0 * self._E[self.spacel:-self.spacer]

        self._H += self._C / self._Z0 * (self._E[1:] - self._E[:-1])
        self._E[1:-1] += self._C * self._Z0 * (self._H[1:] - self._H[:-1])
        self._E[-1] = (
            self._coef0 * (self._E[-3] + self._auxfield[1][0]) +
            self._coef1 * (self._auxfield[0][0] + self._auxfield[0][2] - self._E[-2] - self._auxfield[1][1]) +
            self._coef2 * self._auxfield[0][1] - self._auxfield[1][2]
        )
        self._auxfield.pop()
        self._auxfield.insert(0, self._E[-1:-4:-1].copy())

        self._E[0] = self.pulse.update(t)

        self._bound_El -= self._C * self._Z0 * self._H[self.spacel - 1]
        self._bound_Er += self._C * self._Z0 * self._H[-self.spacer]

    def build(self, grid):
        self._C = grid.C
        self._Z0 = grid.Z0
        xs = tuple(val[0] for val in self.position)
        ys = tuple(val[1] for val in self.position)
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
        self._auxfield = [numpy.zeros(3), numpy.zeros(3)]


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
                          numpy.math.cos(self.omega*t))
