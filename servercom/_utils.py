"""Some utilities that help out behind-the-scenes."""

class Immutable:
    """Superclass for immutable objects
    """

    def __init__(self):
        """As soon as this constructor is called, the object becomes immutable
        """
        self._frozen = True

    def __delattr__(self, *args, **kwargs):
        if hasattr(self, '_frozen'):
            raise AttributeError("This object is immutable. You cannot delete instance variables from it.")
        object.__delattr__(self, *args, **kwargs)

    def __setattr__(self, *args, **kwargs):
        if hasattr(self, '_frozen'):
            raise AttributeError("This object is immutable. You cannot set any instance variables.")
        object.__setattr__(self, *args, **kwargs)
