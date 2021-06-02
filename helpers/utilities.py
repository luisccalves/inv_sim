import pickle
import re
import logging
import time

from functools import wraps

def log_this(level, name=None, message=None):
    """Logs and reports the execution time of methods and functions"""

    def time_this(func):
        logname = name if name else func.__module__
        log = logging.getLogger(__name__)
        log.addHandler(logging.NullHandler())
        log_msg = message if message else ''

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            log.log(level, 'FUNCTION: {}.{} EXECUTION TIME: {} MESSAGE: {}'
                    .format(logname, func.__name__, end - start, log_msg))
            return result

        return wrapper

    return time_this