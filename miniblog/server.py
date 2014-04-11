import os

from werkzeug.utils import redirect
from werkzeug.wrappers import Response, Request
from werkzeug.serving import run_simple

from miniblog import SiteNamespace


DIR = os.getcwd()


class MiniblogServer(object):
    def __init__(self, content_folder, template_folder):
        self.namespace = SiteNamespace(content_folder, template_folder)

    def dispatch(self, request):
        if not request.path.endswith('/'):
            return redirect(request.path + '/')

        try:
            return Response(self.namespace.dispatch(request.path), content_type='text/html')
        except ValueError:
            return Response("<html><body><h1>404 Page not found</h1></body></html>",
                            content_type='text/html', status=404)

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def get_extra_files(content_folder, template_folder):
    """
    Get all interesting files in a certain folder that need to be watched.
    """
    extra_paths = [(path, files) for path, dirs, files in os.walk(content_folder) if files]
    extra_paths.extend((path, files) for path, dirs, files in os.walk(template_folder) if files)
    extra_files = []
    for path, files in extra_paths:
        for file in files:
            extra_files.append(os.path.join(path, file))
    return extra_files


def run_server(content_folder, template_folder, host='127.0.0.1', port=5000, server=None):
    if server is None:
        app = MiniblogServer(content_folder, template_folder)
    else:
        app = server
    extra_files = get_extra_files(content_folder, template_folder)
    run_simple(host, port, app, use_debugger=True, use_reloader=True, extra_files=extra_files)
