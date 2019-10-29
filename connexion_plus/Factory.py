import logging
from .Util import set_tracer
logger = logging.getLogger('')


class Factory():
    def __init__(self, app, tracer=None, metrics=False):
        self.app = app
        self.api = app.api_cls

        if tracer is not None:
            set_tracer(tracer)
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


