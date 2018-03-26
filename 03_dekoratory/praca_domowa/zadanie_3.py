import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def log_this(logger, level, format):
    def decorator(function):
        def wrapper(*args, **kwargs):
            logging.basicConfig(format=format)
            result = function(*args, **kwargs)
            print(function.__name__, (args, kwargs), result)
            return result
        return wrapper
    return decorator


@log_this(logger, level=logging.INFO, format='%s: %s -> %s')
def my_func(a, b, c=None, d=False):
    return 'Wow!'


print(my_func(1, 2, c='x'))
