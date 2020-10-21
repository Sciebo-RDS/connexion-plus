import logging
from flask import Flask, jsonify

from connexion import FlaskApp


class App(FlaskApp):
    def __init__(
        self,
        name,
        use_tracer=None,
        use_metric=False,
        use_logging_level=logging.DEBUG,
        use_optimizer=None,
        use_cors=None,
        use_default_error=None,
        use_scheduler=None,
        all=None,
        *args,
        **kwargs,
    ):
        # TODO: Add more text here for current situation
        """
        Initialize Flask App with multiple microservice-related and usability features.

        None is for deactivating, so it equals to False.

        *use_tracer* must be of type: bool (True for defaults, False for deactivating), 
        opentracing.Tracer (use it for configuration), dict (use default opentracing.Tracer and the given dict as config) or defaults: None

        *use_metric* must be of type: bool (True for defaults, False for deactivating) or defaults: None

        *use_logging_level* must be of type: logging.{INFO, WARNING, ERROR, DEBUG}, defaults: DEBUG
        *use_optimizer* must be of type: bool (True for defaults, False for deactivating) or defaults: None
        *use_cors* must be of type: bool (True for defaults, False for deactivating) or defaults: None
        *use_default_error* must be of type: bool (True for defaults, False for deactivating) or defaults: None
        *use_scheduler* must be of type: bool (True for defaults, False for deactivating) or defaults: None
        *all* must be of type: bool (True for use all functions with defaults, False for deactivating all functions) or defaults: None
        """
        super().__init__(name, *args, **kwargs)
        logger = logging.getLogger("")

        self.metrics = None
        self.tracing = None
        self.optimize = None
        self.cors = None
        self.default_errorhandler = None
        self.scheduler = None

        if all is not None and all is not False:
            use_tracer = True
            use_metric = True
            use_optimizer = True
            use_cors = True
            use_default_error = True
            use_scheduler = True

        logger.info("--- Start Connexion-Plus ---")

        if not isinstance(self.app, (Flask, FlaskApp)):
            logger.warning(
                "Given App is not flask, so it cannot get any functionality added from this lib currently."
            )
            return

        # add default error
        if use_default_error is not None and use_default_error is not False:
            from werkzeug.exceptions import HTTPException
            from werkzeug.exceptions import default_exceptions

            logger.info("Add default error handler to Flask...")

            if callable(use_default_error):
                self.default_errorhandler = use_default_error

                logger.info("use given handler.")

            else:

                def handle_error(e):
                    code = 500
                    if isinstance(e, HTTPException):
                        code = e.code

                    error = {
                        "error": e.__class__.__name__,
                        "http_code": code,
                        "description": str(e),
                    }
                    logger.exception(error)
                    return jsonify(error), code

                self.default_errorhandler = handle_error

                logger.info("use default one")

            # register for all json exceptions
            self.app.register_error_handler(Exception, self.default_errorhandler)

            # register handler for all http exceptions
            for ex in default_exceptions:
                self.app.register_error_handler(ex, self.default_errorhandler)

        if use_scheduler is not None and use_scheduler is not False:
            logger.info("Add background scheduler to Flask")
            from flask_apscheduler import APScheduler

            self.scheduler = APScheduler()
            self.scheduler.init_app(self.app)
            self.scheduler.start()

        # add optimizer
        if use_optimizer is not None and use_optimizer is not False:
            logger.info("Add optimizer to Flask...")
            from .Optimizer import FlaskOptimize

            config = {"compress": False, "minify": False}
            if isinstance(use_optimizer, dict):
                config.update(use_optimizer)

            if isinstance(use_optimizer, bool) and use_optimizer:
                config.update({"compress": True, "minify": True})

            logger.info("use config {}.".format(config))

            self.optimize = FlaskOptimize(self.app, config)

        # add CORS
        if use_cors is not None and use_cors is not False:
            logger.info("Add cors to Flask...")
            from flask_cors import CORS

            if isinstance(use_cors, dict):
                logger.info("use given settings.")
                self.cors = CORS(self.app, resources=use_cors)
            else:
                logger.info("use default ones.")
                self.cors = CORS(self.app)

            logger.info("CORS added.")

        # add prometheus
        if use_metric is not None and use_metric is not False:
            # TODO: add configuration https://github.com/rycus86/prometheus_flask_exporter#configuration

            from prometheus_flask_exporter import PrometheusMetrics

            self.metrics = PrometheusMetrics(self.app)
            logger.info("Add prometheus to Flask")

        # add tracing
        if use_tracer is not None and use_tracer is not False:
            logger.info("Add opentracing to Flask...")
            # add tracing to all routes in flaskApp
            from flask_opentracing import FlaskTracing
            import opentracing
            from functools import wraps
            from flask import request

            def wrapper(fn):
                @wraps(fn)
                def request_func(*args, **kwargs):
                    if request.path != "/metrics":
                        return fn(*args, **kwargs)

            FlaskTracing._before_request_fn = wrapper(FlaskTracing._before_request_fn)
            FlaskTracing._after_request_fn = wrapper(FlaskTracing._after_request_fn)

            config = None
            if not isinstance(use_tracer, opentracing.Tracer):
                logger.info("use default one.")
                from jaeger_client import Config as jConfig

                tracer_config = {
                    "sampler": {"type": "const", "param": 1,},
                    "local_agent": {
                        "reporting_host": "jaeger-agent",
                        "reporting_port": 5775,
                    },
                    "logging": True,
                }

                if isinstance(use_tracer, dict):
                    tracer_config = use_tracer

                if isinstance(use_metric, bool) and use_metric is True:
                    logger.info("Use metrics for tracer.")
                    from jaeger_client.metrics.prometheus import (
                        PrometheusMetricsFactory,
                    )

                    config = jConfig(
                        config=tracer_config,
                        service_name=f"{name}ConnexionPlus",
                        metrics_factory=PrometheusMetricsFactory(
                            namespace=f"{name}ConnexionPlus"
                        ),
                    )
                else:
                    logger.info("no metrics for tracer configured.")
                    config = jConfig(
                        config=tracer_config, service_name=f"{name}ConnexionPlus",
                    )
            else:
                logger.info("use given tracer config.")

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

            logging.getLogger("").addHandler(th)
            logger.info("Finished Tracer adding.")

        logger.info("--- Finished Connexion-Plus ---")
