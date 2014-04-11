import os

from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple

from miniblog.miniblog import PageTree


DIR = os.getcwd()


class MiniblogServer(object):
    def __init__(self, path):
        self.tree = PageTree(path)

    def dispatch(self, request):
        return Response("yo " + DIR)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def run_server(host='127.0.0.1', port=5000, server=None):
    if server is None:
        app = MiniblogServer()
    else:
        app = server
    run_simple(host, port, app, use_debugger=True, use_reloader=True)
