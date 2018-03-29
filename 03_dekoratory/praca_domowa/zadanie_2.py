from functools import wraps
import json


def validate_json(*expected_args):
    def decorator(func):
        @wraps(func)
        def wrapper(json_data, *args, **kwargs):
            json_dict = json.loads(json_data)
            missing = set(expected_args) - set(json_dict)
            if len(missing) != 0:
                raise ValueError(
                    'missing data in json {}'.format(
                        str(missing)[1:-1]
                    )
                )
            extra = set(json_dict) - set(expected_args)
            if len(extra) != 0:
                raise ValueError(
                    'got unexpected data: {}'.format(
                        str(extra)[1:-1]
                    )
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
