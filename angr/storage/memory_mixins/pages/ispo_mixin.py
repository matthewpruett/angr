from .. import MemoryMixin

class ISPOMixin(MemoryMixin):
    """
    An implementation of the International Stateless Persons Organisation, a mixin which should be applied as a bottom
    layer for memories which have no state and must redirect certain operations to a parent memory. Main usecase is
    for memory region classes which are stored within other memories, such as pages.
    """
    def set_state(self, state):
        raise Exception("Cannot set state on this stateless object")

    def _default_value(self, *args, memory=None, **kwargs):
        try:
            func = memory._default_value
        except AttributeError as e:
            raise Exception("memory kwarg must be passed to this stateless object") from e
        else:
            return func(*args, **kwargs)

    def _add_constraints(self, *args, memory=None, **kwargs):
        try:
            func = memory._add_constraints
        except AttributeError as e:
            raise Exception("memory kwarg must be passed to this stateless object") from e
        else:
            return func(*args, **kwargs)