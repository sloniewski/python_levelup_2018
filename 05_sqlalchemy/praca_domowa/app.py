from datetime import datetime
from functools import (
    reduce,
    wraps,
)
import json

from flask import (
    Flask,
    Response,
    request,
    abort,
)

from sqlalchemy import create_engine, Column, Integer, ForeignKey, DateTime, String, SmallInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship
from sqlalchemy.sql.functions import max, count

from engine_conf import conf_string

engine = create_engine(conf_string)

Base = declarative_base()

session = Session(engine)


class City(Base):
    __tablename__ = 'city'

    city_id = Column(Integer, primary_key=True)
    city = Column(String(50), nullable=False)
    country_id = Column(ForeignKey('country.country_id', ondelete='NO ACTION', onupdate='CASCADE'), nullable=False, index=True)
    last_update = Column(DateTime, nullable=False)

    country = relationship('Country')

    @property
    def to_dict(self):
        city = {
            'city_id': self.city_id,
            'city': self.city,
            'country_id': self.country_id,
        }
        return city

    @property
    def to_json(self):
        return json.dumps(self.to_dict)


class Country(Base):
    __tablename__ = 'country'

    country_id = Column(SmallInteger, primary_key=True)
    country = Column(String(50), nullable=False)
    last_update = Column(DateTime)


app = Flask(__name__)


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
        def wrapper(*args, **kwargs):
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
def city_endpoint():

    country_name = request.args.get('country_name')
    if country_name is not None:
        country_id = session.query(Country.country_id).filter(Country.country == country_name).scalar()
        if country_id is None:
            abort(404)
        cities = session.query(City.city).filter(City.country_id == country_id)
    else:
        cities = session.query(City.city)

    page = request.args.get('page')
    page = safe_str_to_int(page)
    if page is not None:

        per_page = request.args.get('per_page')
        per_page = safe_str_to_int(per_page)
        if per_page is None:
            per_page = 10

        city_count = session.query(count(City.city_id)).scalar()
        if city_count is None:
            city_count = 0

        paginator = PaginationHelper(items_count=city_count, items_per_page=per_page)
        offset = paginator.get_offset_for_page(page_num=page)

        cities_limited = cities.limit(per_page).offset(offset)
        cities = cities_limited
    # cities_ordered = cities.order_by('city') nie sortuje prawidłowo "Abha", "Abu Dhabi", "A Corua (La Corua)" ...
    cities_ordered = list(map(lambda a: a[0], cities.all()))

    return sorted(cities_ordered)


@app.route('/cities', methods=['POST'])
@jsonify_response(200)
@validate_json(request, 'country_id', 'city_name')
def add_city():
    data = json.loads(request.data)
    last_id = session.query(max(City.city_id)).scalar()
    if last_id is None:
        last_id = 0
    new_id = last_id + 1
    city = City(
        city_id=new_id,
        country_id=data['country_id'],
        city=data['city_name'],
        last_update=datetime.now().isoformat(sep=' ')
    )
    session.add(city)
    session.commit()
    return city.to_dict


@app.route('/')
def hello():
    return 'Hello'

if __name__ == '__main__':
    app.run(debug=True)
