from functools import wraps


def add_tag(tag):
    def decorator(func):
        @wraps(func)
        def wrapper():
            text = func()
            return '<{0}>{1}</{0}>'.format(
                tag, text
            )
        return wrapper
    return decorator


@add_tag('h1')
def write_something():
    return 'something'


result = write_something()
print(result)
assert result == '<h1>something</h1>'
