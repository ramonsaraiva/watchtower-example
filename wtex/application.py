import requests
import secrets
import time

from flask import (
    Flask,
    request,
    current_app,
    render_template,
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


def build_response(app, request, template, data):
    """
    Builds a response creating a watchtower session key if does not exist.
    The session key contains a hex token of 64 characters.
    """
    response = app.make_response(render_template(template, **data))
    value = secrets.token_hex()
    if 'WTSK' not in request.cookies:
        response.set_cookie('WTSK', value=value)
    return response, request.cookies.get('WTSK', value)


@app.route('/')
def index():
    data = {}
    response, sk = build_response(current_app, request, 'index.jinja', data)
    send_pageview(request, response, sk, {})
    return response


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        response, sk = build_response(
            current_app, request, 'thanks.jinja', data={'email': email})

        event_data = {
            'uid': email,
            'ec': 'accounts',
            'en': 'signup',
            'ed': {
                'email': email,
                'password': password
            }
        }
        send_event(request, response, sk, event_data)
        return response

    response, sk = build_response(current_app, request, 'signup.jinja', {})
    send_pageview(request, response, sk, {})
    return response


@app.route('/books/')
@app.route('/books/<slug>/')
def books(slug=None):
    if slug:
        response, sk = build_response(
            current_app, request, 'book.jinja', {'slug': slug})
        send_pageview(request, response, sk, {})

        event_data = {
            'ec': 'books',
            'en': 'read',
            'ed': {
                'slug': slug,
                'words': 287
            }
        }
        send_event(request, response, sk, event_data)
        return response

    response, sk = build_response(current_app, request, 'books.jinja', {})
    send_pageview(request, response, sk, {})
    return response
