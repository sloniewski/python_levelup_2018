from _datetime import datetime
import json
from functools import reduce
import sqlite3

from flask import (
    Flask,
    Response,
    g,
    request,
)


app = Flask(__name__)

DATABASE = '/home/maciek/Documents/python_levelup_2018/04_sqlite/praca_domowa/db.sqlite3'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


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


@app.route('/cities', methods=['GET'])
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
    resp = Response(
        response=json.dumps(data, indent=4),
    )
    resp.headers.set('Content-Type', 'application/json')
    return resp


@app.route('/cities', methods=['POST'])
def add_city():
    data = json.loads(request.data)

    db = get_db()
    cursor = db.cursor()

    max_id_query = 'SELECT Max(city_id) FROM city;'
    city_id = int(cursor.execute(max_id_query).fetchone()[0]) + 1

    insert_query = 'INSERT INTO city (city_id, city, country_id, last_update) VALUES (:city_id, :city_name, :country_id, :update_date);'

    params = {}
    params['city_name'] = data['city_name']
    params['country_id'] = data['country_id']
    params['update_date'] = datetime.now().isoformat(sep=' ')
    params['city_id'] = city_id

    cursor.execute(insert_query, params).fetchall()

    return str(city_id)

if __name__ == '__main__':
    app.run(debug=True)
