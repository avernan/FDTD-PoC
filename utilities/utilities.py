from matplotlib.colors import LogNorm

class SafeLogNorm(LogNorm):
    def __call__(self, value, clip=None):
        return LogNorm.__call__(self, value + 1e-20, clip)

