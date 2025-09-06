import threading


class SingletonMeta(type):
    """
    singleton metaclass (thread-safe)
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        _lock = threading.Lock()
        with _lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
