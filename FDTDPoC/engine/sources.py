import numpy


class SourceDipole(object):
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
