import requests
import secrets
import time

from flask import (
    Flask,
    request,
    current_app,
)


def create_app():
    app = Flask(__name__)
    return app


app = create_app()


def send_event(request, response, sk, data):
    user_agent = request.user_agent.string
    ip = request.remote_addr
    data.update({
        'sk': sk,
        'ua': user_agent,
        'ip': ip,
        'ts': str(time.time()),
    })
    response = requests.post('http://localhost:5000/event/', json=data)
    return response


def send_pageview(request, response, sk, data):
    data.update({
        'ec': 'root',
        'en': 'pageview',
        'ed': {
            'scheme': request.scheme,
            'host': request.host,
            'path': request.path
        }
    })
    send_event(request, response, sk, data)


def build_response(app, request, data):
    """
    Builds a response creating a watchtower session key if does not exist.
    The session key contains a hex token of 64 characters.
    """
    response = app.make_response(data)
    value = secrets.token_hex()
    if 'WTSK' not in request.cookies:
        response.set_cookie('WTSK', value=value)
    return response, request.cookies.get('WTSK', value)


@app.route('/')
def index():
    html = """
    Welcome to the homepage!
    """
    response, sk = build_response(current_app, request, html)
    send_pageview(request, response, sk, {})
    return response
