import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(message)s')
file_handler = logging.FileHandler('test.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def log_this(logger, level, format):
    def decorator(function):
        def wrapper(*args, **kwargs):
            # call function
            result = function(*args, **kwargs)

            # build message
            message = format % (function.__name__, (args, kwargs), result)

            # log results with function matching log level
            logging_func = {
                10: logger.debug,
                20: logger.info,
                30: logger.warning,
                40: logger.error,
                50: logger.critical,
            }
            logging_func[level](msg=message)

            return result
        return wrapper
    return decorator


@log_this(logger=logger, level=logging.DEBUG, format='%s: %s -> %s')
def my_func(a, b, c=None, d=False):
    return 'Wow!'


print(my_func(1, 2, c='x'))
