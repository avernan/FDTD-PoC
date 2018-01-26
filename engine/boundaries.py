
class Boundary(object):
    pass

class PEC(Boundary):
    """
    Perfect Electric Conductor (PEC) boundary.
    Perfectly reflecting boundary obtained by forcing the terminating E node to zero
    """
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        return 0
