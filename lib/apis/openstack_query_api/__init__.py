import threading


class QueryThread(threading.Thread):
    """
    Custom thread class that allows for returning a value from the target function.
    """

    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None):
        super().__init__(group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, timeout=None):
        super().join(timeout)
        return self._return
