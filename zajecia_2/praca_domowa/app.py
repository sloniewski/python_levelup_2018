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
    try:
        username = request.authorization['username']
        password = request.authorization['password']
    except (TypeError, KeyError, AttributeError):
        return Response(
            response='404 four oh four',
            status=404,
        )

    if authenticate(username, password):
        return redirect(
            location='/hello',
        )
    else:
        return Response(
            response='401 Unauthorized',
            status=401,
        )


@app.route('/test')
def test():
    print(request.authorization)
    return '!'


@app.route('/logout')
def logout():
    global session
    session = None
    return 'done'


@app.route('/hello')
def hello():
    global logged_user

    return render_template(
        template_name_or_list='hello.html',
        user=logged_user,
    )


@app.route('/fishes')
def fishes():
    pass


if __name__ == '__main__':
    app.run(debug=True)
