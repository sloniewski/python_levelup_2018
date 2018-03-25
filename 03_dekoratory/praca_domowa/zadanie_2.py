from functools import wraps
import json


def validate_json(*expected_args):
    def decorator(func):
        @wraps(func)
        def wrapper(json_data, *args, **kwargs):
            json_object = json.loads(json_data)
            for expected_arg in expected_args:
                if expected_arg not in json_object.keys():
                    raise ValueError(
                        'key {} missing in json'.format(expected_arg)
                    )
            return func(json_data, *args, **kwargs)
        return wrapper
    return decorator


@validate_json('first_name', 'last_name')
def process_json(json_data):
    return len(json_data)


result = process_json('{"first_name": "James", "last_name": "Bond"}')
assert result == 44

try:
    process_json('{"first_name": "James", "age": 45}')
except ValueError:
    print('!')
else:
    print('fail')

try:
    process_json('{"first_name": "James", "last_name": "Bond", "age": 45}')
except ValueError:
    print('!')
else:
    print('fail')
