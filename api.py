print("Loading libraries...")
from aiohttp import web
import datetime
import pymysql
import os
import db
import logging
import random
import traceback
import sys
logging.basicConfig(level=logging.INFO)
try:
    dbapi = db.db(password="", ip="localhost", database="interessant")
except:
    if not "--allownodb" in sys.argv:
        print("Failed to set up database. Pass '--allownodb' to continue without a database connection.")
        os._exit(12)
    print("'--allownodb' passed, continuing without a database connection.")
routes = web.RouteTableDef()
links = {}
hashes = {}

def fill_cache():
    global hashes
    data = dbapi.exec_safe_query("select * from links", (), fetchall=True)
    if isinstance(data, dict):
        data = [data]
    if not data:
        print("No links in database!")
        return
    for link in data:
        links[link['hash']] = link['url']
    hashes = {v: k for k, v in links.items()}

async def compute_hash():
    a = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    n = ['1', '2', '3', '4', '5', '6', '7', '8', '0']
    for each in range(1, 9):
        hash = hash + random.choice([random.choice(a), random.choice(n)])
    return hash

@routes.get('/shorten')
async def shorten(request):
    global hashes
    print("Request recieved")
    url = request.rel_url.query.get('url', '').strip()
    if not url.startswith("http"):
        url = "http://"+url
    try:
        #url already shortened?? just return the existing hash for it
        if url in list(links.values()):
            return web.HTTPFound(f'/?hash={hashes[url]}')
    except KeyError:
        print("keyerror - see output above")
    hash = await compute_hash()
    try:
        dbapi.exec_safe_query("insert into links(url, hash) values(%s, %s)", (url, hash))
        links[hash] = url
        hashes[url] = hash
    except pymysql.err.IntegrityError:
        traceback.print_exc()
        return web.HTTPFound('/?hash=d')
    return web.HTTPFound(f'/?hash={hash}')

def return_document(name, type):
    document = open(name, "r")
    return web.Response(text=document.read(), content_type=type)

@routes.get('/deps/bootstrap.min.css')
async def css(request):
    return return_document('./deps/bootstrap.min.css', 'text/css')

@routes.get('/')
async def main(request):
    return return_document('index.html', 'text/html')

async def check_link(request):
    hash = request.path.replace('/', '')
    if hash in ['index.html', 'invalid.html', 'error.html']:
        return return_document(hash, 'text/html')
    if request.path in ['/deps/theming.js', '/deps/fa/solid.js', '/deps/fa/fontawesome.min.js', '/deps/fa/regular.js', '/deps/bootstrap.bundle.min.js']:
        return return_document(f".{request.path}", 'script/javascript')
    try:
        return web.HTTPFound(links[hash])
    except KeyError:
        ret = dbapi.exec_safe_query("select url from links where hash=%s", (hash))
        if ret:
            #have to nest to prevent keyerrors
            if ret['url']:
                return web.HTTPFound(ret['url'])
        return return_document('invalid.html', 'text/html')
    except:
        return return_document('invalid.html', 'text/html')
    
async def handle_errors(request):
    return return_document('error.html', 'text/html')

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
    error_middleware = create_error_middleware({404 : check_link, 500 : handle_errors})
    app.middlewares.append(error_middleware)

app = web.Application()
app.add_routes(routes)

try:
    from aiohttp_compress import compress_middleware
    app.middlewares.append(compress_middleware)
except ImportError:
    print("aiohttp-compress isn't installed. Compression disabled.")
setup_middlewares(app)
if not "--allownodb" in sys.argv:
    fill_cache()
web.run_app(app, port=80, access_log=None)
