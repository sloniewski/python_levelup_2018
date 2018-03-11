from datetime import datetime

from flask import (
    Flask,
    request,
)

from user_agents import parse

app = Flask(__name__)


@app.route('/')
def hello():
    return "Hello, World!"


@app.route('/now')
def time():
    now_object = datetime.now()
    return now_object.isoformat(sep=' ')


@app.route('/user-agent')
def user_agent():
    ua_string = request.headers['User-Agent']
    user_agent = parse(ua_string)
    return '{} / {} / {}'.format(
        user_agent.device.family,
        user_agent.os.family,
        user_agent.browser.family,
    )

if __name__ == '__main__':
    app.run()
