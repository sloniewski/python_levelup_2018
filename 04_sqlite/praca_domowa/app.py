import sqlite3
import json

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
    if page is not None:
        per_page = request.args.get('per_page')
        if per_page is None:
            per_page = 10

        query += ' LIMIT :per_page OFFSET :page'
        params['per_page'] = int(per_page)
        params['page'] = int(page)

    query += ';'

    data = cursor.execute(query, params).fetchall()
    resp = Response(
        response=json.dumps(data, indent=4),
    )
    resp.headers.set('Content-Type', 'application/json')
    return resp


if __name__ == '__main__':
    app.run(debug=True)