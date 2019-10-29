name = "connexion-plus"

import logging

def addServices(app, use_tracer=None, use_metric=False, use_logging_level=logging.DEBUG):
    metrics = None
    tracing = None

    # add prometheus
    if use_metric:
        from prometheus_flask_exporter import PrometheusMetrics
        metrics = PrometheusMetrics(app.app)

    # add tracing
    if use_tracer is not None:
        # add tracing to all routes in flaskApp
        from flask_opentracing import FlaskTracing
        tracing = FlaskTracing(use_tracer, True, app.app)
        
        # add tracer to everything to support spans through multiple microservices via rpc-calls
        from opentracing_instrumentation.client_hooks import install_all_patches
        install_all_patches()

        # add a TracingHandler for Logging
        from .TracingHandler import TracingHandler

        th = TracingHandler(use_tracer)
        th.setLevel(use_logging_level)

        logging.getLogger('').addHandler(th)

    return tracing, metrics
