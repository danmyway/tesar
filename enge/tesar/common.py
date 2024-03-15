import abc
import copy
import functools

class FrozenException(Exception):
    def __init__(self):
        super().__init__(self, f"Can't do that! FROZEN!")

class Freezable(abc.ABC):
    FREEZABLE_PROPERTIES = {}

    def __init__(self):
        self._setup_freezable_properties()

    def __getattr__(self, attrname):
        return self._freezable_properties[attrname]

    def __setattr__(self, attrname, value):
        if attrname not in self._freezable_properties:
            return super().__setattr__(attrname, value)
        if self.frozen:
            raise FrozenException()
        self._freezable_properties[attrname] = value

    def _setup_freezable_properties(self):
        super().__setattr__(
            '_freezable_properties',
            copy.deepcopy(self.FREEZABLE_PROPERTIES)
        )

    @abc.abstractproperty
    def frozen(self):
        pass

def freezable(wrapped):
    @functools.wraps(wrapped)
    def wrapper(self, *args, **kwargs):
        if self.frozen:
            raise FrozenException()
        return wrapped(self, *args, **kwargs)
    return wrapper
