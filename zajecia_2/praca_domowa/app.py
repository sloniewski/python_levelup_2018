from uuid import uuid4
import json

from flask import (
    Flask,
    request,
    Response,
    redirect,
    render_template,
    session
)

app = Flask(__name__)

app.secret_key = str(uuid4())

# this global variable will substitute database for now
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
        session['username'] = username
        session['logged'] = True
        return True
    return False


@app.route('/login', methods=['POST'])
def login():

    # check if user is already logged
    if session.get('logged') is True:
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
        resp = Response()
        resp.status_code = 301
        resp.headers.add('Location', '/hello')
        return resp
    else:
        return Response(
            response='401 Unauthorized',
            status=401,
        )


@app.route('/logout', methods=['POST'])
def logout():
    session['username'] = None
    session['logged'] = None
    return redirect(
        location='/hello'
    )


@app.route('/hello')
def hello():
    return render_template(
        template_name_or_list='hello.html',
        user=session.get('username'),
    )


def handle_GET():
    global fishes
    resp = Response(
        response=json.dumps(fishes, indent=4),
    )
    resp.headers.set('Content-Type', 'application/json')
    return resp


def handle_POST():
    if not session.get('logged'):
        return Response(
            response='401 Unauthorized',
            status=401,
        )
    global fishes
    fish = json.loads(request.data)

    # generate next id
    keys = [int(key[3:]) for key in fishes.keys()]
    next_id = 'id_' + str(max(keys)+1)

    # add new fish to dict
    fishes[next_id] = fish
    return json.dumps(fishes[next_id])


@app.route('/fishes', methods=['GET', 'POST'])
def handle_fishes_list():
    handlers = {
        'GET': handle_GET,
        'POST': handle_POST,
    }

    return handlers[request.method]()


def handle_GET_fish(fish_id):
    global fishes
    resp = Response(
        response=json.dumps(fishes[fish_id], indent=4),
    )
    resp.headers.set('Content-Type', 'application/json')
    return resp


def handle_PUT_fish(fish_id):
    if not session.get('logged'):
        return Response(
            response='401 Unauthorized',
            status=401,
        )
    global fishes
    fish = json.loads(request.data)
    fishes[fish_id] = fish

    # set up response
    resp = Response(
        response=json.dumps(fishes[fish_id], indent=4),
    )
    resp.headers.set('Content-Type', 'application/json')
    return resp


def handle_PATCH_fish(fish_id):
    # check for login
    if not session.get('logged'):
        return Response(
            response='401 Unauthorized',
            status=401,
        )
    global fishes
    fish = fishes[fish_id]

    # load request data
    fish_data = json.loads(request.data)

    # reassign values using incoming data
    for key, value in fish_data.items():
        fish[key]=value
    fishes[fish_id] = fish

    # set up response
    resp = Response(
        response=json.dumps(fishes[fish_id], indent=4),
    )
    resp.headers.set('Content-Type', 'application/json')
    return resp


def handle_DELETE_fish(fish_id):
    if not session.get('logged'):
        return Response(
            response='401 Unauthorized',
            status=401,
        )
    global fishes
    deleted_fish = fishes[fish_id]
    del(fishes[fish_id])

    # set up response
    resp = Response(
        response=json.dumps(deleted_fish, indent=4),
    )
    resp.headers.set('Content-Type', 'application/json')
    return resp


@app.route('/fishes/<fish_id>', methods=['GET', 'PUT', 'PATCH', 'DELETE'])
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
        'GET': handle_GET_fish,
        'PUT': handle_PUT_fish,
        'PATCH': handle_PATCH_fish,
        'DELETE': handle_DELETE_fish,
    }

    return handler[request.method](fish_id)


if __name__ == '__main__':
    app.run(debug=True)
