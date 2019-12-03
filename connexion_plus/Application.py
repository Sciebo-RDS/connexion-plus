import logging
from flask import Flask, jsonify

from connexion import FlaskApp


class App(FlaskApp):
    def __init__(self, name, use_tracer=None, use_metric=False, use_logging_level=logging.DEBUG, use_optimizer=None, use_cors=None, use_default_error=None, all=False, *args, **kwargs):
        """
        Initialize Flask App with multiple microservice and easier usability features.
        """
        super().__init__(name, *args, **kwargs)
        logger = logging.getLogger("")

        self.metrics = None
        self.tracing = None
        self.optimize = None
        self.cors = None
        self.default_errorhandler = None

        if all is True:
            use_tracer = True
            use_metric = True
            use_optimizer = True
            use_cors = True
            use_default_error = True

        logger.info("--- Start Connexion-Plus ---")

        if not isinstance(self.app, (Flask, FlaskApp)):
            logger.warning(
                "Given App is not flask, so it cannot get any functionality added from this lib currently.")
            return

        # add default error
        if use_default_error is not None and use_default_error:
            from werkzeug.exceptions import HTTPException

            @self.app.errorhandler(Exception)
            def handle_error(e):
                code = 500
                if isinstance(e, HTTPException):
                    code = e.code

                error = {
                    "error": e.__class__.__name__,
                    "http_code": code,
                    "message": str(e),
                }
                return jsonify(error), code
            self.default_errorhandler = handle_error

        # add optimizer
        if use_optimizer is not None and use_optimizer is not False:
            from .Optimizer import FlaskOptimize

            config = {"compress": True, "minify": True}
            if isinstance(use_optimizer, dict):
                config = use_optimizer

            self.optimize = FlaskOptimize(self.app, config)
            logger.info("Optimizer added.")

        # add CORS
        if use_cors is not None and use_cors is not False:
            from flask_cors import CORS

            if isinstance(use_cors, dict):
                self.cors = CORS(self.app, resources=use_cors)
            else:
                self.cors = CORS(self.app)

            logger.info("CORS added.")

        # add prometheus
        if use_metric is not None and use_metric is not False:
            # TODO: add configuration https://github.com/rycus86/prometheus_flask_exporter#configuration

            from prometheus_flask_exporter import PrometheusMetrics
            self.metrics = PrometheusMetrics(self.app)
            logger.info("Prometheus added.")

        # add tracing
        if use_tracer is not None and use_tracer is not False:
            # add tracing to all routes in flaskApp
            from flask_opentracing import FlaskTracing
            import opentracing

            config = None
            if not isinstance(use_tracer, opentracing.Tracer):
                logger.info("Tracer should be used, but no object was given.")
                from jaeger_client import Config as jConfig

                if isinstance(use_metric, bool) and use_metric is True:
                    logger.info("Use metrics for tracer.")
                    from jaeger_client.metrics.prometheus import PrometheusMetricsFactory
                    config = jConfig(
                        config={},
                        service_name="MicroserviceConnexionPlus",
                        metrics_factory=PrometheusMetricsFactory(
                            namespace="MicroserviceConnexionPlus")
                    )
                else:
                    config = jConfig(
                        config={},
                        service_name="MicroserviceConnexionPlus",
                    )
            else:
                logger.info("Tracer given and will be used.")

            tracer_obj = use_tracer if config is None else config.initialize_tracer()
            self.tracing = FlaskTracing(tracer_obj, True, self.app)

            # add tracer to everything to support spans through multiple microservices via rpc-calls
            from opentracing_instrumentation.client_hooks import install_all_patches
            install_all_patches()
            logger.info("All tracing relevant libs patched.")

            # add a TracingHandler for Logging
            from .TracingHandler import TracingHandler

            th = TracingHandler(use_tracer)
            th.setLevel(use_logging_level)

            logging.getLogger('').addHandler(th)
            logger.info("Tracer added.")

        logger.info("--- Finished Connexion-Plus ---")
