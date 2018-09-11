from aiohttp import web
from aiohttp_wsgi import WSGIHandler

from .app import application

wsgi_handler = WSGIHandler(application)
app = web.Application()
app.router.add_route("*", "/{path_info:.*}", wsgi_handler)
web.run_app(app)
