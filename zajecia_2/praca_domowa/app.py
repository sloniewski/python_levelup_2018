from uuid import uuid4
import json

from flask import (
    Flask,
    request,
    Response,
    redirect,
    render_template,
)

app = Flask(__name__)

session = None
logged_user = None
fishes = {
    "id_1": {
        "who": "Znajomy",
        "where": {
            "lat": 0.001,
            "long": 0.002,
        },
        "mass": 34.56,
        "length": 23.67,
        "kind": "szczupak",
    },
    "id_2": {
        "who": "Kolega kolegi",
        "where": {
            "lat": 34.001,
            "long": 52.002,
        },
        "mass": 300.12,
        "length": 234.56,
        "kind": "sum olimpijczyk",
    }
}


def authenticate(username, password):
    stored_username = 'Akwarysta69'
    stored_password = 'J3si07r'
    if username == stored_username and password == stored_password:
        global logged_user
        logged_user = username
        return True
    return False


@app.route('/login', methods=['POST'])
def login():
    global session

    # check if user is already logged
    if request.cookies.get('session_id') == str(session) and session is not None:
        return redirect(
            location='/hello',
        )

    # get username and password
    try:
        username = request.authorization['username']
        password = request.authorization['password']
    except (TypeError, KeyError, AttributeError):
        return Response(
            response='404 four oh four',
            status=404,
        )

    # authenticate user
    if authenticate(username, password):
        session_id = uuid4()
        session = session_id
        resp = Response()
        resp.set_cookie(key='session_id', value=str(session_id), path='/')
        resp.status_code = 301
        resp.headers.add('Location', '/hello')
        return resp
    else:
        return Response(
            response='401 Unauthorized',
            status=401,
        )


@app.route('/logout')
def logout():
    global session
    session = None
    return redirect(
        location='/login'
    )


@app.route('/hello')
def hello():
    global logged_user

    return render_template(
        template_name_or_list='hello.html',
        user=logged_user,
    )



def handle_GET():
    global fishes
    return str(fishes)

def handle_POST():
    global fishes

    #generate next id
    keys = [int(key[3:]) for key in fishes.keys()]
    next_id = 'id_' + str(max(keys)+1)
    print(next_id)


@app.route('/fishes', methods=['GET', 'POST'])
def handle_fishes_list():
    handlers = {
        'GET': handle_GET,
        'POST': handle_POST,
    }

    return handlers[request.method]()


def handle_PUT():
    pass


def handle_PATCH():
    pass


def handle_DELETE(fish_id):
    pass


@app.route('/fishes/<int:fish_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
def handle_fish_object(fish_id):
    global fishes
    try:
        fish = fishes[fish_id]
    except KeyError:
        return Response(
            response='404 four oh four',
            status=404,
        )

    handler = {
        'PUT': handle_PUT,
        'PATCH': handle_PATCH,
        'DELETE': handle_DELETE,
    }

    return handler


if __name__ == '__main__':
    app.run(debug=True)
