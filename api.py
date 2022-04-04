from aiohttp import web
import datetime
import pymysql
import os
import db
import logging
import random
import traceback

logging.basicConfig(level=logging.INFO)
dbapi = db.db(password="19Integra98", ip="localhost", database="interessant")
routes = web.RouteTableDef()
links = {}

def fill_cache():
    data = dbapi.exec_safe_query("select * from links", (), fetchall=True)
    if isinstance(data, dict):
        data = [data]
    if not data:
        print("No links in database!")
        return
    for link in data:
        links[link['hash']] = link['url']
    print(links)

async def compute_hash():
    a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    n = ['1', '2', '3', '4', '5', '6', '7', '8', '0']
    hash = random.choice(n)
    for each in range(1, 8):
        hash += random.choice([random.choice(a), random.choice(n)])
    hash += str(int(hash[0])+1)
    print(hash)
    return hash

@routes.get('/deps/bootstrap.bundle.min.js')
async def js(request):
    return return_document('./deps/bootstrap.bundle.min.js', 'text/javascript')

@routes.get('/shorten')
async def shorten(request):
    print("Request recieved")
    url = request.rel_url.query.get('url', '')
    hash = await compute_hash()
    try:
        dbapi.exec_safe_query("insert into links(url, hash) values(%s, %s)", (url, hash))
        links[hash] = url
    except pymysql.err.IntegrityError:
        traceback.print_exc()
        return web.HTTPFound('/?hash=d')
    return web.HTTPFound(f'/?hash={hash}')

def return_document(document, type):
    html = open(document, "r")
    return web.Response(text=html.read(), content_type=type)

@routes.get('/deps/bootstrap.min.css')
async def css(request):
    return return_document('./deps/bootstrap.min.css', 'text/css')

@routes.get('/')
async def main(request):
    return return_document('index.html', 'text/html')

async def check_link(request):
    hash = request.path.replace('/', '')
    print(hash)
    try:
        #checksum
        if int(hash[-1]) - int(hash[0]) != 1:
            raise ValueError
        return web.HTTPFound(links[request.path.replace('/', '')])
    except (KeyError, ValueError):
        return return_document('invalid.html', 'text/html')

def create_error_middleware(overrides):

    @web.middleware
    async def error_middleware(request, handler):
        try:
            return await handler(request)
        except web.HTTPException as ex:
            override = overrides.get(ex.status)
            if override:
                return await override(request)

            raise
        except Exception:
            request.protocol.logger.exception("Error handling request")
            return await overrides[500](request)

    return error_middleware


def setup_middlewares(app):
    error_middleware = create_error_middleware({
        404: check_link,
    })
    app.middlewares.append(error_middleware)

app = web.Application()
app.add_routes(routes)
setup_middlewares(app)
fill_cache()
web.run_app(app, port=80)