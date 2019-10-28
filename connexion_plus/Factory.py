import logging

logger = logging.getLogger('')


class Factory():
    def __init__(self, app, api, tracer=None, metrics=False):
        self.app = app
        self.api = api

        if tracer is not None:
            logger.debug("add tracer")
            self.addTracer(tracer)

        if metrics:
            logger.debug("add prometheus")
            self.addPrometheus()
    
    def addTracer(self, tracer):
        try:
            from .TracerDecorator import TracerDecorator
            self.api.get_response = TracerDecorator(self.api.get_response, tracer)
            logger.debug("Add Tracing for flask")
        except ImportError as e:
            print(e)
            logger.debug("TracerDecorator not found")


    def addPrometheus(self):
        try:
            from prometheus_flask_exporter import PrometheusMetrics
            logger.debug("Add PrometheusMetrics for flask")
            return PrometheusMetrics(self.app.app)
        except ImportError as e:
            logger.debug("PrometheusMetrics not found")


