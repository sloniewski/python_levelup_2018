from datetime import datetime
from functools import (
    reduce,
    wraps,
)
import json
import sqlite3
import sys

from flask import (
    Flask,
    Response,
    g,
    request,
    abort,
)


app = Flask(__name__)

DATABASE = sys.path[0]+'/db.sqlite3'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def safe_str_to_int(value):
    if value is None:
        return None
    try:
        value = int(value)
    except ValueError:
        return None
    return value


def jsonify_response(code):
    def decorator(func):
        @wraps(func)
        def wrapper(*args,**kwargs):
            data = func(*args, **kwargs)
            return Response(
                status=code,
                response=json.dumps(data, indent=4),
                headers=[('Content-Type', 'application/json')]
            )
        return wrapper
    return decorator


class PaginationHelper:

    def __init__(self, items_count, items_per_page):
        self.items_count = items_count
        self.items_per_page = items_per_page

    @property
    def page_count(self):
        if self.items_count % self.items_per_page == 0:
            page_count = self.items_count / self.items_per_page
        else:
            page_count = (self.items_count // self.items_per_page) + 1
        return page_count

    def get_offset_for_page(self, page_num):
        if page_num <= 1:
            return 0
        if page_num > self.page_count:
            return self.items_per_page * (self.page_count - 1)

        return self.items_per_page * (page_num - 1)


@app.errorhandler(400)
@jsonify_response(400)
def bad_request(error):
    return error.description


def validate_json(req, *expected_args):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                data = json.loads(req.data)
            except json.decoder.JSONDecodeError:
                abort(400, {'error': 'unable to parse json'})

            missing = set(expected_args) - set(data)
            if len(missing) != 0:
                abort(
                    400, {'error': 'missing data in json: {}'.format(str(missing)[1:-1])})

            extra = set(data) - set(expected_args)
            if len(extra) != 0:
                abort(
                    400, {'error': 'got unexpected data: {}'.format(str(extra)[1:-1])})

            return func(*args, **kwargs)
        return wrapper
    return decorator


@app.route('/cities', methods=['GET'])
@jsonify_response(200)
def cities():
    db = get_db()
    cursor = db.cursor()

    query = 'SELECT city FROM city'
    params = {}

    country_name = request.args.get('country_name')
    if country_name is not None:
        query += ' JOIN country WHERE city.country_id = country.country_id AND country.country = :country_name'
        params['country_name'] = country_name

    query += ' ORDER BY city'

    page = request.args.get('page')
    page = safe_str_to_int(page)
    if page is not None:

        per_page = request.args.get('per_page')
        per_page = safe_str_to_int(per_page)
        if per_page is None:
            per_page = 10

        count_query = 'SELECT Count(*) FROM( {} );'.format(query)
        count = cursor.execute(count_query, params).fetchone()[0]
        count = safe_str_to_int(count)
        paginator = PaginationHelper(items_count=count, items_per_page=per_page)
        offset = paginator.get_offset_for_page(page_num=page)

        query += ' LIMIT :limit OFFSET :offset'
        params['limit'] = per_page
        params['offset'] = offset

    query += ';'

    data = cursor.execute(query, params).fetchall()
    data = reduce((lambda x, y: x + y), data)
    return data


@app.route('/cities', methods=['POST'])
@jsonify_response(200)
@validate_json(request, 'country_id', 'city_name')
def add_city():
    data = json.loads(request.data)

    db = get_db()
    db.row_factory = dict_factory
    cursor = db.cursor()

    country_id_query = 'SELECT country_id from country WHERE country_id = :country_id'
    country_id_check = cursor.execute(country_id_query, {'country_id': data['country_id']}).fetchone()

    if country_id_check is None:
        abort(400, {'error': 'wrong country_id'})

    max_id_query = 'SELECT Max(city_id) FROM city;'
    city_id = int(cursor.execute(max_id_query).fetchone()['Max(city_id)']) + 1

    insert_query = 'INSERT INTO city (city_id, city, country_id, last_update)' \
                   'VALUES (:city_id, :city_name, :country_id, :update_date);'

    params = {
        'city_name': data['city_name'],
        'country_id': data['country_id'],
        'update_date': datetime.now().isoformat(sep=' '),
        'city_id': city_id,
    }

    cursor.execute(insert_query, params)
    db.commit()
    
    return cursor.execute('SELECT * FROM city WHERE city_id = :city_id', {'city_id': city_id}).fetchone()


@app.route('/lang_roles', methods=["GET"])
@jsonify_response(200)
def lang_roles():
    db = get_db()
    cursor = db.cursor()

    query = """
      Select name, Count(name) FROM (
            SELECT actor_id, language.name
            FROM film_actor 
            JOIN film ON film_actor.film_id = film.film_id
            JOIN language ON film.language_id = language.language_id
        ) Group BY name;
    """
    return dict(cursor.execute(query).fetchall())


if __name__ == '__main__':
    app.run(debug=True)
