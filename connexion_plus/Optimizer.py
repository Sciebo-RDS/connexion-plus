# stolen from https://github.com/sunary/flask-optimize/blob/b4421c166fd61b357a9666f34ffb1370bffff7e3/flask_optimize/optimize.py

import sys
import gzip
import time
from htmlmin.main import minify
from flask import request, Response, make_response, current_app, json, wrappers
from functools import update_wrapper, wraps
from flask import Flask
import logging

logger = logging.getLogger('')

IS_PYTHON_3 = True
if sys.version_info[0] < 3:
    from StringIO import StringIO
    IS_PYTHON_3 = False
else:
    from io import BytesIO


class FlaskOptimize(object):

    _cache = {}
    _timestamp = {}

    def __init__(self, app, config=None):
        """
        Global config for flask optimize. 

        Cache have to enabled manually per function with decorator #set_cache_timeout
        Args:
            config: global configure values
        """
        logger.info("Initialize FlaskOptimize...")
        if config is None:
            config = {
                "compress": True,
                "minify": True
            }
        logger.info("Optimizer config: {}".format(config))

        self.config = config
        self.init_app(app)

    def init_app(self, app):
        def before_request():
            # set something useful
            pass

        def after_request(response):
            return self.optimize_response(response)

        app.before_request(before_request)
        app.after_request(after_request)

    @staticmethod
    def set_cache_timeout(timeout=86400):
        """
        Decorator to set the cache for the method.
        This is the only optimization, which have to be enabled manually
        """

        def decorator(f):
            @wraps(f)
            def func(*args, **kwargs):
                request.opt_cache_timeout = timeout
                return f(*args, **kwargs)

            return func

        return decorator

    @staticmethod
    def do_not_minify():
        """
        Decorator to skip the minify for the method.
        """

        def decorator(f):
            @wraps(f)
            def func(*args, **kwargs):
                request.opt_do_not_minify = True
                return f(*args, **kwargs)

            return func

        return decorator

    @staticmethod
    def do_not_compress():
        """
        Decorator to skip the compress for the method.
        """

        def decorator(f):
            @wraps(f)
            def func(*args, **kwargs):
                request.opt_do_not_compress = True
                return f(*args, **kwargs)

            return func

        return decorator

    def clear_timestamps(self):
        tmp_dic = {}

        # FIXME: parallize me
        for k, v in self._timestamp.items():
            if v < time.time():
                tmp_dic[k] = v

        # del self._timestamp # trigger gc for previous dict
        self._timestamp = tmp_dic
        return

    def optimize_response(self, response):
        """
        Optimize the given response with minify html, set crossdomain for json, compress everything or optional caching the response.
        """
        resp = response

        #self.clear_timestamps()
        period_cache = request.opt_cache_timeout if hasattr(request, "opt_cache_timeout") and isinstance(request.opt_cache_timeout, int) else 0

        # init cached data
        now = time.time()
        key_cache = request.method + request.url

        # if cache entry found, return it.
        if period_cache > 0 and self._timestamp.get(key_cache) and self._timestamp.get(key_cache) > now:
            logger.debug("Optimizer: Response from cache. Valid for {}s.".format(int(self._timestamp.get(key_cache) - now)))
            return self._cache[key_cache]

        #resp = func(*args, **kwargs)

        # FIXME: remove this, because we use flask-cors
        # crossdomain
        #if resp.mimetype.endswith('json'):
        #    logger.debug("Optimizer: JSON found. Crossdomain added.")
        #    resp = self.crossdomain(resp)

        # minify html, if its not suppressed
        if (self.config["minify"] and not hasattr(request, "opt_do_not_minify")) and resp.mimetype.endswith("html"):
            logger.debug("Optimizer: minify HTML response.")
            resp = self.validate(self.minifier, resp)

        # compress, if its not suppressed
        if (self.config["compress"] and not hasattr(request, "opt_do_not_compress")):
            logger.debug("Optimizer: compress response.")
            resp = self.validate(self.compress, resp)

        # period_cache is bigger then 0, if request.opt_cache_timeout was set.
        if period_cache > 0:
            logger.debug("Optimizer: response cached.")
            self._cache[key_cache] = resp
            self._timestamp[key_cache] = now + period_cache

        return resp

    @staticmethod
    def validate(method, content):
        instances_compare = (str, Response) if IS_PYTHON_3 else (
            str, unicode, Response)
        if isinstance(content, instances_compare):
            return method(content)
        elif isinstance(content, tuple):
            if len(content) < 2:
                raise TypeError('Content must have larger than 2 elements')

            return method(content[0]), content[1]

        return content

    @staticmethod
    def minifier(content):
        if not IS_PYTHON_3 and isinstance(content, str):
            content = unicode(content, 'utf-8')

        resp = minify(content,
                      remove_comments=True,
                      reduce_empty_attributes=True,
                      remove_optional_attribute_quotes=False)

        logger.debug("Response minifier: {}".format(resp.get_data()))
        return resp

    @staticmethod
    def compress(content):
        """
        Compress str, unicode content using gzip
        """
        resp = Response()
        if isinstance(content, Response):
            resp = content
            content = resp.get_data()
            #logger.debug("Response compress: {}".format(resp))

        if not IS_PYTHON_3 and isinstance(content, unicode):
            content = content.encode('utf8')

        if IS_PYTHON_3:
            gzip_buffer = BytesIO()
            gzip_file = gzip.GzipFile(fileobj=gzip_buffer, mode='wb')
            #gzip_file.write(bytes(content, 'utf-8'))
            gzip_file.write(content)
        else:
            gzip_buffer = StringIO()
            gzip_file = gzip.GzipFile(fileobj=gzip_buffer, mode='wb')
            gzip_file.write(content)

        gzip_file.close()

        resp.headers['Content-Encoding'] = 'gzip'
        resp.headers['Vary'] = 'Accept-Encoding'
        resp.set_data(gzip_buffer.getvalue())

        logger.debug("Response compress: {}".format(resp.get_data()))

        return resp

    @staticmethod
    def crossdomain(content):
        """
        Create decorator Cross-site HTTP requests
        see more at: http://flask.pocoo.org/snippets/56/
        """
        if isinstance(content, (dict, Response)):
            if isinstance(content, dict):
                content = json.jsonify(content)
                resp = make_response(content)
            elif isinstance(content, Response):
                resp = content

            h = resp.headers
            h['Access-Control-Allow-Origin'] = '*'
            h['Access-Control-Allow-Methods'] = current_app.make_default_options_response().headers['allow']
            h['Access-Control-Max-Age'] = '21600'

            logger.debug("Response crossdomain: {}".format(resp.get_data()))

            return resp

        return content

