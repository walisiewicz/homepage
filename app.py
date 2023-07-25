from flask import Flask, render_template
from flask_uwsgi_websocket import GeventWebSocket

from functions import handle_socket

app = Flask(__name__)
websocket = GeventWebSocket()
websocket.init_app(app)


@app.route('/')
def main():
    return render_template("main.html")


@websocket.route('/data')
def data(socket):
    handle_socket(socket)
