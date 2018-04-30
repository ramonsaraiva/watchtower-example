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

    <ul>
        <li><a href="/signup/">Sign up</a></li>
        <li><a href="/login/">Login</a></li>
        <li><a href="/news/">Read our news</a></li>
        <li><a href="/about/">About us</a></li>
    </ul>
    """
    response, sk = build_response(current_app, request, html)
    send_pageview(request, response, sk, {})
    return response


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        html = f"""
        Thanks for signing up {email}!<br/>
        <a href="/">Go back to the homepage</a>
        """
        response, sk = build_response(current_app, request, html)

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

    html = """
    Sign up

    <form method="post" action="/signup/">
        <input type="email" name="email" value="example@email.com" />
        <input type="password" name="password" value="password" />
        <input type="submit" value="Submit" />
    </form>
    """
    response, sk = build_response(current_app, request, html)
    send_pageview(request, response, sk, {})
    return response


@app.route('/news/')
@app.route('/news/<slug>/')
def news(slug=None):
    if slug:
        html = f"""
        <a href="/news/">Back to news</a>

        <h1>{slug}</h1>

        <p>Lorem ipsum dolor amet.</p>
        <p>Lorem ipsum dolor amet.</p>
        <p>Lorem ipsum dolor amet.</p>
        """
        response, sk = build_response(current_app, request, html)
        send_pageview(request, response, sk, {})

        event_data = {
            'ec': 'news',
            'en': 'read',
            'ed': {
                'slug': slug,
                'words': 287
            }
        }
        send_event(request, response, sk, event_data)
        return response

    html = """
    <a href="/">Home</a> | News

    <ul>
        <li><a href="/news/black-girl/">Black Girl</a></li>
        <li><a href="/news/the-broken-ice/">The Broken Ice</a></li>
        <li><a href="/news/shores-of-winter/">Shores of Winter</a></li>
        <li><a href="/news/the-obsessions-servant/">The Obsession's Servant</a></li>
        <li><a href="/news/the-voyage-of-the-stars/">The Voyage of the Stars</a></li>
        <li><a href="/news/destruction-in-the-past/">Destruction in the Past</a></li>
    </ul>
    """
    response, sk = build_response(current_app, request, html)
    send_pageview(request, response, sk, {})
    return response
