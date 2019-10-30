name = "connexion-plus"

import logging
from flask import Flask

from connexion import FlaskApp

class App(FlaskApp):
    def __init__(self, name, use_tracer=None, use_metric=False, use_logging_level=logging.DEBUG):
        super().__init__(name)
        logger = logging.getLogger("")

        self.metrics = None
        self.tracing = None

        if not isinstance(self.app, Flask):
            logger.warning("Given App is not flask, so it cannot get any functionality added from this lib currently.")
            return

        # add prometheus
        if use_metric:
            from prometheus_flask_exporter import PrometheusMetrics
            self.metrics = PrometheusMetrics(self.app)

        # add tracing
        if use_tracer is not None:
            # add tracing to all routes in flaskApp
            from flask_opentracing import FlaskTracing
            self.tracing = FlaskTracing(use_tracer, True, self.app)
            
            # add tracer to everything to support spans through multiple microservices via rpc-calls
            from opentracing_instrumentation.client_hooks import install_all_patches
            install_all_patches()

            # add a TracingHandler for Logging
            from .TracingHandler import TracingHandler

            th = TracingHandler(use_tracer)
            th.setLevel(use_logging_level)

            logging.getLogger('').addHandler(th)

